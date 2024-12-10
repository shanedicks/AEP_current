from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.translation import gettext_lazy as _
from core.tasks import send_mail_task
from core.utils import clean_special_characters
from people.models import Staff, Student



class Profile(models.Model):

    NA = 'NA'
    APPLICANT = 'Applicant'
    ACTIVE = 'Active'
    INACTIVE = 'InActive'
    COMPLETED = 'Completed'
    STATUS_CHOICES = (
        (NA, 'NA'),
        (APPLICANT, 'Applicant'),
        (ACTIVE, 'Active'),
        (INACTIVE, 'InActive'),
        (COMPLETED, 'Completed')
    )

    CALL = 'Call'
    TEXT = 'Text'
    EMAIL = 'Email'
    SOCIAL_MEDIA = 'Social Media'
    GOOGLE_CHAT = 'Google Chat'
    CONTACT_CHOICES = (
        (CALL, 'Call'),
        (TEXT, 'Text'),
        (EMAIL, 'Email'),
        (SOCIAL_MEDIA, 'Social Media'),
        (GOOGLE_CHAT, 'Google Chat'),
    )

    MORNING = 'Morning'
    AFTERNOON = 'Afternoon'
    EVENING = 'Evening'
    AVAILABILITY_CHOICES = (
        (MORNING, 'Morning (8am - 12am)'),
        (AFTERNOON, 'Afternoon (12am - 4pm)'),
        (EVENING, 'Early Evening (4pm - 8pm)'),
    )

    CARD = 'Yes Close and Card'
    CLOSE = 'Yes Close'
    FAR = 'No not Near'
    HOURS = 'No Access Hours'
    UNSURE = 'Unsure'
    LIBRARY_CHOICES = (
        (CARD, 'Yes, I live close and I have a card'),
        (CLOSE, 'Yes, I live close'),
        (FAR, "No, I don't live near a library"),
        (HOURS, "No, I don't have access "
            "to a library during the hours they are open."),
        (UNSURE, "I'm not sure if I live near a library."),
    )

    SIXTH = '6'
    SEVENTH = '7'
    EIGHTH = '8'
    NINTH = '9'
    TENTH = '10'
    ELEVENTH = '11'
    OTHER = 'O'
    GRADE_LEVEL_CHOICES = (
        (SIXTH, '6th Grade or Lower'),
        (SEVENTH, '7th Grade'),
        (EIGHTH, '8th Grade'),
        (NINTH, '9th Grade'),
        (TENTH, '10th Grade'),
        (ELEVENTH, '11th Grade'),
        (OTHER, 'Other'),
    )

    NOT = 'Not'
    SOME = 'Some'
    VERY = 'Very'
    CONFIDENCE_CHOICES = (
        (NOT, 'Not at all Confident'),
        (SOME, 'Somewhat Confident'),
        (VERY, 'Very Confident')
    )

    student = models.OneToOneField(
        Student,
        models.CASCADE,
        related_name='coaching_profile'
    )

    ace_status = models.CharField(
        default='NA',
        choices=STATUS_CHOICES,
        max_length=10
    )

    elearn_status = models.CharField(
        default='NA',
        choices=STATUS_CHOICES,
        max_length=10
    )

    health_pathway_interest = models.BooleanField(
        default=False,
        verbose_name='Healthcare'
    )

    crafts_pathway_interest = models.BooleanField(
        default=False,
        verbose_name='Skilled Crafts'
    )

    it_pathway_interest = models.BooleanField(
        default=False,
        verbose_name='IT'
    )

    hospitality_pathway_interest = models.BooleanField(
        default=False,
        verbose_name='Culinary Arts / Hostpitaliy'
    )

    texts_ok = models.BooleanField(
        default=False,
        verbose_name='Text Messages',
        help_text='Are you okay with elearn sending you text messages?'
    )

    smartphone = models.BooleanField(
        default=False,
        help_text='Do you have a smartphone?'
    )

    webcam = models.BooleanField(
        default=False,
        help_text='Do you have a webcam with a microphone at home?'
    )

    device = models.CharField(
        verbose_name='What device will you be using for online learning?'
                  '(e.g Phone, Tablet, Computer, etc.)',
        max_length=50
    )

    contact_preference = models.CharField(
        choices=CONTACT_CHOICES,
        verbose_name='How do you prefer to be contacted?',
        max_length=12
    )

    other_contact = models.CharField(
        max_length=40,
        blank=True
    )

    availability = models.CharField(
        max_length=11,
        choices=AVAILABILITY_CHOICES,
        verbose_name='What is your typical availability?',
        blank=True
    )

    other_availability = models.CharField(
        max_length=40,
        blank=True,
    )

    library = models.CharField(
        choices=LIBRARY_CHOICES,
        max_length=20,
        verbose_name='Do you have access to a local library?'
    )

    instagram = models.CharField(
        max_length=40,
        blank=True,
        verbose_name='Optional: Instagram Handle'
    )

    twitter = models.CharField(
        max_length=40,
        blank=True,
        verbose_name='Optional: Twitter Handle'
    )

    facebook = models.CharField(
        max_length=40,
        blank=True,
        verbose_name='Optional: Facebook Handle'
    )

    linkedin = models.CharField(
        max_length=40,
        blank=True,
        verbose_name='Optional: LinkedIn Handle'
    )

    grade_level = models.CharField(
        max_length=2,
        choices=GRADE_LEVEL_CHOICES,
        verbose_name='What was the last grade level you completed?'
    )

    school_experience = models.TextField(
        help_text='A good start is to tell us your '
                  'last school attended and a little '
                  'bit of your story about what brought '
                  'you to our program! This helps us to '
                  'get to know and support you in our school!',
        verbose_name='Tell us about your last school experience'
    )

    special_help = models.CharField(
        max_length=1,
        choices=(
            ('Y', 'Yes'),
            ('N', 'No')
        ),
        default='N',
        verbose_name='Did you ever receive any special help'
                     ' in school OR do you believe you should have? ',
        help_text='Examples of special help: special education '
                  'services/accommodations, after school or '
                  'in-school tutoring, counseling services, etc.'
    )

    special_help_desc = models.TextField(
        verbose_name='If you answered yes to the above question'
                     ', describe below what sort of help you '
                     'received OR why you believe you should have',
        blank=True
    )

    conditions = models.TextField(
        verbose_name='(OPTIONAL) Do you have any medical conditions '
                     'you wish to disclose that might impact your academics?',
        blank=True
    )

    elearn_experience = models.CharField(
        max_length=140,
        verbose_name='What experience do you have with online learning? '
                     '(if none, simply put "none" or "NA")'
    )

    math = models.CharField(
        max_length=4,
        choices=CONFIDENCE_CHOICES
    )

    english = models.CharField(
        max_length=4,
        choices=CONFIDENCE_CHOICES
    )

    social_studies = models.CharField(
        max_length=4,
        choices=CONFIDENCE_CHOICES
    )

    science = models.CharField(
        max_length=4,
        choices=CONFIDENCE_CHOICES
    )

    best_classes = models.TextField(
        verbose_name='What classes were you best at?'
    )

    worst_classes = models.TextField(
        verbose_name='What classes did you struggle with the most?'
    )

    favorite_subject = models.TextField(
        verbose_name='What was your favorite subject and '
                     'why was it your favorite subject?',
        help_text='For example:  "Social Studies was my favorite subject, '
                  'because we often got to debate and discuss what '
                  'was going on in the world."'
    )

    completion_time = models.CharField(
        max_length=140,
        verbose_name='How quickly do you want to complete the program? (e.g. '
                     'within one month, within a few months, by end of year)',
        help_text='Note: we use this information to help create a custom '
                  'academic path for you - the quicker you want to complete, '
                  'the more work we will advise you to take on.'
    )

    hours_per_week = models.CharField(
        max_length=140,
        verbose_name='How much time per week can you dedicate '
                     'to the program? (use # of hours)'
    )

    personal_goal = models.TextField(
        verbose_name='What is a personal goal you have for yourself this year?'
                     ' How about five years from now?'
    )

    frustrated = models.TextField(
        verbose_name='When you get stressed or frustrated, '
                     'how can I best support you as a coach?'
    )

    anything_else = models.TextField(
        verbose_name='Is there anything else you want to tell me?'
    )

    class Meta:
        ordering = ["student__last_name", "student__first_name"]

    def get_absolute_url(self):
        return reverse(
            'coaching:profile detail',
            kwargs={'slug': self.student.slug}
        )

    def __str__(self):
        return "%s | %s - %s " % (
            "Coaching Profile",
            self.student.__str__(),
            self.student.WRU_ID
        )

    def save(self, **kwargs):
        try:
            self.student.elearn_record.elearn_status = 'New'
            self.student.elearn_record.save()
        except ObjectDoesNotExist:
            pass
        super(Profile, self).save()


