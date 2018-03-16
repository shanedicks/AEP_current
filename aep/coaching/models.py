from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.translation import ugettext_lazy as _
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

    def save(self):
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

    coachee = models.ForeignKey(
        Student,
        related_name='coaches'
    )

    coach = models.ForeignKey(
        Staff,
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

    def save(self):
        if self.active is True:
            try:
                self.coachee.elearn_record.elearn_status = 'Active'
                self.coachee.elearn_record.save()
            except ObjectDoesNotExist:
                pass
        super(Coaching, self).save()


class MeetingNote(models.Model):

    COLLEGE_OPTIONS = 'College Options'
    NEXT_STEPS = 'Next Steps'
    SCHEDULING = 'Schedule Classes'
    SKILL_BUILDING = 'Build Skills'
    ELEARN_CHECKIN = 'eLearn Check-in'
    ACE_COACHING = 'ACE Coaching'
    ACE_RETURN = 'Return to ACE'

    MEETING_TYPE_CHOICES = (
        (COLLEGE_OPTIONS, 'Discuss College Options'),
        (NEXT_STEPS, 'Plan Next Steps'),
        (SCHEDULING, 'Schedule Next Classes'),
        (SKILL_BUILDING, 'Build Student Skills'),
        (ELEARN_CHECKIN, 'eLearn Check-in'),
        (ACE_COACHING, 'ACE Student Coaching'),
        (ACE_RETURN, 'Plan for Return to ACE')
    )

    coaching = models.ForeignKey(
        Coaching,
        related_name='notes'
    )

    meeting_type = models.CharField(
        max_length=17,
        choices=MEETING_TYPE_CHOICES,
        help_text=_('Type of coaching (Choose One)')
    )

    meeting_date = models.DateField()

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

    start_time = models.TimeField()

    end_time = models.TimeField()

    progress = models.TextField(
        blank=True,
        help_text=_('Progress on Next Steps')
    )

    next_steps = models.TextField(
        blank=True,
        help_text=_('New Next Steps')
    )

    notes = models.TextField(
        blank=True,
        help_text=_('Other Notes')
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
        blank=True
    )

    hsd_date = models.DateField(
        blank=True,
        null=True)

    media_release = models.BooleanField(
        default=False
    )

    third_party_release = models.BooleanField(
        default=False
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
    STATUS_CHOICES = (
        (NEW, 'New'),
        (APPLICANT, 'Applicant'),
        (PENDING, 'Pending'),
        (HOLD, 'On Hold'),
        (ACTIVE, 'Active'),
        (INACTIVE, 'InActive'),
        (ALUMNI, 'Alumni')
    )

    student = models.OneToOneField(
        Student,
        related_name='elearn_record'
    )

    elearn_status = models.CharField(
        choices=STATUS_CHOICES,
        default="Applicant",
        max_length=9,
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
        max_length=40,
        blank=True,
    )

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

    def save(self):
        if self.elearn_status == 'InActive':
            try:
                s = self.student.coaches.filter(coaching_type='elearn')
                s.update(active=False)
            except ObjectDoesNotExist:
                pass
        super(ElearnRecord, self).save()
