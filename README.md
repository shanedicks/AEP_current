# greenbean

**greenbean** is a full-stack student information and program management system built for the Delgado Community College Adult Education Program (DCCAEP). It replaced a fragmented collection of Google Sheets with an integrated, enterprise-grade platform that tracks every stage of the student lifecycle — from initial inquiry through enrollment, attendance, assessment, coaching, and state compliance reporting — and serves approximately 3,000–5,000 students and 50+ staff annually at 99% uptime.

The system was designed, built, and maintained by a single developer who previously served as the program's tutor, instructor, and Program Coordinator. That institutional knowledge shaped the architecture directly: the data model reflects the real operational logic of adult education administration, not abstract technical patterns.

---

## Table of Contents

- [Background](#background)
- [Architecture Overview](#architecture-overview)
- [Application Structure](#application-structure)
  - [people](#people)
  - [sections](#sections)
  - [semesters](#semesters)
  - [assessments](#assessments)
  - [coaching](#coaching)
  - [academics](#academics)
  - [inventory](#inventory)
- [Async Task System](#async-task-system)
- [Google Classroom Integration](#google-classroom-integration)
- [Communication Systems](#communication-systems)
- [State Compliance Reporting](#state-compliance-reporting)
- [Student Lifecycle](#student-lifecycle)
- [Multilingual Support](#multilingual-support)
- [Deployment](#deployment)
- [Configuration](#configuration)

---

## Background

Before greenbean, DCCAEP managed student data across a loosely organized collection of Google Sheets — new sheets created each semester, no relational integrity, no automation, and significant staff time consumed by manual data entry and error correction. There was no way to get a real-time view of who was enrolled in what, whether attendance was current, or how students were progressing toward their goals.

The system replaced that entirely. greenbean tracks the full student journey:

**intake → orientation → placement testing → enrollment → instruction → attendance → post-assessment → coaching → state reporting**

Each stage is integrated. When a student's enrollment status changes, attendance records are generated automatically. When attendance crosses a threshold, drop procedures trigger and waitlisted students are notified. When a test is recorded, the student's placement assignment updates and compliance flags are recalculated. Staff can see any student's complete record in one place rather than hunting across multiple sheets.

---

## Architecture Overview

greenbean is a Django application with a PostgreSQL database, deployed on Heroku with a multi-environment settings structure (base / development / testing / production). Long-running operations are offloaded to Celery task queues backed by CloudAMQP (broker) and Redis (result backend). Static files are served through WhiteNoise. All external service credentials are managed through environment variables.

**Core stack:**
- Django (Python) — web framework and ORM
- PostgreSQL — primary relational database
- Celery + CloudAMQP + Redis — asynchronous task processing
- Heroku — cloud deployment platform
- WhiteNoise — static file serving
- Google Classroom API (via `google-api-python-client`, OAuth2 service account) — LMS integration
- Plivo — SMS notifications
- Anymail / Mailgun — transactional email
- `django-import-export` — CSV/XLSX import and export through the admin interface
- `django-rules` — object-level permission backend
- `crispy-forms` — Bootstrap 3 form rendering
- `formtools` — multi-step form wizard for student intake

The project is organized as a standard Django project under `aep/` with a `config/` settings package and seven domain-specific applications.

---

## Application Structure

### people

The `people` app is the foundation of the system. It defines the core data model for everyone who interacts with the program and manages the intake pipeline.

**Key models:**

`Profile` (abstract base) defines shared fields used by both `Student` and `Staff`: name, contact information, address, date of birth, emergency contact, pronouns, and title.

`Student` extends `Profile` with adult education-specific fields: state WRU ID (`WRU_ID`), intake date, partner organization, parish, WIOA eligibility data, primary program goals (nine distinct goal checkboxes), scheduling preferences (morning/afternoon/evening/weekend, Monday-Wednesday/Tuesday-Thursday/Saturday), modality preferences (on-campus/online/hybrid), technology access flags, and orientation, paperwork, and eligibility tracking. The model includes a `StudentQuerySet` with custom queryset methods for filtering students active within a date range, identifying minor students by age, and identifying students living in poverty using federal poverty level thresholds.

`Staff` extends `Profile` with employment-related fields and links to a Django `User` account for authentication.

`Prospect` is used to manage leads before a student record is created — people who have expressed interest but have not yet completed intake. The `ProspectNote` model allows staff to track contact history.

`WIOA` stores Workforce Innovation and Opportunity Act data (household size, income, employment status, barriers to employment) collected during intake for federal compliance.

`CollegeInterest` tracks students' interest in post-secondary pathways.

`Paperwork` tracks whether each student has completed required documentation: FERPA consent, testing agreement, technology policy, student contract, special disability disclosures (reading, math, language, attention), and special help requests. It also tracks photo ID and eligibility document uploads.

**Intake pipeline:** New students can enter the system through a multi-step wizard (`StudentSignupWizard` via `formtools`) or a newer `ProspectSignupView` that creates a `Prospect` first. The system supports a separate minor student pathway. After intake, a `Prospect` can be linked to a newly created `Student` record. The `people` app also includes a full online orientation system — a multi-page guided orientation with separate English and Spanish versions, covering program overview, class types (CCR and ELL), class structure (online vs. in-person), testing, coaching, and paperwork.

**Duplicate management:** The system includes tooling for identifying and merging duplicate student records, with careful handling of related objects (test history, class enrollments, coaching records, eLearn records, appointments) during the merge process.

**Reporting:** The app produces CSV exports for active students, minor students, prospect lists, intercession reports, and eligibility verification. An `update_eligibility_task` Celery task handles bulk eligibility updates from uploaded CSV files, with error reporting for unmatched WRU IDs and a duplicate-following chain for merged records.

---

### sections

The `sections` app manages the instructional side of the program: the physical locations where classes are held, the class sections themselves, and everything that happens within them — enrollment, attendance, and communication.

**Key models:**

`Site` represents a physical campus location with a two-letter code used throughout the system.

`Section` is the central instructional unit. It links a `Course` (from `academics`), a `Semester` or custom date range, a `Site`, a teacher (`Staff`), and a `g_suite_id` that connects the section to its corresponding Google Classroom course. Sections have day-of-week boolean fields (`monday` through `sunday`), start/end times, seat capacity, program type (ELL, CCR, Transitions, eLearn, Admin), a `WRU_ID` for state reporting, and flags for different attendance tracking modes. The model includes methods for computing scheduled class dates across a semester, calculating daily attendance rates as a matrix, copying rosters to new sections, and managing waitlists.

`Enrollment` links a `Student` to a `Section` with a status field: Active, Waitlist, Withdrawn, Dropped, or Completed. The enrollment lifecycle is managed through methods like `activate()`, `attendance_drop()`, and `waitlist_drop()` that enforce business rules — for example, dropping a student from a section after two absences and automatically pulling the next waitlisted student in.

`Attendance` records each student's daily attendance within a given enrollment. Attendance can be tracked by time-in/time-out (calculated automatically to decimal hours) or by a direct hours field. Each record carries a `reported` flag used to track whether it has been submitted to the state. Saving a `Present` attendance record automatically triggers a `pop_update_task` to update the student's POPS compliance record.

`Message` supports broadcast SMS to all students enrolled in one or more sections, with the SMS dispatch handled through Celery.

`Cancellation` records class cancellations with an option to send SMS notifications to enrolled students.

**Attendance enforcement:** `waitlist_update()` and `enforce_attendance()` are section-level methods that apply attendance policies in bulk — dropping students who have exceeded absence limits and notifying teachers by email, then activating waiting students and syncing their Google Classroom enrollments.

**Import/export:** The admin interface supports CSV import and export for sites, sections, enrollments, and attendance records using `django-import-export`. Staff can also import attendance from EssentialEd and Duolingo integrations directly through the section attendance views.

---

### semesters

The `semesters` app manages program terms. A `Semester` defines a start date, end date, and allowed absence count for that term. Sections belong to a semester, which provides their date boundaries and attendance policy unless overridden at the section level. The admin interface exposes attendance reminder dispatch and section ending workflows.

---

### assessments

The `assessments` app manages all placement and progress testing: scheduling test events, tracking appointments, recording scores, and applying NRS (National Reporting System) level logic.

**Key models:**

`TestEvent` represents a scheduled testing session at a site — with a proctor, room, seat capacity, start/end time, and test type (TABE, CLAS-E, Orientation, etc.). The model can send orientation confirmation emails and test reminder emails to all registered students. It tracks seat capacity and prevents overbooking.

`TestAppointment` links a `Student` to a `TestEvent` with attendance status. Saving a present appointment automatically triggers `orientation_status_task` for orientation events and `pop_update_task` for all present appointments.

`TestHistory` is a one-to-one record per student that tracks their most recent test date, test type, and current test assignment (form + level combination for their next test). It provides properties for computing the student's active hours since last test, looking up NRS scores across test types, and summarizing their peak NRS levels.

`Tabe` stores TABE (Test of Adult Basic Education) scores including scale scores, grade equivalents, and NRS levels for reading, math, and language subtests. The model includes `get_level()` to convert scale scores to NRS levels using the official score table, `assign()` to determine the appropriate form and level for the next test, and `check_gain()` to determine whether a post-test represents a measurable educational gain over a pre-test. Multiple test forms are supported (TABE 11, 12, 13, 14).

`Tabe_Loc` stores TABE Locator scores used for initial placement before a full TABE.

`Clas_E` and `Clas_E_Loc` store CLAS-E (Comprehensive Learning Assessment for ESOL) scores for ELL students, with reading and writing subtests.

`Gain` stores GAIN (Global Assessment of Instructional Needs) scores.

`HiSet_Practice` tracks practice test performance for students preparing for the HiSET (high school equivalency exam).

`HiSET` and `Accuplacer` track scores from the actual HiSET exam and college placement testing respectively.

`TestingAccommodations` records formal testing accommodations granted to individual students.

**NRS level logic:** The TABE score model implements the NRS level assignment table directly in code. Scale scores are mapped to educational functioning levels (Below Basic through Advanced) with specific cutpoints for reading (501/536/576), math (496/537/596), and language (511/547/584). This logic drives test assignment, eligibility determination, and state reporting throughout the system.

**Compliance reporting:** The assessments app produces CSV exports formatted for state WRU submission — attendance records, enrollment records, event attendance, and test score reports — all structured to match the exact column format expected by the Louisiana state reporting system.

---

### coaching

The `coaching` app manages the individualized student support side of the program — academic coaching, eLearn program management, ACE/PACE scholarship tracking, and student profiles.

**Key models:**

`Profile` (coaching) is a rich student intake form for the eLearn program, capturing learning goals, technology access, contact preferences, availability, library access, social media handles, previous school experience, grade level completed, special help needs, program completion timeline, hours per week available, personal goals, and how the student prefers to receive support when stressed. This data informs coaching relationships and scheduling.

`Coaching` links a `Student` (coachee) to a `Staff` (coach) with a coaching type (eLearn, ACE, or Open Coaching), status, and date range. Saving an active coaching record automatically updates the student's elearn status.

`MeetingNote` records individual coaching sessions with contact type (email, phone, text, Google Hangouts, Facebook Messenger, in person), topic, next steps, duration, and outcome flags (no-show, rescheduled, cancelled, low grades, class absences, meeting absences, unable to reach, ACE withdrawal).

`ElearnRecord` is a one-to-one record per student tracking their eLearn program status, intake date, and Google Suite email address. The G Suite email is the key that connects the student to their Google Classroom account.

`AceRecord` and its companion paperwork models track participation in the ACE/PACE scholarship program, including 5-for-6 agreement acceptance, media release decisions, electronic signatures, career pathway selection, and HSD/HSE credential status.

**Reporting:** The coaching app produces CSV exports for eLearn students, enrollment snapshots, exit exam eligibility, and advanced student reports. The advanced student report uses complex ORM annotations to identify students who have achieved NRS level 3 or higher on two or more TABE subtests within the past two years and NRS level 4 or higher on at least one — a compound eligibility calculation for college bridge programs.

---

### academics

The `academics` app manages the curriculum layer — courses offered by the program and skill mastery tracking within those courses.

`Course` defines a class offering with a code and descriptive metadata. Sections belong to courses.

`SkillMastery` links a student enrollment to a specific skill with a mastery date, enabling per-student skill tracking within a course section. The sections app exposes views for reviewing and updating skill mastery for all students in a section.

---

### inventory

The `inventory` app manages physical equipment checked out to students and staff — tablets, hotspots, and other instructional technology.

`Category` groups items by type.

`Item` represents an individual physical asset with a serial number/identifier and optional state asset tag.

`Ticket` records a checkout transaction linking an item to a student or staff member, with issued date, return date, and optional return-required date.

Celery tasks generate CSV reports of active checkouts with attendance activity — for student checkouts, the report includes last attendance date, days since last attendance, and attendance count and hours over the past 30 days, providing a practical signal for follow-up on equipment that may be sitting unused.

---

## Async Task System

greenbean uses Celery with CloudAMQP as the message broker and Redis as the result backend. The task queue is essential because several operations exceed Heroku's 30-second web request timeout.

Tasks are used throughout the system for:

- **Google Classroom operations** — creating courses, syncing rosters, sending G Suite login information to students — all involve Google API calls that can take unpredictable amounts of time
- **State compliance report generation** — producing large CSV exports across tens of thousands of records
- **Bulk email and SMS dispatch** — sending class schedules, cancellation notices, attendance reminders, test reminders, score report links, and orientation confirmations to lists of students
- **Enrollment lifecycle transitions** — activating enrollments, processing drops, checking attendance thresholds, updating POPS records
- **Duplicate detection** — checking new students against existing records asynchronously
- **Eligibility updates** — processing bulk uploads from state systems
- **Inventory reporting** — generating equipment checkout reports cross-referenced with attendance data

The Celery app is initialized in `config/celery.py` and imported in `config/__init__.py` to ensure it loads with Django.

---

## Google Classroom Integration

Each section in greenbean can have a corresponding Google Classroom course, identified by a `g_suite_id`. The integration uses a service account (`admin-629@greenbean-176303.iam.gserviceaccount.com`) with domain-wide delegation, authorized through a JSON keyfile stored in settings as `KEYFILE_DICT`.

**Classroom operations:**

`roster_to_classroom()` syncs the Greenbean active enrollment roster to the Google Classroom course. It fetches the current Classroom roster, computes the diff against active Greenbean enrollments (using the student's G Suite email from their `ElearnRecord`), drops students who are no longer active, and adds students who are active but not yet rostered. Additions are batched in groups of 50 to stay within Google API batch limits.

`create_classroom_section_task` creates a new Classroom course for a section and saves the returned course ID back to the section's `g_suite_id`.

`send_g_suite_info_task` emails each active student their G Suite email address and login instructions in both English and Spanish.

`add_TA_task` adds a staff member as a teacher to existing Classroom courses.

`create_missing_g_suite_task` identifies active students in a section who don't yet have G Suite accounts and creates them.

`g_suite_attendance()` can import attendance data from student Classroom submissions — used for asynchronous eLearn attendance tracking.

The `ElearnRecord.g_suite_email` field is the primary key connecting a Greenbean student to their Google identity throughout all Classroom operations.

---

## Communication Systems

greenbean sends communications through three channels:

**Email** via Anymail/Mailgun for transactional messages: enrollment notifications, class schedules, G Suite login information (bilingual), attendance reminders to teachers, drop notifications, score report links, orientation confirmations, test reminders, and all async task result reports.

**SMS** via Plivo for time-sensitive operational messages: class cancellations, course welcome messages, and broadcast messages to enrolled students. The `Message` model in `sections` supports composing and dispatching SMS to all students across a set of sections. Message length is constrained to 160 characters for standard SMS compatibility. Students have an `allow_texts` flag and an eLearn `texts_ok` flag for consent management.

**HTML email** for orientation confirmations and test reminders uses Django template rendering with `render_to_string` and `strip_tags`, with bilingual content served inline.

All email and SMS dispatch goes through Celery tasks to keep web request times short and to allow retries on transient failures.

---

## State Compliance Reporting

Louisiana requires adult education programs to report attendance, enrollment, and assessment data to the state WRU (WorkReadyU) system. greenbean manages the full compliance pipeline.

**Outbound reporting:**

The `sections` app produces attendance CSV exports formatted to the exact WRU column specification (PROVIDERID, SID, student name fields, COURSE_ID, partner, and up to 48 HOURS/DATE/DL column groups per enrollment). The `MondoAttendanceReport` view produces a comprehensive enrollment-plus-attendance export combining section, teacher, coach, assessment, and attendance data in a single wide-format CSV used for internal reporting and state submission preparation.

`WruCourseRegistrationReport` exports enrollment data for state course registration submission. `WruSectionExport` exports section metadata.

`EventAttendanceCSV` exports testing event attendance in the same WRU format, allowing orientation and testing hours to be reported alongside class attendance.

**Inbound reconciliation:**

`ImportReportedEnrollmentsView` and the corresponding `mark_attendance_reported_task` allow staff to upload a CSV of WRU IDs and dates that the state has confirmed as received, and mark those attendance records as `reported=True` in greenbean. The import task handles mismatched WRU IDs, missing sections, duplicate students, and unmatched attendance dates, generating a detailed error report for manual follow-up.

**Assessment reporting:**

TABE and CLAS-E score records carry a `reported` flag. Score export views generate filtered CSVs that can be filtered by semester and date range.

**Eligibility verification:**

`update_eligibility_task` processes bulk uploads of WRU IDs from state eligibility confirmations, following duplicate chains as needed and generating reports for unmatched records.

---

## Student Lifecycle

The full student lifecycle in greenbean proceeds through these stages, each tracked with explicit status fields and automated transitions:

1. **Prospect** — Student expresses interest via the public signup form. A `Prospect` record is created with contact information, language, and program interest.
2. **Orientation** — Student attends an orientation `TestEvent`. Attendance at orientation triggers `orientation_status_task`, which updates the student's orientation status and may trigger scheduling workflows.
3. **Intake/Paperwork** — Student completes intake forms. A `Student` record is created (or linked from the Prospect). `Paperwork` tracking begins. Required documents (FERPA, testing agreement, technology policy, student contract) are tracked with boolean flags. Photo ID and eligibility documents can be uploaded through the web interface and stored in Google Drive.
4. **Placement Testing** — Student takes a TABE Locator followed by a TABE or CLAS-E. Scores are recorded in the `assessments` app. The `TestHistory` record updates with the new test date and level assignment for the next test.
5. **Enrollment** — Student is enrolled in one or more `Section` objects. Enrollment can be Active or Waitlist. The system enforces seat capacity and waitlist overflow limits.
6. **Instruction** — Sections run across a semester. Daily `Attendance` records are created (Present, Absent, Pending, Cancelled). Teachers update attendance through the web interface. Celery tasks handle attendance reminders, waitlist updates, and class cancellation notifications.
7. **Attendance Enforcement** — The `enforce_attendance()` workflow drops students who have exceeded the semester's allowed absences and notifies teachers. The `waitlist_update()` workflow promotes waitlisted students when active students are dropped.
8. **Post-Assessment** — Students take a post-test after accumulating hours. Score gains are tracked using `check_gain()`. The `active_hours` property on `TestHistory` computes hours since last test.
9. **Completion or Drop** — At semester end, the `end_task` Celery task evaluates each enrollment: students with excessive absences are dropped, others are marked Completed.
10. **Coaching** — Students in eLearn and ACE programs are assigned coaches. `Coaching` records and `MeetingNote` logs track support over time.
11. **State Reporting** — Attendance, enrollment, and assessment data are exported in state-required formats and marked as reported after confirmation.

---

## Multilingual Support

greenbean is used by students who speak a wide range of languages. The orientation system provides a full bilingual experience in English and Spanish, with separate URL namespaces (`en/` and `es/`) and complete template coverage for both languages across all orientation sections (overview, class types, CCR, ELL, class structure, online vs. in-person, testing, coaching, and paperwork).

Email communications to students are sent in both English and Spanish inline — the G Suite login email, for example, contains the full message in English followed by the full message in Spanish in a single communication, to ensure comprehension regardless of primary language.

Student records track primary language through the `Prospect` model. Intake forms and orientation materials are designed to support students with limited English, and the program serves populations whose primary languages include Spanish, Arabic, Russian, French, Vietnamese, Creole, Chinese, Korean, Japanese, Portuguese, Turkish, and Urdu.

---

## Deployment

greenbean is deployed on Heroku using `dj-database-url` for database URL parsing and a `Procfile`-based process configuration. The production settings enable SSL redirect, secure session and CSRF cookies, and serve static files through WhiteNoise's compressed manifest storage.

**Environment separation:**
- `config/settings/base.py` — shared settings
- `config/settings/development.py` — local development with verbose logging
- `config/settings/testing.py` — test environment
- `config/settings/production.py` — Heroku production with CloudAMQP, Redis, and security settings

**Proxy configuration:** Outbound requests to the Louisiana state WRU system use a fixed egress IP via Fixie proxy, which is required for IP whitelisting by the state system. The proxy is configured in `PROXIE_DICT` and applied to the relevant requests.

---

## Configuration

All secrets and service credentials are loaded from environment variables via a `get_env_variable()` utility. Required environment variables include:

| Variable | Purpose |
|---|---|
| `GOOGLE_API_KEY_ID` | Google service account key ID |
| `GOOGLE_API_KEY` | Google service account private key |
| `CLOUDAMQP_URL` | Celery broker URL (production) |
| `REDIS_URL` | Celery result backend (production) |
| `DATABASE_NAME` / `USER` / `PASSWORD` | Database credentials (development) |
| `LCTCS_PASS` | Louisiana state WRU system password |
| `FIXIE_URL` | Fixed egress proxy URL |
| `PLIVO_AUTH_ID` / `PLIVO_AUTH_TOKEN` | SMS service credentials |
| `MAILGUN_*` | Transactional email credentials (via Anymail) |