class Coaching(models.Model):

    ELEARN = 'elearn'
    ACE = 'ace'
    OPEN = 'open'
    COACHING_TYPE_CHOICES = (
        (ELEARN, 'eLearn'),
        (ACE, 'ACE'),
        (OPEN, 'Open Coaching')
    )

    ACTIVE = 'Active'
    ON_HOLD = 'On Hold'
    INACTIVE = 'Inactive'
    ELL_CCR = 'ELL > CCR'
    COMPLETED_HISET = 'Completed HiSET'
    STATUS_CHOICES = (
        (ACTIVE, 'Active'),
        (ON_HOLD, 'On Hold'),
        (INACTIVE, 'Inactive'),
        (ELL_CCR, 'ELL > CCR'),
        (COMPLETED_HISET, 'Completed HiSET')
    )

    coachee = models.ForeignKey(
        Student,
        models.CASCADE,
        related_name='coaches'
    )

    coach = models.ForeignKey(
        Staff,
        models.PROTECT,
        related_name='coachees'
    )

    coaching_type = models.CharField(
        max_length=6,
        default='open',
        choices=COACHING_TYPE_CHOICES,
        help_text=_('Type of coaching (Choose One)')
    )

    active = models.BooleanField(
        default=True
    )

    status = models.CharField(
        max_length=20,
        default='Active',
        choices=STATUS_CHOICES,
    )

    start_date = models.DateTimeField(
    )

    end_date = models.DateTimeField(
        blank=True,
        null=True
    )

    last_modified = models.DateTimeField(
        auto_now=True
    )

    def latest_note(self):
        return self.notes.latest('pk')

    def get_absolute_url(self):
        return reverse(
            'coaching:coaching detail',
            kwargs={'pk': self.pk}
        )

    def __str__(self):
        return "%s coaching %s" % (
            self.coach.__str__(),
            self.coachee.__str__(),
        )

    def save(self, **kwargs):
        if self.active is True:
            try:
                self.coachee.elearn_record.elearn_status = 'Active'
                self.coachee.elearn_record.save()
            except ObjectDoesNotExist:
                pass
        super(Coaching, self).save()


class MeetingNote(models.Model):

    coaching = models.ForeignKey(
        Coaching,
        models.CASCADE,
        related_name='notes'
    )

    ELEARN = 'eLearn'
    ACE = 'ACE'
    OPEN = 'Open Coaching'

    MEETING_TYPE_CHOICES = (
        (ELEARN, 'eLearn'),
        (ACE, 'ACE'),
        (OPEN, 'Open Coaching')
    )

    EMAIL = 'email'
    PHONE = 'phone'
    TEXT = 'text'
    HANGOUTS = 'hangouts'
    MESSENGER = 'messenger'
    PERSON = 'In person'

    CONTACT_TYPE_CHOICES = (
        (EMAIL, 'Email'),
        (PHONE, 'Phone'),
        (TEXT, 'Text'),
        (HANGOUTS, 'Google Hangouts'),
        (MESSENGER, 'Facebook Messenger'),
        (PERSON, 'In Person')        
    )

    DURATION_CHOICES = (
        ("15", "15 min"),
        ("30", "30 min"),
        ("45", "45 min"),
        ("60", "60 min")
    )

    meeting_type = models.CharField(
        max_length=17,
        choices=MEETING_TYPE_CHOICES,
        help_text=_('Type of coaching (Choose One)')
    )

    contact_type = models.CharField(
        max_length=10,
        choices=CONTACT_TYPE_CHOICES,
        blank=True
    )

    next_steps = models.TextField(
        blank=True,
    )

    meeting_topic = models.TextField(
        blank=True,
    )

    meeting_date = models.DateField(
    )

    student_no_show = models.BooleanField(
        default=False,
        help_text='Check this box if the student failed to attend the meeting'
    )

    student_reschedule = models.BooleanField(
        default=False,
        help_text='Check this box if the student requested to reschedule the meeting'
    )

    student_cancel = models.BooleanField(
        default=False,
        help_text='Check this box if the student cancelled the meeting'
    )

    coach_cancel = models.BooleanField(
        default=False,
        help_text='Check this box if the coach cancelled the meeting'
    )

    low_grades = models.BooleanField(
        default=False,
        verbose_name='Concern: Low Grades'
    )

    class_absences = models.BooleanField(
        default=False,
        verbose_name='Concern: Class Absences'
    )

    meeting_absences = models.BooleanField(
        default=False,
        verbose_name='Concern: Meeting Absences'
    )

    cannot_reach = models.BooleanField(
        default=False,
        verbose_name='Concern: Coach Unable to Reach'
    )

    ace_withdrawl = models.BooleanField(
        default=False,
        verbose_name='Withdawing from Ace'
    )

    start_time = models.TimeField(
        null=True,
        blank=True
    )

    end_time = models.TimeField(
        null=True,
        blank=True
    )

    duration = models.TextField(
        max_length=3,
        choices=DURATION_CHOICES,
        blank=True
    )

    multiple_days = models.BooleanField(
        default=False,
        verbose_name='Meeting took place over multiple days'
    )

    progress = models.TextField(
        blank=True,
        help_text=_('Progress on Next Steps')
    )

    notes = models.TextField(
        blank=True,
    )

    class Meta:
        ordering = ['-meeting_date']

    def get_absolute_url(self):
        return reverse(
            'coaching:meeting note detail',
            kwargs={'pk': self.pk})

    def __str__(self):
        meeting_date = self.meeting_date.strftime("%a, %b %d")
        return "%s - %s" % (self.coaching, meeting_date)


class AceRecord(models.Model):

    HEALTHCARE = 'Healthcare'
    SKILLED_CRAFTS = 'Skilled Crafts'
    IT = 'IT'
    HOSPITALITY = 'Hospitality'
    PATHWAY_CHOICES = (
        (HEALTHCARE, 'Healthcare'),
        (SKILLED_CRAFTS, 'Skilled Crafts'),
        (IT, 'IT'),
        (HOSPITALITY, 'Culinary Arts / Hospitality')
    )

    HSE = 'HSE'
    HSD = 'HSD'
    NEITHER = 'Neither'
    HSD_CHOICES = (
        (HSE, 'HSE'),
        (HSD, 'HSD'),
        (NEITHER, 'Neither'),
    )

    APPLICANT = 'Applicant'
    PENDING = 'Pending'
    DEFERRED = 'Deferred'
    ACTIVE = 'Active'
    INACTIVE = 'InActive'
    COMPLETED = 'Completed'
    STATUS_CHOICES = (
        (APPLICANT, 'Applicant'),
        (PENDING, 'Pending'),
        (DEFERRED, 'Deferred'),
        (ACTIVE, 'Active'),
        (INACTIVE, 'InActive'),
        (COMPLETED, 'Completed')
    )

    FALL = 'Fall'
    SPRING = 'Spring'
    SUMMER = 'Summer'
    SEMESTER_CHOICES = (
        (FALL, 'Fall'),
        (SPRING, 'Spring'),
        (SUMMER, 'Summer'),
    )

    student = models.OneToOneField(
        Student,
        models.CASCADE,
        related_name='ace_record'
    )

    ace_status = models.CharField(
        choices=STATUS_CHOICES,
        max_length=9,
        blank=True
    )

    status_updated = models.DateField(
        blank=True,
        null=True
    )

    intake_semester = models.CharField(
        choices=SEMESTER_CHOICES,
        max_length=6,
        blank=True
    )

    intake_year = models.CharField(
        max_length=4,
        blank=True
    )

    lola = models.CharField(
        max_length=9,
        blank=True
    )

    dcc_email = models.EmailField(
        max_length=40,
        blank=True
    )

    ace_pathway = models.CharField(
        max_length=15,
        choices=PATHWAY_CHOICES,
        blank=True
    )

    program = models.CharField(
        max_length=40,
        blank=True
    )

    hsd = models.CharField(
        max_length=7,
        choices=HSD_CHOICES,
        default='Neither',
        blank=True,
        verbose_name='Diploma'
    )

    hsd_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='Diploma Date'
    )

    media_release = models.BooleanField(
        default=False
    )

    third_party_release = models.BooleanField(
        default=False
    )

    read_072 = models.BooleanField(
        default=False,
        verbose_name='Passed Townsend'
    )

    eng_062 = models.BooleanField(
        default=False,
        verbose_name='Passed ENG 062'
    )

    math_092 = models.BooleanField(
        default=False,
        verbose_name='Passed MATH 092'
    )

    math_098 = models.BooleanField(
        default=False,
        verbose_name='Passed MATH 098'
    )

    five_for_six = models.BooleanField(
        default=False,
        verbose_name='5 for 6 Scholarship'
    )

    five_for_six_year = models.CharField(
        max_length=4,
        blank=True
    )

    five_for_six_semester = models.CharField(
        choices=SEMESTER_CHOICES,
        max_length=6,
        blank=True   
    )

    reading_exit = models.BooleanField(
        default=False,
        verbose_name='Passed Reading Exit Exam'
    )

    writing_exit = models.BooleanField(
        default=False,
        verbose_name='Passed Writing Exit Exam'
    )

    math_exit = models.BooleanField(
        default=False,
        verbose_name='Passed Math Exit Exam'
    )

    nccer_cert = models.BooleanField(
        default = False,
        verbose_name = 'NCCER Cert'
    )

    bls_cert = models.BooleanField(
        default = False,
        verbose_name = 'Basic Life Support Cert'
    )

    servsafe_cert = models.BooleanField(
        default = False,
        verbose_name = 'ServSafe Cert'
    )

    microsoft_cert = models.BooleanField(
        default = False,
        verbose_name = 'Microsoft Cert'
    )
    def get_absolute_url(self):
        return reverse(
            'coaching:ace record detail',
            kwargs={'slug': self.student.slug}
        )

    def __str__(self):
        return "%s for %s-%s" % (
            "ACE Record",
            self.student.__str__(),
            self.student.WRU_ID,
        )


class ElearnRecord(models.Model):

    NEW = 'New'
    APPLICANT = 'Applicant'
    PENDING = 'Pending'
    HOLD = 'On Hold'
    ACTIVE = 'Active'
    INACTIVE = 'InActive'
    ALUMNI = 'Alumni'
    PARTNER = 'Partner'
    PARTNER_ALUMNUS = 'Partner Alumnus'
    CAMPUS = 'Campus'
    STATUS_CHOICES = (
        (NEW, 'New'),
        (APPLICANT, 'Applicant'),
        (PENDING, 'Pending'),
        (HOLD, 'On Hold'),
        (ACTIVE, 'Active'),
        (INACTIVE, 'InActive'),
        (ALUMNI, 'Alumni'),
        (PARTNER, 'Partner'),
        (PARTNER_ALUMNUS, 'Partner Alumnus'),
        (CAMPUS, 'Campus')
    )

    student = models.OneToOneField(
        Student,
        models.CASCADE,
        related_name='elearn_record'
    )

    elearn_status = models.CharField(
        choices=STATUS_CHOICES,
        default="Applicant",
        max_length=15,
        blank=True
    )

    status_updated = models.DateField(
        blank=True,
        null=True
    )

    intake_date = models.DateField(
        blank=True,
        null=True
    )

    g_suite_email = models.EmailField(
        max_length=60,
        blank=True,
    )

    def create_g_suite_account(self, service):
        if self.g_suite_email:
            pass
        else:
            first = clean_special_characters(self.student.first_name.split()[0])
            last = clean_special_characters(self.student.last_name.split()[0])
            name = ".".join([first, last]).lower()
            def check_email(name, x): # check g_suite for email, add numbers incrementally if email in use until email is valid
                if x == 0:
                    email = "@".join([name, 'elearnclass.org'])
                    try:
                        user = service.users().get(userKey=email).execute()
                        return check_email(name, x + 1)
                    except:
                        return email
                else:
                    new_name = "{0}{1}".format(name, x)
                    new_email = "@".join([new_name, 'elearnclass.org'])
                    try:
                        user = service.users().get(userKey=new_email).execute()
                        return check_email(name, x + 1)
                    except:
                        return new_email
            email = check_email(name, 0)

            record = {
                "primaryEmail": email,
                "name": {
                    "givenName": first,
                    "familyName": last
                },
                "password": "123456789",
                "externalIds": [
                    {
                        "value": self.student.WRU_ID,
                        "type": "custom",
                        "customType": "wru"
                    }
                ],
            }
            service.users().insert(body=record).execute()
            self.g_suite_email = email
            self.save()

    def send_g_suite_info(self):
        if self.student.email:
            g_suite = self.g_suite_email
            if self.student.alt_email:
                recipient_list = [self.student.email, self.student.alt_email]
            else:
                recipient_list = [self.student.email] 
            send_mail_task.delay(
                subject="Welcome to Delgado Adult Education Online!",
                message="",
                html_message="<p>Hello!</p><p>You have been invited"
                    " to online classes. You can login with your new email address"
                    " now, which is:</p><ul><li><strong>Username:</strong> {g_suite}"
                    "</li><li><strong>Password:</strong> 123456789</li></ul>"
                    "<p>This is a Google account that can be used with Gmail, "
                    "Drive, Calendar, and more. To get started, <strong>go to "
                    "<a href='http://classroom.google.com'>Google Classroom</a>"
                    " now and login with this new account.</strong>"
                    "</p><p>And for more tips, "
                    "<a href='https://docs.google.com/document/d/1M0ODyAMGGk6q4SfnEcdPUhiGYTLUxsWnI8Q7QYJGbJw/edit'>"
                    "click here to read the guide to get started!</a></p>"
                    "<p>If you have any questions, please contact coach@elearnclass.org</p>"
                    "<br><p>¡Bienvenido a Delgado Adult Education en línea!</p>"
                    "<p>Hola!</p><p>Ha sido invitado a clases en línea. Puede iniciar "
                    "sesión con su nueva dirección de correo electrónico ahora, "
                    "que es:</p><ul><li><strong>Nombre de usario:</strong> {g_suite}</li>"
                    "<li><strong>Password:</strong> 123456789</li></ul><p>Esta es una "
                    "cuenta de Google que se puede usar con Gmail, Drive, Calendar y más."
                    " Para comenzar, <strong>vaya a <a href='http://classroom.google.com'>Google Classroom</a>"
                    " ahora e inicie sesión con esta nueva cuenta.</strong></p><p>"
                    "<a href='https://docs.google.com/document/d/1cK3b8gArFICmYPB-gH15ke75uhCwCpORwoXUuDPJUj8/edit'>"
                    "¡Haga clic aquí para leer la guía para comenzar!</a><p>"
                    "Si tiene alguna pregunta, comuníquese con coach@elearnclass.org.</p>".format(
                    g_suite=g_suite
                ),
                from_email='robot@elearnclass.org',
                recipient_list=recipient_list
            )
            return True
        return False


    def get_absolute_url(self):
        return reverse(
            'coaching:elearn record detail',
            kwargs={'slug': self.student.slug}
        )

    def __str__(self):
        return "%s for %s-%s" % (
            "eLearn Record",
            self.student.__str__(),
            self.student.WRU_ID,
        )

    def save(self, **kwargs):
        if self.elearn_status in ('InActive', 'Alumni'):
            try:
                s = self.student.coaches.filter(coaching_type='elearn')
                s.update(active=False)
            except ObjectDoesNotExist:
                pass
        super(ElearnRecord, self).save()


class PerformanceDomainScreening(models.Model):
    DIFFICULTY_CHOICES = [
        ("0", 'No difficulty'),
        ("1", 'Mild difficulty'),
        ("2", 'Moderate difficulty'),
        ("3", 'Severe difficulty'),
        ("4", 'Cannot do')
    ]

    ENVIRONMENT_CHOICES = [
        ('quiet', 'Quiet space (ear mufflers, white noise, etc.)'),
        ('noise', 'Noise (e.g., listening to music while learning)'),
        ('extra_time', 'Extra time on task'),
        ('other', 'Other')
    ]

    student = models.OneToOneField(
        Student,
        models.CASCADE,
        related_name='pd_screening'
    )

    # Learning and Applying Knowledge
    seeing_difficulty = models.CharField(
        choices=DIFFICULTY_CHOICES,
        verbose_name="How difficult is it to see text/white board?"
    )
    hearing_difficulty = models.CharField(
        choices=DIFFICULTY_CHOICES,
        verbose_name="How difficult is it to see your teacher/classmates?"
    )
    reading_difficulty = models.CharField(
        choices=DIFFICULTY_CHOICES,
        verbose_name="How difficult is it for you to read?"
    )
    writing_difficulty = models.CharField(
        choices=DIFFICULTY_CHOICES,
        verbose_name="How difficult is it for you to write?"
    )
    math_difficulty = models.CharField(
        choices=DIFFICULTY_CHOICES,
        verbose_name="How difficult is math?"
    )
    problem_solving_difficulty = models.CharField(
        choices=DIFFICULTY_CHOICES,
        verbose_name="How difficult is it to figure out steps to solve a problem?"
    )
    speaking_difficulty = models.CharField(
        choices=DIFFICULTY_CHOICES,
        verbose_name="How difficult is it to speak to your teacher/classmates/neighbors/others?"
    )
    
    # Major Life Areas
    lifting_difficulty = models.CharField(
        choices=DIFFICULTY_CHOICES,
        verbose_name="How difficult is it to lift things? Are you in pain when lifting?"
    )
    walking_difficulty = models.CharField(
        choices=DIFFICULTY_CHOICES,
        verbose_name="How difficult is it for you to walk? Are you in pain when walking?"
    )
    stress_management = models.CharField(
        choices=DIFFICULTY_CHOICES,
        verbose_name="How difficult is it for you to manage stress?"
    )
    sleep_difficulty = models.CharField(
        choices=DIFFICULTY_CHOICES,
        verbose_name="How difficult is it to get enough sleep?"
    )
    community_access = models.CharField(
        choices=DIFFICULTY_CHOICES,
        verbose_name="How difficult is to for you to get around and be social?"
    )
    
    # Environment preferences for learning
    learning_environment = models.CharField(
        max_length=20,
        choices=ENVIRONMENT_CHOICES,
        verbose_name="What surroundings help you learn?"
    )


class Accommodations(models.Model):
    ACCOMMODATION_CHOICES = [
        ('used', 'Used Successfully in the Past'),
        ('willing', 'Willing to try'),
        ('not_interested', 'Not Interested')
    ]

    student = models.OneToOneField(
        Student,
        models.CASCADE,
        related_name='accommodations'
    )
    
    # Reading Accommodations
    reads_aloud = models.CharField(max_length=15, choices=ACCOMMODATION_CHOICES, verbose_name="Reading out loud on own")
    reads_with_someone = models.CharField(max_length=15, choices=ACCOMMODATION_CHOICES, verbose_name="Reading together with someone")
    needs_reader = models.CharField(max_length=15, choices=ACCOMMODATION_CHOICES, verbose_name="Being read to by someone")
    uses_text_to_speech = models.CharField(max_length=15, choices=ACCOMMODATION_CHOICES, verbose_name="Text-to-speech software")
    uses_colored_overlays = models.CharField(max_length=15, choices=ACCOMMODATION_CHOICES, verbose_name="Use of colored overlays")
    needs_colored_paper = models.CharField(max_length=15, choices=ACCOMMODATION_CHOICES, verbose_name="Use of colored paper for handouts/printer materials")
    uses_visual_guides = models.CharField(max_length=15, choices=ACCOMMODATION_CHOICES, verbose_name="Visual guides (graphic organizers, story maps)")
    takes_reading_notes = models.CharField(max_length=15, choices=ACCOMMODATION_CHOICES, verbose_name="Note taking while reading")
    uses_text_marking = models.CharField(max_length=15, choices=ACCOMMODATION_CHOICES, verbose_name="Highlighting, underlining, text marking")
    reading_other = models.CharField(max_length=255, blank=True, verbose_name="Other reading accommodations")
    
    # Writing Accommodations
    oral_before_writing = models.CharField(max_length=15, choices=ACCOMMODATION_CHOICES, verbose_name="Telling the story out loud before writing it")
    uses_word_prediction = models.CharField(max_length=15, choices=ACCOMMODATION_CHOICES, verbose_name="Use of word prediction")
    uses_dictation = models.CharField(max_length=15, choices=ACCOMMODATION_CHOICES, verbose_name="Use of text to speech and dictation software/features")
    uses_spell_check = models.CharField(max_length=15, choices=ACCOMMODATION_CHOICES, verbose_name="Use of spell checkers")
    needs_multiple_revisions = models.CharField(max_length=15, choices=ACCOMMODATION_CHOICES, verbose_name="Revising and editing multiple times")
    writing_other = models.CharField(max_length=255, blank=True, verbose_name="Other writing accommodations")
    
    # Comprehension Accommodations
    needs_demonstration = models.CharField(max_length=15, choices=ACCOMMODATION_CHOICES, verbose_name="Instructor shows me how something is done")
    needs_explanation = models.CharField(max_length=15, choices=ACCOMMODATION_CHOICES, verbose_name="Instructor tells me how I could understand")
    records_lectures = models.CharField(max_length=15, choices=ACCOMMODATION_CHOICES, verbose_name="Recording lectures to listen multiple times")
    uses_teacher_videos = models.CharField(max_length=15, choices=ACCOMMODATION_CHOICES, verbose_name="Viewing recorded videos by the teacher")
    needs_glossaries = models.CharField(max_length=15, choices=ACCOMMODATION_CHOICES, verbose_name="Use of short glossaries for common terms")
    needs_captions = models.CharField(max_length=15, choices=ACCOMMODATION_CHOICES, verbose_name="Use of closed captioning in videos")
    uses_visual_aids = models.CharField(max_length=15, choices=ACCOMMODATION_CHOICES, verbose_name="Use of visual guides: graphic organizers and story maps")
    uses_pictures = models.CharField(max_length=15, choices=ACCOMMODATION_CHOICES, verbose_name="Seeing or drawing pictures of what I am learning")
    needs_clear_expectations = models.CharField(max_length=15, choices=ACCOMMODATION_CHOICES, verbose_name="Knowing what I am expected to learn")
    works_in_pairs = models.CharField(max_length=15, choices=ACCOMMODATION_CHOICES, verbose_name="Working in pairs")
    needs_cultural_context = models.CharField(max_length=15, choices=ACCOMMODATION_CHOICES, verbose_name="Knowing the cultural context")
    asks_questions = models.CharField(max_length=15, choices=ACCOMMODATION_CHOICES, verbose_name="Asking questions")
    uses_sentence_pausing = models.CharField(max_length=15, choices=ACCOMMODATION_CHOICES, verbose_name="Pausing/rephrasing each sentence")
    uses_paragraph_pausing = models.CharField(max_length=15, choices=ACCOMMODATION_CHOICES, verbose_name="Pausing and retelling/rewriting each paragraph")
    makes_lists = models.CharField(max_length=15, choices=ACCOMMODATION_CHOICES, verbose_name="Making lists on my own")
    makes_glossaries = models.CharField(max_length=15, choices=ACCOMMODATION_CHOICES, verbose_name="Making my own glossaries")
    comprehension_other = models.CharField(max_length=255, blank=True, verbose_name="Other comprehension accommodations")
    
    # Math Accommodations
    uses_math_visuals = models.CharField(max_length=15, choices=ACCOMMODATION_CHOICES, verbose_name="Use of visual organizers")
    uses_manipulatives = models.CharField(max_length=15, choices=ACCOMMODATION_CHOICES, verbose_name="Use of manipulatives")
    uses_math_software = models.CharField(max_length=15, choices=ACCOMMODATION_CHOICES, verbose_name="Use of math/logic/simulation software")
    math_other = models.CharField(max_length=255, blank=True, verbose_name="Other math accommodations")


class ServiceProvider(models.Model):
    CATEGORY_CHOICES = [
        ('CAREER', 'Career Counseling and Job Placement'),
        ('EDUCATION', 'GED/HiSET Prep Classes and Testing'),
        ('WORKFORCE', 'Workforce Development Programs'),
        ('ACADEMIC', 'Tutoring and Academic Support'),
        ('MENTAL_HEALTH', 'Mental Health Services'),
        ('FINANCIAL', 'Financial Assistance'),
        ('COLLEGE', 'College and Technical School Programs'),
        ('FAMILY', 'Family and Childcare Support Services'),
        ('FOOD', 'Food and Nutrition Assistance'),
        ('HOUSING', 'Housing Assistance'),
        ('HEALTHCARE', 'Healthcare Services'),
        ('DIGITAL', 'Digital Literacy Training'),
        ('LEGAL', 'Legal Aid and Advocacy'),
        ('MENTORSHIP', 'Youth Mentorship'),
        ('TRANSPORT', 'Transportation Assistance'),
        ('LGBTQ', 'LGBTQ+ Support'),
        ('RECOVERY', 'Substance Abuse Recovery'),
        ('VOLUNTEER', 'Volunteer Opportunities'),
        ('VETERANS', 'Veterans Services'),
    ]

    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=200, blank=True)
    description = models.TextField()
    eligibility = models.TextField()

    def __str__(self):
        return f"{self.get_category_display()} - {self.name}"

    class Meta:
        ordering = ['category', 'name']


class Referral(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONTACTED', 'Provider Contacted'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('UNSUCCESSFUL', 'Unsuccessful'),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='service_referrals'
    )
    service_provider = models.ForeignKey(
        ServiceProvider,
        on_delete=models.PROTECT,
        related_name='client_referrals'
    )
    staff_member = models.ForeignKey(
        Staff,
        on_delete=models.PROTECT,
        related_name='referrals_made'
    )
    date_referred = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    notes = models.TextField(blank=True)
    followup_date = models.DateField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_referred']
