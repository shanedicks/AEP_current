import logging
import requests
import bs4
import time
import sys
import csv
from datetime import datetime, timedelta
from django.apps import apps
from django.db import models, IntegrityError
from django.db.models import Sum
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from assessments import rules
from core.tasks import send_mail_task, send_sms_task
from core.utils import make_slug, make_AEP_ID, make_unique_slug, state_session

Q = models.Q
logger = logging.getLogger(__name__)

# make_slug and make_AEP_ID callables were defaults for Profile and Student -have to be kept or migrations break
def make_student_slug():
    return make_unique_slug('people', 'Student')

def make_staff_slug():
    return make_unique_slug('people', 'Staff')

def make_prospect_slug():
    return make_unique_slug('people', 'Prospect')

def move_test_history(orig, duplicate):
    try:
        t = orig.tests
        try:
            d = duplicate.tests
        except ObjectDoesNotExist:
            pass
        t.student = duplicate
        t.student_wru = duplicate.WRU_ID
        try:
            t.save()
        except IntegrityError:
            querysets = []
            querysets.append(d.tabe_tests.all())
            querysets.append(d.tabe_loc_tests.all())
            querysets.append(d.clas_e_tests.all())
            querysets.append(d.clas_e_loc_tests.all())
            querysets.append(d.gain_tests.all())
            querysets.append(d.hiset_practice_tests.all())
            for queryset in querysets:
                try:
                    queryset.update(student=t)
                except IntegrityError:
                    for test in queryset:
                        try:
                            test.student = t
                            test.save()
                        except IntegrityError:
                            test.delete()
            if d.last_test_date is not None:
                def copy_fields(t, d):
                    t.last_test_date = d.last_test_date
                    t.last_test_type = d.last_test_type
                    t.test_assignment = d.test_assignment
                if t.last_test_date is None:
                    copy_fields(t, d)
                elif t.last_test_date < d.last_test_date:
                    copy_fields(t, d)
            d.delete()
            t.student = duplicate
            t.student_wru = duplicate.WRU_ID
            t.save()
    except ObjectDoesNotExist:
        pass

def move_classes(orig, duplicate):
    for c in orig.classes.all():
        c.student = duplicate
        try:
            c.save()
        except IntegrityError:
            c.delete()

def move_appointments(orig, duplicate):
    for a in orig.test_appointments.all():
        a.student = duplicate
        try:
            a.save()
        except IntegrityError:
            a.delete()

def move_elearn_record(orig, duplicate):
    try:
        e = duplicate.elearn_record
        pass
    except ObjectDoesNotExist:
        try:
            e = orig.elearn_record
            e.student = duplicate
            e.save()
        except ObjectDoesNotExist:
            pass

def move_coaching(orig, duplicate):
    try:
        p = duplicate.coaching_profile
        pass
    except ObjectDoesNotExist:
        try:
            p = orig.coaching_profile
            p.student = duplicate
            p.save()
        except ObjectDoesNotExist:
            pass
    for c in orig.coaches.all():
        c.coachee = duplicate
        try:
            c.save()
        except IntegrityError:
            pass

def move_ace_record(orig, duplicate):
    try:
        e = duplicate.ace_record
        pass
    except ObjectDoesNotExist:
        try:
            a = orig.ace_record
            a.student = duplicate
            a.save()
        except ObjectDoesNotExist:
            pass

def move_college_interest(orig, duplicate):
    try:
        a = orig.college_interest
        a.student = duplicate
        a.save()
    except ObjectDoesNotExist:
        pass

def copy_office_tracking(orig, duplicate):
    n = duplicate
    if n.paperwork != 'C' and orig.paperwork != 'P':
        n.paperwork = orig.paperwork
    if n.folder != 'C' and orig.folder != 'P':
        n.folder = orig.folder
    if n.orientation != 'C' and orig.orientation != 'P':
        n.orientation = orig.orientation
    n.save()

def move_or_copy_paperwork(orig, duplicate):
    try:
        p = orig.student_paperwork
        try:
            np = duplicate.student_paperwork
        except ObjectDoesNotExist:
            np = None
        if np is None:
            p.student = duplicate
            p.save()
        else:
            bools = [
                f.name for f in type(p)._meta.get_fields()
                if f.get_internal_type() == 'BooleanField'
            ]
            for field_name in bools:
                setattr(np, field_name, max(getattr(p, field_name), getattr(np, field_name)))
            others = [
                'sd_other',
                'sh_other',
                'sh_request',
                'signature',
                'guardian_signature',
                'sig_date',
                'g_sig_date',
            ]
            if np.sig_date is not None and p.sig_date is not None:
                if p.sig_date < np.sig_date:
                    for field_name in others:
                        setattr(np, field_name,  getattr(p, field_name))
            elif p.sig_date is not None:
                for field_name in others:
                    setattr(np, field_name,  getattr(p, field_name))
            if np.pic_id_file == '' and p.pic_id_file != '':
                np.pic_id_file = p.pic_id_file
            np.save()
    except ObjectDoesNotExist:
        pass

def merge_pops(pop, pop2):
        pop2.last_service_date = max(pop.last_service_date, pop2.last_service_date)
        pop2.active = max(pop.active, pop2.active)
        pop2.made_gain = max(pop.made_gain, pop2.made_gain)
        if pop2.pretest_date is not None and pop.pretest_date is not None:
            pop2.pretest_date = min(pop.pretest_date, pop2.pretest_date)
        elif pop.pretest_date is not None:
            pop2.pretest_date = pop.pretest_date
        pop2.pretest_type = max(pop.pretest_type, pop2.pretest_type)
        pop2.save()
        pop.delete()

def move_or_merge_pops(orig, duplicate):
    og_pops = orig.pop.all()
    for pop in og_pops:
        try:
            pop.student = duplicate
            pop.save()
        except IntegrityError:
            conflict = duplicate.pop.get(
                start_date=pop.start_date
            )
            merge_pops(pop, conflict)

    new_pops = duplicate.pop.all()
    i, j = 0, 1
    while j < new_pops.count():
        orig = new_pops[i]
        duplicate = new_pops[j]
        exit = orig.last_service_date + timedelta(days=90)
        if duplicate.start_date <= exit:
            merge_pops(duplicate, orig)
        i += 1
        j += 1

def move_skill_masteries(orig, duplicate):
    sm = orig.skillmasterys.all()
    for record in sm:
        try:
            record.student = duplicate
            record.save()
        except IntegrityError:
            pass

def move_certificates(orig, duplicate):
    c = orig.certificates.all()
    for record in c:
        try:
            record.student = duplicate
            record.save()
        except IntegrityError:
            pass

def move_course_completions(orig, duplicate):
    cc = orig.coursecompletions.all()
    for record in cc:
        try:
            record.student = duplicate
            record.save()
        except IntegrityError:
            pass

def move_prospects(orig, duplicate):
    p = orig.prospects.all()
    for record in p:
        try:
            record.student = duplicate
            record.save()
        except IntegrityError:
            pass

def full_merge(orig, duplicate):
    nid = None
    if rules.needs_pretest(duplicate):
        nid = duplicate.WRU_ID
        duplicate.WRU_ID = orig.WRU_ID
    if nid is None:
        try:
            orig.WRU_ID = 'd' + orig.WRU_ID
        except TypeError:
            orig.WRU_ID = 'dNone'
    else:
        orig.WRU_ID = 'd' + nid.replace('x', '')
    move_test_history(orig, duplicate)
    move_classes(orig, duplicate)
    move_appointments(orig, duplicate)
    move_elearn_record(orig, duplicate)
    move_coaching(orig, duplicate)
    move_ace_record(orig, duplicate)
    move_college_interest(orig, duplicate)
    copy_office_tracking(orig, duplicate)
    move_or_copy_paperwork(orig, duplicate)
    move_or_merge_pops(orig, duplicate)
    move_skill_masteries(orig, duplicate)
    move_certificates(orig, duplicate)
    move_course_completions(orig, duplicate)
    move_prospects(orig, duplicate)
    duplicate.intake_date = orig.intake_date
    duplicate.notes = orig.notes
    duplicate.save()
    orig.duplicate_of = duplicate
    orig.duplicate = True
    orig.dupl_date = timezone.now().date()
    orig.save()

def merge_duplicates(dupe_id):
    orig_id = dupe_id.replace('x', '')
    try:
        orig = Student.objects.get(WRU_ID=orig_id, duplicate=False)
    except ObjectDoesNotExist:
        print(f"No student found with WRU_ID {orig_id}")
        orig = None
    if orig:
        dupes = Student.objects.filter(
            WRU_ID=dupe_id,
            duplicate=False,
            dob=orig.dob
        ).order_by('pk')
        while dupes.count() > 0:
            dupe = dupes[0]
            print(f"Merging orig {orig}-{orig_id} into dupe {dupe}-{dupe_id}")
            full_merge(orig, dupe)
            orig = Student.objects.get(WRU_ID=orig_id, duplicate=False)
            dupes = Student.objects.filter(
                WRU_ID=dupe_id,
                duplicate=False,
                dob=orig.dob
            ).order_by('pk')


class Profile(models.Model):
    STATE_CHOICES = (
        ("AL", "Alabama"),
        ("AK", "Alaska"),
        ("AZ", "Arizona"),
        ("AR", "Arkansas"),
        ("CA", "California"),
        ("CO", "Colorado"),
        ("CT", "Connecticut"),
        ("DC", "District of Columbia"),
        ("DE", "Delaware"),
        ("FL", "Florida"),
        ("GA", "Georgia"),
        ("HI", "Hawaii"),
        ("ID", "Idaho"),
        ("IL", "Illinois"),
        ("IN", "Indiana"),
        ("IA", "Iowa"),
        ("KS", "Kansas"),
        ("KY", "Kentucky"),
        ("LA", "Louisiana"),
        ("ME", "Maine"),
        ("MA", "Massachusetts"),
        ("MD", "Maryland"),
        ("MI", "Michigan"),
        ("MN", "Minnesota"),
        ("MS", "Mississippi"),
        ("MO", "Missouri"),
        ("MT", "Montana"),
        ("NC", "North Carolina"),
        ("ND", "North Dakota"),
        ("NH", "New Hampshire"),
        ("NJ", "New Jersey"),
        ("NM", "New Mexico"),
        ("NY", "New York"),
        ("NE", "Nebraska"),
        ("NV", "Nevada"),
        ("OH", "Ohio"),
        ("OK", "Oklahoma"),
        ("OR", "Oregon"),
        ("PA", "Pennsylvania"),
        ("RI", "Rhode Island"),
        ("SC", "South Carolina"),
        ("SD", "South Dakota"),
        ("TN", "Tennessee"),
        ("TX", "Texas"),
        ("UT", "Utah"),
        ("VA", "Virginia"),
        ("VT", "Vermont"),
        ("WV", "West Virginia"),
        ("WA", "Washington"),
        ("WI", "Wisconsin"),
        ("WY", "Wyoming")
    )
    CITY_CHOICES = (
        ("Abbeville", "Abbeville"),
        ("Abita Springs", "Abita Springs"),
        ("Addis", "Addis"),
        ("Albany", "Albany"),
        ("Alexandria", "Alexandria"),
        ("Amite", "Amite"),
        ("Anacoco", "Anacoco"),
        ("Angie", "Angie"),
        ("Arcadia", "Arcadia"),
        ("Arnaudville", "Arnaudville"),
        ("Ashland", "Ashland"),
        ("Athens", "Athens"),
        ("Atlanta", "Atlanta"),
        ("Baker", "Baker"),
        ("Baldwin", "Baldwin"),
        ("Ball", "Ball"),
        ("Basile", "Basile"),
        ("Baskin", "Baskin"),
        ("Bastrop", "Bastrop"),
        ("Baton Rouge", "Baton Rouge"),
        ("Belcher", "Belcher"),
        ("Benton", "Benton"),
        ("Bernice", "Bernice"),
        ("Berwick", "Berwick"),
        ("Bienville", "Bienville"),
        ("Blanchard", "Blanchard"),
        ("Bogalusa", "Bogalusa"),
        ("Bonita", "Bonita"),
        ("Bossier", "Bossier"),
        ("Boutte", "Boutte"),
        ("Boyce", "Boyce"),
        ("Breaux Bridge", "Breaux Bridge"),
        ("Broussard", "Broussard"),
        ("Brusly", "Brusly"),
        ("Bryceland", "Bryceland"),
        ("Bunkie", "Bunkie"),
        ("Calvin", "Calvin"),
        ("Campti", "Campti"),
        ("Cankton", "Cankton"),
        ("Carencro", "Carencro"),
        ("Castor", "Castor"),
        ("Chalmette", "Chalmette"),
        ("Central", "Central"),
        ("Chataignier", "Chataignier"),
        ("Chatham", "Chatham"),
        ("Cheneyville", "Cheneyville"),
        ("Choudrant", "Choudrant"),
        ("Church Point", "Church Point"),
        ("Clarence", "Clarence"),
        ("Clarks", "Clarks"),
        ("Clayton", "Clayton"),
        ("Clinton", "Clinton"),
        ("Colfax", "Colfax"),
        ("Collinston", "Collinston"),
        ("Columbia", "Columbia"),
        ("Converse", "Converse"),
        ("Cottonport", "Cottonport"),
        ("Cotton Valley", "Cotton Valley"),
        ("Coushatta", "Coushatta"),
        ("Covington", "Covington"),
        ("Creola", "Creola"),
        ("Crowley", "Crowley"),
        ("Cullen", "Cullen"),
        ("Delcambre", "Delcambre"),
        ("Delhi", "Delhi"),
        ("Delta", "Delta"),
        ("Denham Springs", "Denham Springs"),
        ("DeQuincy", "DeQuincy"),
        ("DeRidder", "DeRidder"),
        ("Dixie Inn", "Dixie Inn"),
        ("Dodson", "Dodson"),
        ("Donaldsonville", "Donaldsonville"),
        ("Downsville", "Downsville"),
        ("Doyline", "Doyline"),
        ("Dry Prong", "Dry Prong"),
        ("Dubach", "Dubach"),
        ("Dubberly", "Dubberly"),
        ("Duson", "Duson"),
        ("East Hodge", "East Hodge"),
        ("Edgefield", "Edgefield"),
        ("Elizabeth", "Elizabeth"),
        ("Elton", "Elton"),
        ("Epps", "Epps"),
        ("Erath", "Erath"),
        ("Eros", "Eros"),
        ("Estherwood", "Estherwood"),
        ("Eunice", "Eunice"),
        ("Evergreen", "Evergreen"),
        ("Farmerville", "Farmerville"),
        ("Fenton", "Fenton"),
        ("Ferriday", "Ferriday"),
        ("Fisher", "Fisher"),
        ("Florien", "Florien"),
        ("Folsom", "Folsom"),
        ("Fordoche", "Fordoche"),
        ("Forest", "Forest"),
        ("Forest Hill", "Forest Hill"),
        ("Franklin", "Franklin"),
        ("Franklinton", "Franklinton"),
        ("French Settlement", "French Settlement"),
        ("Georgetown", "Georgetown"),
        ("Gibsland", "Gibsland"),
        ("Gilbert", "Gilbert"),
        ("Gilliam", "Gilliam"),
        ("Glenmora", "Glenmora"),
        ("Golden Meadow", "Golden Meadow"),
        ("Goldonna", "Goldonna"),
        ("Gonzales", "Gonzales"),
        ("Grambling", "Grambling"),
        ("Gramercy", "Gramercy"),
        ("Grand Cane", "Grand Cane"),
        ("Grand Coteau", "Grand Coteau"),
        ("Grand Isle", "Grand Isle"),
        ("Grayson", "Grayson"),
        ("Greensburg", "Greensburg"),
        ("Greenwood", "Greenwood"),
        ("Gretna", "Gretna"),
        ("Grosse Tete", "Grosse Tete"),
        ("Gueydan", "Gueydan"),
        ("Hall Summit", "Hall Summit"),
        ("Hammond", "Hammond"),
        ("Harahan", "Harahan"),
        ("Harrisonburg", "Harrisonburg"),
        ("Haughton", "Haughton"),
        ("Haynesville", "Haynesville"),
        ("Heflin", "Heflin"),
        ("Henderson", "Henderson"),
        ("Hessmer", "Hessmer"),
        ("Hodge", "Hodge"),
        ("Homer", "Homer"),
        ("Hornbeck", "Hornbeck"),
        ("Hosston", "Hosston"),
        ("Houma", "Houma"),
        ("Ida", "Ida"),
        ("Independence", "Independence"),
        ("Iota", "Iota"),
        ("Iowa", "Iowa"),
        ("Jackson", "Jackson"),
        ("Jamestown", "Jamestown"),
        ("Jeanerette", "Jeanerette"),
        ("Jean Lafitte", "Jean Lafitte"),
        ("Jena", "Jena"),
        ("Jennings", "Jennings"),
        ("Jonesboro", "Jonesboro"),
        ("Jonesville", "Jonesville"),
        ("Junction", "Junction"),
        ("Kaplan", "Kaplan"),
        ("Keachi", "Keachi"),
        ("Keithville", "Keithville"),
        ("Kenner", "Kenner"),
        ("Kentwood", "Kentwood"),
        ("Kilbourne", "Kilbourne"),
        ("Killian", "Killian"),
        ("Kinder", "Kinder"),
        ("Krotz Springs", "Krotz Springs"),
        ("Lafayette", "Lafayette"),
        ("Lake Arthur", "Lake Arthur"),
        ("Lake Charles", "Lake Charles"),
        ("Lake Providence", "Lake Providence"),
        ("Lecompte", "Lecompte"),
        ("Leesville", "Leesville"),
        ("Leonville", "Leonville"),
        ("Lillie", "Lillie"),
        ("Lisbon", "Lisbon"),
        ("Livingston", "Livingston"),
        ("Livonia", "Livonia"),
        ("Lockport", "Lockport"),
        ("Logansport", "Logansport"),
        ("Longstreet", "Longstreet"),
        ("Loreauville", "Loreauville"),
        ("Lucky", "Lucky"),
        ("Lutcher", "Lutcher"),
        ("McNary", "McNary"),
        ("Madisonville", "Madisonville"),
        ("Mamou", "Mamou"),
        ("Mandeville", "Mandeville"),
        ("Mangham", "Mangham"),
        ("Mansfield", "Mansfield"),
        ("Mansura", "Mansura"),
        ("Many", "Many"),
        ("Maringouin", "Maringouin"),
        ("Marion", "Marion"),
        ("Marksville", "Marksville"),
        ("Martin", "Martin"),
        ("Maurice", "Maurice"),
        ("Melville", "Melville"),
        ("Mermentau", "Mermentau"),
        ("Mer Rouge", "Mer Rouge"),
        ("Merryville", "Merryville"),
        ("Metairie", "Metairie"),
        ("Minden", "Minden"),
        ("Monroe", "Monroe"),
        ("Montgomery", "Montgomery"),
        ("Montpelier", "Montpelier"),
        ("Mooringsport", "Mooringsport"),
        ("Moreauville", "Moreauville"),
        ("Morgan City", "Morgan City"),
        ("Morganza", "Morganza"),
        ("Morse", "Morse"),
        ("Mound", "Mound"),
        ("Mount Lebanon", "Mount Lebanon"),
        ("Napoleonville", "Napoleonville"),
        ("Natchez", "Natchez"),
        ("Natchitoches", "Natchitoches"),
        ("Newellton", "Newellton"),
        ("New Iberia", "New Iberia"),
        ("New Llano", "New Llano"),
        ("New Orleans", "New Orleans"),
        ("New Roads", "New Roads"),
        ("Noble", "Noble"),
        ("North Hodge", "North Hodge"),
        ("Norwood", "Norwood"),
        ("Oakdale", "Oakdale"),
        ("Oak Grove", "Oak Grove"),
        ("Oak Ridge", "Oak Ridge"),
        ("Oberlin", "Oberlin"),
        ("Oil City", "Oil City"),
        ("Olla", "Olla"),
        ("Opelousas", "Opelousas"),
        ("Palmetto", "Palmetto"),
        ("Parks", "Parks"),
        ("Patterson", "Patterson"),
        ("Pearl River", "Pearl River"),
        ("Pine Prairie", "Pine Prairie"),
        ("Pineville", "Pineville"),
        ("Pioneer", "Pioneer"),
        ("Plain Dealing", "Plain Dealing"),
        ("Plaquemine", "Plaquemine"),
        ("Plaucheville", "Plaucheville"),
        ("Pleasant Hill", "Pleasant Hill"),
        ("Pollock", "Pollock"),
        ("Ponchatoula", "Ponchatoula"),
        ("Port Allen", "Port Allen"),
        ("Port Barre", "Port Barre"),
        ("Port Vincent", "Port Vincent"),
        ("Powhatan", "Powhatan"),
        ("Provencal", "Provencal"),
        ("Quitman", "Quitman"),
        ("Rayne", "Rayne"),
        ("Rayville", "Rayville"),
        ("Reeves", "Reeves"),
        ("Richmond", "Richmond"),
        ("Richwood", "Richwood"),
        ("Ridgecrest", "Ridgecrest"),
        ("Ringgold", "Ringgold"),
        ("Robeline", "Robeline"),
        ("Rodessa", "Rodessa"),
        ("Rosedale", "Rosedale"),
        ("Roseland", "Roseland"),
        ("Rosepine", "Rosepine"),
        ("Ruston", "Ruston"),
        ("St. Francisville", "St. Francisville"),
        ("St. Gabriel", "St. Gabriel"),
        ("St. Joseph", "St. Joseph"),
        ("St. Martinville", "St. Martinville"),
        ("Saline", "Saline"),
        ("Sarepta", "Sarepta"),
        ("Scott", "Scott"),
        ("Shongaloo", "Shongaloo"),
        ("Shreveport", "Shreveport"),
        ("Sibley", "Sibley"),
        ("Sicily Island", "Sicily Island"),
        ("Sikes", "Sikes"),
        ("Simmesport", "Simmesport"),
        ("Simpson", "Simpson"),
        ("Simsboro", "Simsboro"),
        ("Slaughter", "Slaughter"),
        ("Slidell", "Slidell"),
        ("Sorrento", "Sorrento"),
        ("South Mansfield", "South Mansfield"),
        ("Spearsville", "Spearsville"),
        ("Springfield", "Springfield"),
        ("Springhill", "Springhill"),
        ("Stanley", "Stanley"),
        ("Sterlington", "Sterlington"),
        ("Stonewall", "Stonewall"),
        ("Sulphur", "Sulphur"),
        ("Sun", "Sun"),
        ("Sunset", "Sunset"),
        ("Tallulah", "Tallulah"),
        ("Tangipahoa", "Tangipahoa"),
        ("Thibodaux", "Thibodaux"),
        ("Tickfaw", "Tickfaw"),
        ("Tullos", "Tullos"),
        ("Turkey Creek", "Turkey Creek"),
        ("Urania", "Urania"),
        ("Varnado", "Varnado"),
        ("Vidalia", "Vidalia"),
        ("Vienna", "Vienna"),
        ("Ville Platte", "Ville Platte"),
        ("Vinton", "Vinton"),
        ("Vivian", "Vivian"),
        ("Walker", "Walker"),
        ("Washington", "Washington"),
        ("Waterproof", "Waterproof"),
        ("Welsh", "Welsh"),
        ("Westlake", "Westlake"),
        ("West Monroe", "West Monroe"),
        ("Westwego", "Westwego"),
        ("White Castle", "White Castle"),
        ("Wilson", "Wilson"),
        ("Winnfield", "Winnfield"),
        ("Winnsboro", "Winnsboro"),
        ("Wisner", "Wisner"),
        ("Woodworth", "Woodworth"),
        ("Youngsville", "Youngsville"),
        ("Zachary", "Zachary"),
        ("Zwolle", "Zwolle"),
        ("Other", "Other"),
    )
    EC_RELATIONS_CHOICES = (
        ("D", "Father"),
        ("M", "Mother"),
        ("S", "Spouse"),
        ("B", "Sibling"),
        ("F", "Friend"),
        ("G", "Legal Guardian"),
        ("O", "Other")
    )
    PRONOUN_CHOICES = (
        ("He/Him/His", "He/Him/His"),
        ("She/Her/Hers", "She/Her/Hers"),
        ("They/Them/Theirs", "They/Them/Theirs"),
        ("Ze/Hir/Hirs", "Ze/Hir/Hirs"),
        ("I do not use a pronoun", "I do not use a pronoun"),
        ("Other, please ask", "Other, please ask"),
        ("I use all gender pronouns", "I use all gender pronouns")
    )
    TITLE_CHOICES = (
        ("Mx.", "Mx."),
        ("Miss", "Miss"),
        ("Ms.", "Ms."),
        ("Mrs.", "Mrs."),
        ("Mr.", "Mr."),
        ("Dr.", "Dr.")
    )
    first_name = models.CharField(
        max_length=30,
        verbose_name=_("First Name"),
        blank=True
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name=_("Last Name"),
        blank=True
    )
    email = models.EmailField(
        max_length=60,
        verbose_name=_("Email Address"),
        blank=True
    )
    alt_email = models.EmailField(
        max_length=60,
        verbose_name=_("Alternate Email Address"),
        blank=True
    )
    phone = models.CharField(
        max_length=20,
        verbose_name=_("Phone Number"),
    )
    alt_phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_("Alternate Phone Number"),
    )
    street_address_1 = models.CharField(
        max_length=60,
        verbose_name=_("Street Address 1"),
    )
    street_address_2 = models.CharField(
        max_length=60,
        blank=True,
        verbose_name=("Street Address 2"))
    city = models.CharField(
        max_length=30,
        choices=CITY_CHOICES,
        default="New Orleans"
    )
    other_city = models.CharField(
        max_length=30,
        blank=True
    )
    state = models.CharField(
        max_length=2,
        choices=STATE_CHOICES,
        default="LA"
    )
    zip_code = models.CharField(
        max_length=10,
        verbose_name=_("Zip Code")
    )
    dob = models.DateField(
        verbose_name=_("Date of Birth")
    )
    emergency_contact = models.CharField(
        max_length=60,
        blank=True,
        verbose_name=_("Emergency Contact Full Name")
    )
    ec_phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_("Their Phone Number")
    )
    ec_email = models.EmailField(
        max_length=40,
        blank=True,
        verbose_name=_("Their Email Address")
    )
    ec_relation = models.CharField(
        max_length=1,
        choices=EC_RELATIONS_CHOICES,
        default='O',
        verbose_name=_("Their Relationship to You")
    )
    nickname = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("Preferred Name or Nickname")
    )
    pronoun = models.CharField(
        max_length=25,
        blank=True,
        choices=PRONOUN_CHOICES,
        verbose_name=_("Pronouns")
    )
    title = models.CharField(
        max_length=5,
        blank=True,
        choices=TITLE_CHOICES,
        verbose_name=_("Title")
    )
    # make_slug here creates a 5 character string for use in absolute urls

    class Meta:
        abstract = True

    def __str__(self):
        return '{0} {1}'.format(self.first_name, self.last_name)


class Student(Profile):

    PARISH_CHOICES = (
        ("1", "Outside LA"),
        ("2", "Acadia"),
        ("3", "Allen"),
        ("4", "Ascension"),
        ("5", "Assumption"),
        ("6", "Avoyelles"),
        ("7", "Beauregard"),
        ("8", "Bienville"),
        ("9", "Bossier"),
        ("10", "Caddo"),
        ("11", "Calcasieu"),
        ("12", "Caldwell"),
        ("13", "Cameron"),
        ("14", "Catahoula"),
        ("15", "Claiborne"),
        ("16", "Concordia"),
        ("17", "De Soto"),
        ("18", "East Baton Rouge"),
        ("19", "East Carroll"),
        ("20", "East Feliciana"),
        ("21", "Evangeline"),
        ("22", "Franklin"),
        ("23", "Grant"),
        ("24", "Iberia"),
        ("25", "Iberville"),
        ("26", "Jackson"),
        ("27", "Jefferson"),
        ("28", "Jefferson Davis"),
        ("29", "Lafayette"),
        ("30", "Lafourche"),
        ("31", "La Salle"),
        ("32", "Lincoln"),
        ("33", "Livingston"),
        ("34", "Madison"),
        ("35", "Morehouse"),
        ("36", "Natchitoches"),
        ("37", "Orleans"),
        ("38", "Ouachita"),
        ("39", "Plaquemines"),
        ("40", "Pointe Coupee"),
        ("41", "Rapides"),
        ("42", "Red River"),
        ("43", "Richland"),
        ("44", "Sabine"),
        ("45", "St. Bernard"),
        ("46", "St. Charles"),
        ("47", "St. Helena"),
        ("48", "St. James"),
        ("49", "St. John the Baptist"),
        ("50", "St. Landry"),
        ("51", "St. Martin"),
        ("52", "St. Mary"),
        ("53", "St. Tammany"),
        ("54", "Tangipahoa"),
        ("55", "Tensas"),
        ("56", "Terrebonne"),
        ("57", "Union"),
        ("58", "Vermilion"),
        ("59", "Vernon"),
        ("60", "Washington"),
        ("61", "Webster"),
        ("62", "West Baton Rouge"),
        ("63", "West Carroll"),
        ("64", "West Feliciana"),
        ("65", "Winn"),
    )
    MALE = 'M'
    FEMALE = 'F'
    GENDER_CHOICES = (
        (MALE, 'Male'),
        (FEMALE, 'Female'),
    )
    SINGLE = 'S'
    MARRIED = 'M'
    DIVORCED = 'D'
    WIDOWED = 'W'
    OTHER = 'O'
    MARITAL_STATUS_CHOICES = (
        (SINGLE, 'Single'),
        (MARRIED, 'Married'),
        (DIVORCED, 'Divorced'),
        (WIDOWED, 'Widowed'),
        (OTHER, 'Other')
    )
    CCR = 'C'
    ELL = 'E'
    ELEARN = 'D'
    SUCCESS = 'S'
    ACE = 'A'
    PROGRAM_CHOICES = (
        (CCR, "College and Career Readiness - HiSET Prep Classes"),
        (ELL, "Beginning English Language Classes"),
        (ELEARN, "Online Classes"),
        (ACE, "ACE Program"),
    )
    PRIMARY_GOAL_CHOICES = (
        ("1", "I want to earn a high school equivalency diploma (HiSET, formerly GED)"),
        ("2", "I want to work on my reading, writing, or math skills"),
        ("3", "I want to learn English"),
        ("4", "I want to prepare for college"),
        ("5", "I want to work on my computer skills, financial skills, or health literacy"),
        ("6", "I want to start college classes while working on my reading, writing, and math skills"),
        ("7", "I want to participate in workforce trainings wille working on my reading, writing, and math skills"),
        ("8", "I want to start college classes while earning my high school equivalency diploma"),
        ("9", "I want to explore career options")
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        models.PROTECT,
        related_name='student',
        verbose_name=_("user"),
        null=True,
        blank=True
    )
    slug = models.CharField(
        unique=True,
        default=make_student_slug,
        max_length=5
    )
    intake_date = models.DateField(
        null=True,
        blank=True,
        default=timezone.now
    )
    WRU_ID = models.CharField(
        null=True,
        blank=True,
        max_length=20
    )
    other_ID = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_("State ID, Passport #, Visa info, etc. (Optional)")
    )
    other_ID_name = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_('What kind of ID is this? (Optional)')
    )
    US_citizen = models.BooleanField(
        default=False,
        verbose_name=_("US Citizen")
    )
    prior_registration = models.BooleanField(
        default=False,
        verbose_name=_("Returning Student"),
        help_text=_("Have you registered with this program in the past?")
    )
    program = models.CharField(
        max_length=1,
        choices=PROGRAM_CHOICES,
        default='C'
    )
    ccr_app = models.BooleanField(
        default=False,
        verbose_name=_("HiSET In-Person")
    )
    ell_app = models.BooleanField(
        default=False,
        verbose_name=_("ELL In-Person")
    )
    ell_online_app = models.BooleanField(
        default=False,
        verbose_name=_("ELL Online")
    )
    ace_app = models.BooleanField(
        default=False,
        verbose_name=_("ACE")
    )
    e_learn_app = models.BooleanField(
        default=False,
        verbose_name=_("HiSET Online")
    )
    success_app = models.BooleanField(
        default=False,
        verbose_name=_("Success")
    )
    eng_boot_app = models.BooleanField(
        default=False,
        verbose_name=_("Eng. Boot")
    )
    math_boot_app = models.BooleanField(
        default=False,
        verbose_name=_("Math Boot")
    )
    accuplacer_app = models.BooleanField(
        default=False,
        verbose_name=_("Accuplacer")
    )
    certifications_app = models.BooleanField(
        default=False,
        verbose_name=_('Certifications')
    )
    parish = models.CharField(
        max_length=2,
        choices=PARISH_CHOICES,
        default='37'
    )
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        verbose_name=_('Sex')
    )
    marital_status = models.CharField(
        max_length=1,
        choices=MARITAL_STATUS_CHOICES,
        default='S',
        verbose_name=_('Marital Status')
    )
    partner = models.CharField(
        max_length=40,
        blank=True
    )
    duplicate_of = models.ForeignKey(
        'self',
        models.CASCADE,
        null=True,
        blank=True,
        related_name='duplicated_by'
    )
    duplicate = models.BooleanField(
        default=False
    )
    dupl_date = models.DateField(
        null=True,
        blank=True
    )
    notes = models.TextField(
        blank=True
    )

    PENDING = 'P'
    INCOMPLETE = 'I'
    COMPLETE = 'C'

    OFFICE_CHOICES = (
        (PENDING, 'Pending'),
        (INCOMPLETE, 'Incomplete'),
        (COMPLETE, 'Complete')
    )

    paperwork = models.CharField(
        max_length=1,
        blank=True,
        choices=OFFICE_CHOICES,
        default=PENDING
    )

    folder = models.CharField(
        max_length=1,
        blank=True,
        choices=OFFICE_CHOICES,
        default=PENDING
    )

    orientation = models.CharField(
        max_length=1,
        blank=True,
        choices=OFFICE_CHOICES,
        default=PENDING
    )

    intake_form = models.BooleanField(
        default = False
    )

    intake_quiz = models.BooleanField(
        default = False
    )

    allow_texts = models.BooleanField(
        default = True
    )
    primary_goal = models.CharField(
        max_length=50,
        default = "1",
        choices = PRIMARY_GOAL_CHOICES
    )
    check_goal_1 = models.BooleanField(
        default = False,
        verbose_name = _("I want to earn a high school equivalency diploma (HiSET, formerly GED)")
    )
    check_goal_2 = models.BooleanField(
        default = False,
        verbose_name = _("I want to work on my reading, writing, or math skills")
    )
    check_goal_3 = models.BooleanField(
        default = False,
        verbose_name = _("I want to learn English")
    )
    check_goal_4 = models.BooleanField(
        default = False,
        verbose_name = _("I want to prepare for college")
    )
    check_goal_5 = models.BooleanField(
        default = False,
        verbose_name = _("I want to work on my computer skills, financial skills, or health literacy")
    )
    check_goal_6 = models.BooleanField(
        default = False,
        verbose_name = _("I want to start college classes while working on my reading, writing, and math skills")
    )
    check_goal_7 = models.BooleanField(
        default = False,
        verbose_name = _("I want to participate in workforce trainings wille working on my reading, writing, and math skills")
    )
    check_goal_8 = models.BooleanField(
        default = False,
        verbose_name = _("I want to start college classes while earning my high school equivalency diploma")
    )
    check_goal_9 = models.BooleanField(
        default = False,
        verbose_name = _("I want to explore career options")
    )

    on_campus = models.BooleanField(
        default = False,
        verbose_name = _("On Campus - in person courses where students meet at a specific time as a group") 
    )
    online_solo = models.BooleanField(
        default = False,
        verbose_name = _("Online, Self Paced - online coursework completed when learner is ready")
    )
    online_cohort = models.BooleanField(
        default = False,
        verbose_name = _("Online, Cohort - online course where students meet at a specific time as a group")
    )
    hybrid = models.BooleanField(
        default = False,
        verbose_name = _("Hybrid - some online and some in person")
    )
    morning = models.BooleanField(
        default = False,
        verbose_name = _("Morning (8:30am - 1:00pm)")
    )
    afternoon = models.BooleanField(
        default = False,
        verbose_name = _("Afternoon (1:00pm - 4:00pm)")
    )
    evening = models.BooleanField(
        default = False,
        verbose_name = _("Evening (5:30pm - 8:30pm)")
    )
    weekend = models.BooleanField(
        default = False,
        verbose_name = _("Weekend")
    )
    mw = models.BooleanField(
        default = False,
        verbose_name = _("Monday and Wednesday")
    )
    tr = models.BooleanField(
        default = False,
        verbose_name = _("Tuesday and Thursday")
    )
    sat = models.BooleanField(
        default = False,
        verbose_name = _("Saturday")
    )
    site_preference = models.ManyToManyField(
        "sections.Site",
        blank=True,
    )
    computer_access = models.BooleanField(
        default = False,
        verbose_name = _("I have access to a computer or device to participate in online classes or resources")
    )
    internet_access = models.BooleanField(
        default = False,
        verbose_name = _("I have access to the internet")
    )


    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self):
        string = super().__str__()
        if self.partner not in ['', "Job1", 'JeffPar']:
            string = f"{self.partner}- " + string
        return string

    def get_absolute_url(self):
        return reverse('people:student detail', kwargs={'slug': self.slug})

    def testing_status(self):
        if rules.has_valid_test_record(self):
            status = "No Test Needed"
        elif rules.needs_pretest(self) | rules.needs_post_test(self):
            status = "Test Needed"
        else:
            status = "Something is wrong"
        return status

    def future_appts(self):
        return self.test_appointments.filter(
            event__start__gte=timezone.now()
        ).order_by('event__start')

    def active_classes(self):
        return self.classes.filter(
            status="A"
        ).order_by(
            '-section__ending',
            '-section__semester__end_date'
        )

    def completed_classes(self):
        return self.classes.filter(
            status="C"
        ).order_by(
            '-section__ending',
            '-section__semester__end_date'
        )

    def dropped_classes(self):
        return self.classes.filter(
            status="D"
        ).order_by(
        '-section__ending',
        '-section__semester__end_date'
        )

    def current_classes(self):
        today = timezone.localdate()
        classes = self.classes.filter(
            section__semester__end_date__gte=today
        ) | self.classes.filter(
            section__ending__gte=today
        )
        return classes.order_by(
            '-section__semester__end_date'
        )

    def past_classes(self):
        today = timezone.localdate()
        classes = self.classes.filter(
            section__semester__end_date__lt=today
        ) | self.classes.filter(
            section__ending__lt=today
        )
        return classes.order_by(
            '-section__semester__end_date'
        )

    def all_classes(self):
        return self.classes.all()

    def latest_class_start(self):
        semester_start = self.classes.latest('section__semester__start_date').section.semester.start_date
        section_start = self.classes.latest('section__starting').section.starting
        if section_start is not None:
            return max(section_start, semester_start)
        else:
            return semester_start

    def all_attendance(self, from_date=None, to_date=None):
        queryset = apps.get_model('sections', 'Attendance').objects.filter(enrollment__student=self)
        if from_date:
            queryset = queryset.filter(attendance_date__gte=from_date)
        if to_date:
            queryset = queryset.filter(attendance_date__lte=to_date)
        return queryset

    def last_attendance(self):
        return self.all_attendance().filter(attendance_type='P').latest('attendance_date').attendance_date

    def all_test_appointments(self, from_date=None, to_date=None):
        queryset = self.test_appointments.all()
        if from_date:
            queryset = queryset.filter(event__start__gte=from_date)
        if to_date:
            queryset = queryset.filter(event__end__lte=to_date)
        return queryset

    def total_hours(self, from_date=None, to_date=None):
        class_attendance = sum(a.hours for a in self.all_attendance(from_date, to_date))
        event_attendance = sum(a.hours for a in self.all_test_appointments(from_date, to_date))
        return class_attendance + event_attendance

    def testify(self):
        TestHistory = apps.get_model('assessments', 'TestHistory')
        if TestHistory.objects.filter(student=self).exists():
            pass
        else:
            if self.WRU_ID not in [None, 'No ID']:
                TestHistory.objects.create(student=self, student_wru=self.WRU_ID)

    def track(self):
        Paperwork = apps.get_model('people', 'Paperwork')
        try: 
            Paperwork.objects.create(student=self)
        except:
            pass

    def create_elearn_record(self):
        Elearn = apps.get_model('coaching', 'ElearnRecord')
        if Elearn.objects.filter(student=self).exists():
            pass
        else:
            Elearn.objects.create(
                student=self,
                intake_date=timezone.now()
            )

    def create_pops(self):
        dates = list(self.test_appointments.exclude(
            attendance_date=None
        ).filter(
            attendance_type='P'
        ).values_list('attendance_date', flat=True))

        dates.extend(list(self.all_attendance().exclude(
            attendance_date=None
        ).filter(
            attendance_type='P'
        ).values_list('attendance_date', flat=True)))

        dates = sorted(dates)
        for date in dates:
            exit = date - timedelta(days=90)
            try:
                pop = PoP.objects.filter(
                    student=self,
                    last_service_date__gte=exit,
                ).latest()
                if date > pop.last_service_date:
                    pop.last_service_date=date
                    pop.save()
            except PoP.DoesNotExist:
                pop = PoP(
                    student=self,
                    start_date=date,
                    last_service_date=date,
                )
                try:
                    tests = self.tests
                    pretest_limit = date - timedelta(days=180)
                    if (tests.last_test_date is not None and
                        pop.start_date > tests.last_test_date and
                        tests.last_test_date > pretest_limit):
                        pop.pretest_date = tests.last_test_date
                        pop.pretest_type = tests.last_test_type
                except ObjectDoesNotExist:
                    pass
                pop.save()

    def sign_paperwork_form_link(self):
        return "https://www.dccaep.org{0}".format(
            reverse('people:sign paperwork', kwargs={'slug': self.slug})
        )

    def pic_id_form_link(self):
        return "https://www.dccaep.org{0}".format(
            reverse('people:upload photo id', kwargs={'slug': self.slug})
        )

    def orientation_link(self):
        return "https://www.dccaep.org{0}".format(
            reverse('people:orientation start', kwargs={'slug': self.slug})
        )        

    def email_form_link(self, url_name):
        if url_name == 'upload photo id':
            try:
                paperwork = self.student_paperwork
                send = True if paperwork.pic_id_file == '' else False
            except ObjectDoesNotExist:
                send = False 
            url = self.pic_id_form_link()
            html_message = ''
            message = 'Hello from Delgado Adult Education. Click the link to upload a picture of your photo id: {0}'.format(url)
        if url_name == 'sign paperwork':
            try:
                paperwork = self.student_paperwork
                send = True if paperwork.sig_date is None else False
            except ObjectDoesNotExist:
                send = False
            url = self.sign_paperwork_form_link()
            html_message = ''
            message = 'Hello from Delgado Adult Education. Click the link to submit the rest of your registration paperwork: {0}'.format(url)
        recipient_list = []
        if self.email != '':
            recipient_list.append(self.email)
        try:
            elearn = self.elearn_record
            if elearn.g_suite_email != '':
                recipient_list.append(elearn.g_suite_email)
        except ObjectDoesNotExist:
            pass
        if len(recipient_list) > 0:
            send_mail_task.delay(
                subject = 'Delgado Adult Education Registration Paperwork',
                message = message,
                html_message = html_message,
                from_email = 'no_reply@elearnclass.org',
                recipient_list = recipient_list,
            )

    def text_form_link(self, url_name):
        if url_name == 'upload photo id':
            try:
                paperwork = self.student_paperwork
                send = True if paperwork.pic_id_file == '' else False
            except ObjectDoesNotExist:
                send = False            
            url = self.pic_id_form_link()
            message = 'Hello from Delgado Adult Education. Click the link to upload a picture of your photo id: {0}'.format(url)
        if url_name == 'sign paperwork':
            try:
                paperwork = self.student_paperwork
                send = True if paperwork.sig_date is None else False
            except ObjectDoesNotExist:
                send = False
            url = self.sign_paperwork_form_link()
            message = 'Hello from Delgado Adult Education. Click the link to submit the rest of your registration paperwork: {0}'.format(url)            
        if self.phone != '' and send:
            send_sms_task.delay(self.phone, message)

    def content_filter(self, queryset):
        return queryset

    def schedule_filter(self, queryset):
        time_filter_query = Q()
        if self.morning:
            time_filter_query |= Q(start_time__gte='08:30:00', end_time__lte='13:00:00')
        if self.afternoon:
            time_filter_query |= Q(start_time__gte='13:00:00', end_time__lte='16:00:00')
        if self.evening:
            time_filter_query |= Q(start_time__gte='17:30:00', end_time__lte='20:30:00')
        if self.weekend:
            time_filter_query |= Q(saturday=True) | Q(sunday=True)
        day_filter_query = Q()
        if self.mw:
            day_filter_query |= Q(monday=True, wednesday=True)
        if self.tr:
            day_filter_query |= Q(tuesday=True, thursday=True)
        if self.sat:
            day_filter_query |= Q(saturday=True)
        site_filter_query = Q()
        if self.site_preference.exists():
            site_filter_query = Q(site__in=self.site_preference.all())
        return queryset.filter(time_filter_query, day_filter_query, site_filter_query)

    def suggested_classes(self):
        sections = apps.get_model('sections', 'Section').objects.filter(
            Q(semester__end_date__gte=timezone.now()) | Q(ending__gte=timezone.now())
        )
        sections = self.schedule_filter(sections)
        sections = self.content_filter(sections)
        return sections

    @property
    def program_from_interest(self):
        program = []
        if any([self.ccr_app, self.e_learn_app, self.accuplacer_app, self.success_app, self.certifications_app]):
            program.append("CCR")
        if any([self.ell_app, self.ell_online_app]):
            program.append("ELL")
        return ", ".join(program)

class Staff(Profile):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        models.CASCADE,
        related_name='staff',
        verbose_name=_("user"))
    
    slug = models.CharField(
        unique=True,
        default=make_staff_slug,
        max_length=5
    )

    wru = models.CharField(blank=True, max_length=5)

    bio = models.TextField(blank=True, max_length=4000)

    g_suite_email = models.EmailField(
        blank=True,
        max_length=50
    )

    teacher = models.BooleanField(default=True)

    prospect_advisor = models.BooleanField(default=False)

    coach = models.BooleanField(default=False)

    active = models.BooleanField(default=True)

    full_time = models.BooleanField(default=False)

    partner = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'staff'
        ordering = ["last_name", "first_name"]

    def get_absolute_url(self):
        return reverse('people:staff home', kwargs={'slug': self.slug})

    def active_coachees(self):
        return self.coachees.filter(status='Active')

    def on_hold_coachees(self):
        return self.coachees.filter(status='On Hold')

    def inactive_coachees(self):
        return self.coachees.filter(status='Inactive')

    def ell_ccr_coachees(self):
        return self.coachees.filter(status='ELL > CCR')

    def hiset_coachees(self):
        return self.coachees.filter(status='Completed HiSET')

    def enrolled_coachees(self):
        return self.coachees.filter(coachee__classes__status='A').distinct()

    def active_prospects(self):
        return self.prospects.filter(active=True)

    def inactive_prospects(self):
        return self.prospects.filter(active=False, student=None)

    def closed_prospects(self):
        return self.prospects.filter(active=True).exclude(student=None)

    def current_classes(self):
        today = timezone.localdate()
        classes = self.classes.filter(
            semester__end_date__gte=today,
            semester__start_date__lte=today
        ) | self.classes.filter(
            ending__gte=today,
            starting__lte=today
        )
        return classes.order_by(
            '-ending',
            '-monday',
            'start_time'
        )

    def upcoming_classes(self):
        today = timezone.localdate()
        classes = self.classes.filter(
            semester__start_date__gt=today
        ) | self.classes.filter(
            starting__gt=today
        )
        return classes.order_by(
            'starting',
            'semester__start_date',
            '-monday',
            'start_time'
        )

    def past_classes(self):
        today = timezone.localdate()
        classes = self.classes.filter(
            semester__end_date__lt=today
        ) | self.classes.filter(
            ending__lt=today
        )
        return classes.order_by(
            '-ending',
            '-semester__end_date',
            '-monday',
            'start_time'
        )


class Paperwork(models.Model):

    student = models.OneToOneField(
        Student,
        models.CASCADE,
        related_name='student_paperwork'
    )
    ferpa = models.BooleanField(
        default = False,
        verbose_name = 'FERPA'
    )
    testing = models.BooleanField(
        default = False,
        verbose_name = 'Testing Agreement'
    )
    technology = models.BooleanField(
        default = False,
        verbose_name = 'Technology Usage Agreement'
    )
    contract = models.BooleanField(
        default = False,
        verbose_name = 'Student Contract'
    )
    disclosure = models.BooleanField(
        default = False,
        verbose_name = 'Self-Disclosure Form'
    )
    writing = models.BooleanField(
        default = False,
        verbose_name = 'Writing Sample'
    )
    pic_id = models.BooleanField(
        default = False,
        verbose_name = 'Picture ID'
    )
    sd_reading = models.BooleanField(
        default=False,
        verbose_name='Reading'
    )
    sd_math = models.BooleanField(
        default=False,
        verbose_name='Math'
    )
    sd_language = models.BooleanField(
        default=False,
        verbose_name='Language'
    )
    sd_attention = models.BooleanField(
        default=False,
        verbose_name='Attention Deficit Disorder/Attention Deficit Hyperactivity Disorder'
    )
    sd_other = models.CharField(
        max_length=140,
        blank=True,
        verbose_name='Other (explain)'
    )
    sh_self_se = models.BooleanField(
        default = False,
        verbose_name='Self-contained Special Education Classroom'
    )
    sh_resource_se = models.BooleanField(
        default = False,
        verbose_name='Resource Special Education Classroom'
    )
    sh_title1_read = models.BooleanField(
        default = False,
        verbose_name='Title 1 Reading'
    )
    sh_title1_math = models.BooleanField(
        default = False,
        verbose_name='Title 1 Math'
    )
    sh_504 = models.BooleanField(
        default = False,
        verbose_name='504 Accommodations'
    )
    sh_medication = models.BooleanField(
        default = False,
        verbose_name='Medication for A.D.D. or A.D.H.D'
    )
    sh_other = models.CharField(
        max_length=140,
        blank=True,
        verbose_name = 'Other (explain)'
    )
    sh_request = models.TextField(
        blank=True,
        verbose_name='I feel I need help in the following area(s):'
    )
    writing_sample = models.TextField(
        verbose_name = 'Student Writing Sample',
        blank=True
    )
    signature = models.CharField(
        max_length=140,
        blank=True
    )
    sig_date = models.DateField(
        null=True
    )
    guardian_signature = models.CharField(
        max_length=140,
        blank=True
    )
    g_sig_date = models.DateField(
        null=True,
        blank=True
    )
    pic_id_file = models.CharField(
        max_length=50,
        blank=True
    )


    class Meta:
        verbose_name_plural = 'paperwork'
        ordering = ['student__last_name', 'student__first_name']

    def __str__(self):
        return '{0} Paperwork'.format(self.student)

    def pic_id_url(self):
        if self.pic_id_file == '':
            return ""
        else:
            return "https://drive.google.com/file/d/{0}/view".format(self.pic_id_file)

    def save(self, *args, **kwargs):
        super(Paperwork, self).save(*args, **kwargs)
        if self.sig_date:
            student = self.student
            student.paperwork = student.COMPLETE
            student.save()

def convert_date_format(date_string):
    date_i = datetime.strptime(date_string, "%m/%d/%y")
    return datetime.strftime(date_i, "%m/%d/%Y")


def get_SID(sid):
    return "".join(sid.split("-"))

def get_age_at_intake(dob, intake_date):
    diff = intake_date - dob
    age = diff.days // 365
    return age


def citizen(i):
    if i == 1:
        cit = "True"
    else:
        cit = "False"
    return cit


def marital(i):
    statuses = {
        "S": "1",
        "M": "2",
        "D": "3",
        "W": "4",
        "O": "5"
    }
    return statuses[i]


def gender(i):
    genders = {
        "M": 2,
        "F": 1
    }
    return genders[i]


def state(i):
    states = {
        "AL": "2",
        "AK": "1",
        "AZ": "4",
        "AR": "3",
        "CA": "5",
        "CO": "6",
        "CT": "7",
        "DC": "8",
        "DE": "9",
        "FL": "10",
        "GA": "11",
        "HI": "12",
        "ID": "14",
        "IL": "15",
        "IN": "16",
        "IA": "13",
        "KS": "17",
        "KY": "18",
        "LA": "19",
        "ME": "22",
        "MA": "20",
        "MD": "21",
        "MI": "23",
        "MN": "24",
        "MS": "26",
        "MO": "25",
        "MT": "27",
        "NE": "30",
        "NV": "34",
        "NH": "31",
        "NJ": "32",
        "NM": "33",
        "NY": "35",
        "NC": "28",
        "ND": "29",
        "OH": "36",
        "OK": "37",
        "OR": "38",
        "PA": "39",
        "RI": "40",
        "SC": "41",
        "SD": "42",
        "TN": "43",
        "TX": "44",
        "UT": "45",
        "VA": "46",
        "VT": "47",
        "WA": "48",
        "WV": "50",
        "WI": "49",
        "WY": "51"
    }
    return states[i]


def email_status(i):
    if i != "":
        return "true"
    else:
        return "false"


def true_false(i):
    if i is True:
        return "true"
    else:
        return "false"


def hl_tf(i):
    if i is True:
        return "True"
    else:
        return "False"


def primary_program(student):
    if student.success_app:
        program = '14'
    elif student.ace_app:        
        program = '15'
    elif student.e_learn_app:
        program = '12'
    elif student.ell_app:
        program = '16'
    else:
        program = "1"
    return program


def secondary_program(student):
    program = ""
    if student.ccr_app:
        program = '8'
    if student.ell_app:
        program = '6'
    return program


def ell(student):
    if student.ell_app:
        return "true"
    else:
        return "false"


def employment_status(i):
    emp = {
        "1": "1_EM",
        "9": "1_EM",
        "2": "3_UE",
        "3": "3_UE",
        "4": "3_UE",
        "5": "11_EMR",
        "6": "3_UE",
        "7": "14_RT",
        "8": "3_UE"
    }
    return emp[i]


def migrant(i):
    mig = {
        "0": 0,
        "1": 1,
        "2": 2,
        "3": 3,
        "4": 0,
    }
    return mig[i]


def one_stop(i):
    o = {
        "1": 1,
        "2": 2,
        "3": 3,
        "4": 0
    }
    return o[i]


def y_n_u(i):
    y = {
        "": 9,
        "1": 1,
        "2": 0,
        "3": 9
    }
    return y[i]


def school_status(i):
    status = {
        "1": 1,
        "2": 2,
        "3": 3,
        "4": 4,
        "5": 5,
        "6": 6
    }
    return status[i]


def dislocated(i):
    if i is True:
        return 1
    else:
        return 0


def voc_rehab(i):
    v = {
        "1": 1,
        "2": 2,
        "3": 3,
        "4": 0
    }
    return v[i]

def check_farm(wioa):
    if wioa.migrant_seasonal_status == "4":
        return "false"
    else:
        return "true"

def low_income(wioa):
    avg = wioa.household_income / wioa.household_size
    return avg >= 12,750

def check_statements(wioa):
    if any([
        wioa.migrant_seasonal_status != "4",
        wioa.lacks_adequate_residence,
        wioa.criminal_record,
        wioa.in_foster_care,
        wioa.single_parent,
        low_income(wioa)
    ]):
        return "false"
    else:
        return "true"

def pronouns(i):
    p = {
        "He/Him/His": 1,
        "She/Her/Hers": 2,
        "They/Them/Theirs": 3,
        "Ze/Hir/Hirs": 4,
        "I do not use a pronoun": 4,
        "Other, please ask": 4,
        "I use all gender pronouns": 4
    }
    if i in p.keys():
        other = i if p[i] not in [1,2,3] else ""
        return (p[i], other)
    else:
        return ("", "")

def title(i):
    t = {
        "Mx.": "",
        "Miss": "Ms.",
        "Ms.": "Ms.",
        "Mrs.": "Mrs.",
        "Mr.": "Mr.", 
    }
    if i in t.keys():
        return t[i]
    else:
        return ""

def ec_name(i):
    name = i.split(" ", 1)
    if len(name) < 2:
        name.append('')
    return name

def ec_relation(i):
    r = {
        "D": 1,
        "M": 2,
        "S": 3,
        "B": 6,
        "F": 4,
        "G": 5,
        "O": 6
    }
    return r[i]


def full_time(i):
    return i == "1"

def labor_force(i):
    l = "true" if i in ["6", "4", "3"] else "false"

def looking_for_work(i):
    l = "true" if i in ["8", "2"] else "false"

def recieved_assistance(wioa):
    if any([
        wioa.TANF,
        wioa.TANF_2,
        wioa.SNAP,
        wioa.SSI,
        wioa.Tstate
    ]):
        return "true"
    else :
        return "false"

class WIOA(models.Model):

    EMPLOYMENT_STATUS_CHOICES = (
        ("1", "Employed - Full Time"),
        ("9", "Employed - Part Time"),
        ("5", "Employed, but received notice of termination or Military separation is pending"),
        ("2", "Unemployed - Looking For Work"),
        ("4", "Not in labor force / Not looking for work"),
        ("7", "Retired")
    )
    MIGRANT_SEASONAL_STATUS_CHOICES = (
        ("0", "I am a farmworker"),
        ("1", "I am a seasonal farmworker who has worked the last 12 months in agriculture or farm fishing labor"),
        ("2", "I am a seasonal farmworker with no permanent residence (migrant)"),
        ("3", "I am a dependent of a farmworker"),
        ("4", "None of these apply to me"),
    )
    YES_NO_UNKNOWN = (
        ("1", "Yes"),
        ("2", "No"),
        ("3", "Unknown"),
    )
    YES_NO = (
        ("1", "Yes"),
        ("2", "No"),
    )
    ONE_STOP_CHOICES = (
        ("1", "Yes, Local Formula"),
        ("2", "Yes, Statewide"),
        ("3", "Yes, Both Local and Statewide"),
        ("4", "No"),
    )
    VOCATIONAL_REHAB_CHOICES = (
        ("1", "Vocational Rehabilitation"),
        ("2", "Vocational Rehabilitation and Employment, Statewide"),
        ("3", "Both, VR and VR&E"),
        ("4", "No"),
    )
    SCHOOL_STATUS_CHOICES = (
        ("1", "In-School, H.S. or less"),
        ("2", "In-School, Alternative School"),
        ("3", "In-School, Post H.S."),
        ("4", "Not attending school or H.S. dropout"),
        ("5", "Not attending school; H.S. graduate"),
        ("6", "Not attending school; within age of compulsory school attendance"),
    )
    TRAINING_TYPE_CHOICES = (
        ("1", "On the Job Training"),
        ("2", "Skill Upgrading"),
        ("3", "Entrepreneurial Training (non-WIOA Youth)"),
        ("4", "ABE or ESL in conjunction with Training (non-TAA funded)"),
        ("5", "Customized Training"),
        ("6", "Other Occupational Skills Training"),
        ("7", "Remedial Training (ABE/ESL – TAA only)"),
        ("8", "Prerequisite Training"),
        ("9", "Registered Apprenticeship"),
        ("10", "Youth Occupational Skills Training"),
        ("11", "Other Non-Occupational-Skills Training"),
        ("0", "No Training Service"),
    )
    PROGRAM_OF_STUDY_CHOICES = (
        ("1", "A program of study leading to an industry-recognized certificate or certification"),
        ("2", "A program of study leading to a certificate of completion of an apprenticeship"),
        ("3", "A program of study leading to a license recognized by the State involved or the Federal Government"),
        ("4", "A program of study leading to an associate degree"),
        ("5", "A program of study leading to a baccalaureate degree"),
        ("6", "A program of study leading to a community college certificate of completion"),
        ("7", "A program of study leading to a secondary school diploma or its equivalent"),
        ("8", "A program of study leading to employment"),
        ("9", "A program of study leading to a measureable skills gain leading to a credentiacredential or employmentment"),
        ("10", "Youth Occupational Skills Training"),
    )
    HIGHEST_COMPLETED_CHOICES = (
        ("1", "NO FORMAL SCHOOL"),
        ("2", "COMPLETED 1 YEAR"),
        ("3", "COMPLETED 2 YEARS"),
        ("4", "COMPLETED 3 YEARS"),
        ("5", "COMPLETED 4 YEARS"),
        ("6", "COMPLETED 5 YEARS"),
        ("7", "COMPLETED 6 YEARS"),
        ("8", "COMPLETED 7 YEARS"),
        ("9", "COMPLETED 8 YEARS"),
        ("10", "COMPLETED 9 YEARS"),
        ("11", "COMPLETED 10 YEARS"),
        ("12", "COMPLETED 11 YEARS"),
        ("13", "COMPLETED 12 YEARS (HS DIPLOMA NOT EARNED)"),
        ("14", "COMPLETED 13 YEARS"),
        ("15", "COMP 14 YEARS/ASSC DEG/TECHNICAL DIPLOMA"),
        ("16", "COMPLETED 15 YEARS"),
        ("17", "COMPLETED BACHELOR DEGREE"),
        ("18", "COMPLETED BEYOND BACHELOR DEGREE"),
        ("19", "HIGH SCHOOL EQUIVALENCY"),
        ("20", "CERTIFICATE OF ATTENDANCE OR COMPLETION (HS ONLY)"),
        ("21", "POST SECONDARY DEGREE/CERTIFICATE EARNED"),
        ("22", "COMPLETED 12 YEARS (HS DIPLOMA EARNED)"),
    )
    COMPLETED_AT_ENTRY_CHOICES = (
        ("0", "NO SCHOOL GRADE COMPLETED"),
        ("1", "COMPLETED 1 YEAR"),
        ("2", "COMPLETED 2 YEARS"),
        ("3", "COMPLETED 3 YEARS"),
        ("4", "COMPLETED 4 YEARS"),
        ("5", "COMPLETED 5 YEARS"),
        ("6", "COMPLETED 6 YEARS"),
        ("7", "COMPLETED 7 YEARS"),
        ("8", "COMPLETED 8 YEARS"),
        ("9", "COMPLETED 9 YEARS"),
        ("10", "COMPLETED 10 YEARS"),
        ("11", "COMPLETED 11 YEARS"),
        ("12", "COMPLETED 12 YEARS"),
    )
    SCHOOL_LOCATION_CHOICES = (
        ("", "Please Select"),
        ("1", "US Based"),
        ("2", "Non-US Based"),
    )
    NATIVE_LANGUAGE_CHOICES = (
        ("english", "English"),
        ("spanish", "Spanish"),
        ("vietnamese", "Vietnamese"),
        ("arabic", "Arabic"),
        ("chinese", "Chinese"),
        ("french", "French"),
        ("korean", "Korean"),
        ("japanese", "Japanese"),
        ("creole", "Creole"),
        ("portugese", "Portugese"),
        ("turkish", "Turkish"),
        ("russian", "Russian"),
        ("other", "Other")
    )
    COUNTRY_CHOICES = (
        ("1", "United States"),
        ("2", "India"),
        ("3", "Australia"),
        ("4", "Japan"),
        ("5", "New Zealand"),
        ("6", "Philippines"),
        ("7", "Turkey"),
        ("8", "Austria"),
        ("9", "Belgium"),
        ("10", "Denmark"),
        ("11", "France"),
        ("12", "Germany"),
        ("13", "Italy"),
        ("14", "Portugal"),
        ("15", "Spain"),
        ("16", "Sweden"),
        ("17", "Argentina"),
        ("18", "Brazil"),
        ("19", "Russia"),
        ("20", "South Korea"),
        ("21", "Egypt"),
        ("22", "England"),
        ("23", "Greece"),
        ("24", "Singapore"),
        ("25", "South Africa"),
        ("26", "Mexico"),
        ("27", "Afghanistan"),
        ("28", "Algeria"),
        ("29", "Albania"),
        ("30", "Aruba"),
        ("31", "Bahamas"),
        ("32", "North Korea"),
        ("33", "Canada"),
        ("34", "China"),
        ("35", "Georgia"),
        ("36", "Hong Kong"),
        ("37", "Indonesia"),
        ("38", "Iraq"),
        ("39", "Israel"),
        ("40", "Kuwait"),
        ("41", "Korea"),
        ("42", "Lebanon"),
        ("43", "Malaysia"),
        ("44", "Nigeria"),
        ("45", "Norway"),
        ("46", "Oman"),
        ("47", "Pakistan"),
        ("48", "Switzerland"),
        ("49", "Thailand"),
        ("50", "United Arab Emirates"),
        ("51", "United Kingdom"),
        ("52", "Switzerland"),
        ("53", "Thailand"),
        ("100", "Other"),

    )
    REFERRER_CHOICES = (
        ("1", "TV"),
        ("2", "RADIO"),
        ("3", "SOCIAL MEDIA"),
        ("4", "BROCHURE"),
        ("5", "CAREER COMPASS"),
        ("6", "COACH"),
        ("7", "COLLEGE RECRUITER"),
        ("8", "FACULTY/STAFF"),
        ("9", "FAMILY MEMBER"),
        ("10", "FORMER STUDENT"),
        ("11", "FRIEND"),
        ("12", "HIGH SCHOOL COUNSELOR"),
        ("13", "INTERNET SEARCH"),
        ("14", "NEWSPAPER"),
        ("15", "OTHER"),
        ("16", "ONE STOP"),
        ("17", "AMERICAN JOB CENTER"),
        ("18", "UNEMPLOYMENT OFFICE"),
    )
    PARENTAL_STATUS_CHOICES = (
        ( "1", "parent of children 1-5"),
        ( "2", "parent of children 6-10"),
        ( "3", "parent of children 11-13"),
        ( "4", "parent of children 14-18"),
        ( "0", "No")
    )
    DISABILITY_CHOICES = (
        ("1", "Yes"),
        ("2", "No"),
        ("3", "Do not wish to disclose")
    )
    student = models.OneToOneField(
        Student,
        models.CASCADE,
        related_name='WIOA'
    )
    SID = models.CharField(
        max_length=11,
        blank=True,
        verbose_name="SSN",
    )
    hispanic_latino = models.BooleanField(
        default=False,
        verbose_name=_("Hispanic/Latino"),
    )
    amer_indian = models.BooleanField(
        default=False,
        verbose_name=_("American Indian or Alaska Native")
    )
    asian = models.BooleanField(
        default=False,
        verbose_name=_("Asian")
    )
    black = models.BooleanField(
        default=False,
        verbose_name=_("Black or African American")
    )
    white = models.BooleanField(
        default=False,
        verbose_name=_("White")
    )
    pacific_islander = models.BooleanField(
        default=False,
        verbose_name=_("Native Hawaiian or Pacific Islander")
    )
    native_language = models.CharField(
        max_length=20,
        choices=NATIVE_LANGUAGE_CHOICES,
        blank=True,
        verbose_name=_("Native Language")
    )
    other_language = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_("Other Native Language Not Listed")
    )
    country = models.CharField(
        max_length=20,
        choices=COUNTRY_CHOICES,
        blank=True,
        verbose_name=_("Country of Birth")
    )
    other_country = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_("Other Country if not listed")
    )
    current_employment_status = models.CharField(
        max_length=2,
        choices=EMPLOYMENT_STATUS_CHOICES,
        default="2",
        verbose_name=_("What is your current employment status")
    )
    employer = models.CharField(
        max_length=25,
        blank=True,
        verbose_name=_("Employer")
    )
    occupation = models.CharField(
        max_length=25,
        blank=True,
        verbose_name=_("Occupation")
    )
    parental_status = models.CharField(
        max_length=2,
        choices=PARENTAL_STATUS_CHOICES,
        blank=True,
        verbose_name=_("Are you a parent?")
    )
    current_industry = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("If you are currently employed, what industry cluster do you work in?")
    )
    industry_preference = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("If you could get a job or change jobs, what industry cluster would you like to work in?")
    )
    household_income = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Annual Household Income")
    )
    household_size = models.PositiveIntegerField(
        default=1,
        verbose_name=_("How many family members including yourself have lived in your household in the past six months?")
    )
    TANF = models.BooleanField(
        default=False,
        verbose_name=_("TANF (Temporary Assistance for Needy Families")
    )
    TANF_2 = models.BooleanField(
        default=False,
        verbose_name=_("Have you received TANF for more than two years in total?")
    )
    SNAP = models.BooleanField(
        default=False,
        verbose_name=_("SNAP (Supplemental Nutrition Assistance Program) Food Stamps")
    )
    SSI = models.BooleanField(
        default=False,
        verbose_name=_("SSI (Supplemental Security Income)")
    )
    Tstate = models.BooleanField(
        default=False,
        verbose_name=_("Tstate or Local income-based public assistance")
    )
    veteran = models.BooleanField(
        default=False,
        verbose_name=_("I am a veteran")
    )
    criminal_record = models.BooleanField(
        default=False,
        verbose_name=_("I have a criminal record that makes it hard to find a job.")
    )
    long_term_unemployed = models.BooleanField(
        default=False,
        verbose_name=_("Long-term Unemployed"),
        help_text=_("If you are not working, has it been 27 weeks (6 months) or longer since you had a job?")
    )
    migrant_seasonal_status = models.CharField(
        max_length=2,
        choices=MIGRANT_SEASONAL_STATUS_CHOICES,
        default="4",
        verbose_name=_("Farmworker Status")
    )
    single_parent = models.BooleanField(
        default=False,
        verbose_name=_("I am a single parent. I am unmarried or seperated from my spouse and have primary responsibility for one or more dependent children under the age of 18, or I am a single, pregnant woman.")
    )
    help_with_schoolwork = models.BooleanField(
        default = False,
        verbose_name = _("Helping more frequently with their schoolwork.")
    )
    student_teacher_contact  = models.BooleanField(
        default = False,
        verbose_name = _("Increasing contact with my children's teachers to discuss children's education")
    )
    parent_volunteering = models.BooleanField(
        default = False,
        verbose_name = _("Being more involved in my children's school, such as attendending school activities and parent meetings, and volunteering")
    )
    read_to_children = models.BooleanField(
        default = False,
        verbose_name = _("Reading to children")
    )
    visit_library  = models.BooleanField(
        default = False,
        verbose_name = _("Visiting a library")
    )
    purchase_books = models.BooleanField(
        default = False,
        verbose_name = _("Purchasing books or magazines")
    )
    referred_by = models.CharField(
        max_length=2,
        blank=True,
        choices=REFERRER_CHOICES
    )
    digital_signature = models.CharField(
        max_length = 100,
        blank = True,
        verbose_name = _("DISCLAIMER: By typing your name below, you are signing this application electronically. You agree that your electronic signature is the legal equivalent of your manual signature on this application.")
    )
    disability_notice = models.CharField(
        max_length = 1,
        blank = True,
        choices = DISABILITY_CHOICES,
        verbose_name = _("Are you an Individual with a Disability?"),
        help_text= _("In the Americans with Disabilities Act of 1990, a disability is defined as a physical or mental impairment that substantially limits one or more of a person’s major life activities.")
    )
    request_accommodation = models.BooleanField(
        default = False,
        verbose_name = _("Check here to indicate that you understand your responsibility to request accommodations."),
        help_text = _("If you have a disability and/or a condition for which you would like special accommodations for instruction or testing it is your responsibility to notify the program’s administrative office and provide professional documentation.")
    )
    rural_area = models.BooleanField(
        default=False,
        verbose_name=_("Do you live in a rural area?")
    )
    displaced_homemaker = models.BooleanField(
        default=False,
        verbose_name=_("I am a former homemaker who is having trouble finding a job or a better job.")
    )
    dislocated_worker = models.BooleanField(
        default=False,
        verbose_name=_("Are you a dislocated worker?")
    )
    cult_barriers_hind_emp = models.BooleanField(
        default=False,
        verbose_name=_(
            "Are there cultural barriers hindering your employment?"
        )
    )
    foster_care = models.BooleanField(
        default = False,
        verbose_name = _("I am in the foster care system (or used to be) and I am less than 24 years old.")
    )
    lacks_adequate_residence = models.BooleanField(
        default=False,
        verbose_name = _("I am homeless. I live in a motel, hotel, campground, transitional housing, or with another person because I lost my house or apartment")
    )
    in_foster_care = models.BooleanField(
        default=False,
        verbose_name=_("Are you currently in foster care?")
    )
    aged_out_foster_care = models.BooleanField(
        default=False,
        verbose_name=_(
            "Have you aged out of foster care?"
        )
    )
    exhaust_tanf = models.BooleanField(
        default=False,
        verbose_name=_(
            "Are you receiving TANF assistance that ends within 2 years?"
        )
    )
    job_corps = models.CharField(
        max_length=1,
        choices=YES_NO_UNKNOWN,
        blank=True,
        default=2,
        verbose_name=_("Are you in Job Corps?")
    )
    youth_build = models.CharField(
        max_length=1,
        choices=YES_NO_UNKNOWN,
        blank=True,
        default=2,
        verbose_name=_("Are you in a Youth Build program?")
    )

    # Tick Checkboxes
    # A
    recieves_public_assistance = models.BooleanField(
        default=False,
        verbose_name=_("Do you receive public assistance?")
    )
    # B
    low_family_income = models.BooleanField(
        default=False,
    )
    # D
    state_payed_foster = models.BooleanField(
        default=False,
    )
    # E
    disabled_in_poverty = models.BooleanField(
        default=False,
    )
    # G
    youth_in_high_poverty_area = models.BooleanField(
        default=False,
    )

    # Ex Offender
    # A
    subject_of_criminal_justice = models.BooleanField(
        default=False,
    )
    # B
    arrest_record_employment_barrier = models.BooleanField(
        default=False,
    )

    # Homeless Individual
    # A
    # B
    irregular_sleep_accomodation = models.BooleanField(
        default=False,
    )
    # C
    migratory_child = models.BooleanField(
        default=False,
    )
    # D
    runaway_youth = models.BooleanField(
        default=False,
    )
    # Adult
    adult_one_stop = models.CharField(
        max_length=1,
        choices=ONE_STOP_CHOICES,
        default="4"
    )
    # Youth
    youth_one_stop = models.CharField(
        max_length=1,
        choices=ONE_STOP_CHOICES,
        default="4"
    )
    # Vocational Rehab
    voc_rehab = models.CharField(
        max_length=1,
        choices=VOCATIONAL_REHAB_CHOICES,
        default="4"
    )
    # Wagner Peyser Act
    wagner_peyser = models.CharField(
        max_length=1,
        choices=YES_NO_UNKNOWN,
        default="3"
    )
    # School Status at Participation
    school_status = models.CharField(
        max_length=1,
        choices=SCHOOL_STATUS_CHOICES,
        default="4",
        blank=True
    )
    recieved_training = models.CharField(
        max_length=1,
        choices=YES_NO,
        default="2")
    # Eligible Training Provider
    etp_name = models.CharField(
        max_length=30,
        blank=True
    )
    etp_program = models.CharField(
        max_length=2,
        blank=True,
        choices=PROGRAM_OF_STUDY_CHOICES,
    )
    etp_CIP_Code = models.CharField(
        max_length=20,
        blank=True
    )
    training_type_1 = models.CharField(
        max_length=2,
        blank=True,
        choices=TRAINING_TYPE_CHOICES
    )
    training_type_2 = models.CharField(
        max_length=2,
        blank=True,
        choices=TRAINING_TYPE_CHOICES
    )
    training_type_3 = models.CharField(
        max_length=2,
        blank=True,
        choices=TRAINING_TYPE_CHOICES
    )
    # Disability Details
    # Disability

    # ADHD
    adhd = models.BooleanField(
        default=False,
        verbose_name=_("ADHD")
    )
    # Autism
    autism = models.BooleanField(
        default=False,
        verbose_name=_("Autism")
    )
    # Deaf-blindness
    deaf_blind = models.BooleanField(
        default=False,
        verbose_name=_("Deaf-blindness")
    )
    # Deafness
    deaf = models.BooleanField(
        default=False,
        verbose_name=_("Deafness")
    )
    # Emotional Disturbance
    emotional_disturbance = models.BooleanField(
        default=False,
        verbose_name=_("Emotional Disturbance")
    )
    # Had an IEP in K-12
    k12_iep = models.BooleanField(
        default=False,
        verbose_name=_("Had an IEP in K-12")
    )
    # Hard of Hearing
    hard_of_hearing = models.BooleanField(
        default=False,
        verbose_name=_("Hard of Hearing")
    )
    # Intellectual Disability
    intellectual_disability = models.BooleanField(
        default=False,
        verbose_name=_("Intellectual Disability")
    )
    # Multiple Disabilities
    multiple_disabilities = models.BooleanField(
        default=False,
        verbose_name=_("Multiple Disabilities")
    )
    # Orthopedic Impairment
    orthopedic_impairment = models.BooleanField(
        default=False,
        verbose_name=_("Orthopedic Impairment")
    )
    # Other Health Impairment
    other_health_impairment = models.BooleanField(
        default=False,
        verbose_name=_("Other Health Impairment")
    )
    # Specific Learning Disability
    learning_disability = models.BooleanField(
        default=False,
        verbose_name=_("Specific Learning Disability")
    )
    # Speech or Language Impairment
    speech_or_lang_impairment = models.BooleanField(
        default=False,
        verbose_name=_("Speech or Language Impairment")
    )
    # Traumatic Brain Injury
    traumatic_brain_injury = models.BooleanField(
        default=False,
        verbose_name=_("Traumatic Brain Injury")
    )
    # Visual Impairment
    visual_impairment = models.BooleanField(
        default=False,
        verbose_name=_("Visual Impairment")
    )

    # Learning Disabled

    # Dyscalculia
    dyscalculia = models.BooleanField(
        default=False,
        verbose_name=_("Dyscalculia")
    )
    # Dysgraphia
    dysgraphia = models.BooleanField(
        default=False,
        verbose_name=_("Dysgraphia")
    )
    # Dyslexia
    dyslexia = models.BooleanField(
        default=False,
        verbose_name=_("Dyslexia")
    )
    # Related to Neurological Impairments
    neurological_impairments = models.BooleanField(
        default=False,
        verbose_name=_("Related to Neurological Impairments")
    )
    highest_level_completed = models.CharField(
        max_length=2,
        choices=HIGHEST_COMPLETED_CHOICES,
        default="1",
    )
    highet_level_at_entry = models.CharField(
        max_length=2,
        choices=COMPLETED_AT_ENTRY_CHOICES,
        default="0"
    )
    school_location = models.CharField(
        max_length=1,
        choices=SCHOOL_LOCATION_CHOICES,
        default="1"
    )

    state_id_checked = models.BooleanField(
        default=False
    )

    class Meta:
        verbose_name_plural = "WIOA records"

    def __str__(self):
        return self.student.__str__()

    def wru_search(self, session, search_dict):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36'
        }

        s = session.post(
            'https://workreadyu.lctcs.edu/Student/',
            data=search_dict,
            headers=headers,
            proxies=settings.PROXIE_DICT
        )
        p = bs4.BeautifulSoup(
            s.text,
            "html.parser"
        )
        try:
            return p.select("table.Webgrid > tbody > tr > td")[9].text.encode('utf-8')
        except IndexError:
            return 'No ID'

    def check_for_state_id(self, session):
        search = {
            'LastNameTextBox': self.student.last_name,
            'FirstNameTextBox': self.student.first_name,
            'SSNTextBox': '',
            'SIDTextBox': '',
            'Status': -1,
            'ProviderId': 9,
            'ParishId': 0,
            'AgeSearchType': 1,
            'AgeFromInequality': 4,
            'AgeFromTextBox': get_age_at_intake(self.student.dob, self.student.intake_date),
            'btnFilter': 'Filter List'
        }
        wru = self.wru_search(session, search)
        if wru == 'No ID':
            if self.SID:
                search = {
                    'SSNTextBox': get_SID(self.SID),
                    'Status': -1,
                    'btnFilter': 'Filter List'
                }
                wru = self.wru_search(session, search)
        if wru != 'No ID':
            wru = b'x' + wru
            wru = wru.decode('ascii')
        self.state_id_checked = True
        self.save()
        self.student.WRU_ID = wru
        self.student.save()

    def prepare_student(self):

            student = {
                "hdnRoleType": "2",
                "FY": "12",
                "lblCurrentFY": "12",
                "FYBginDate": "7/1/2023 12:00:00 AM",
                "FYEndDate": "6/30/2024 12:00:00 AM",
                "hdnProviderId": "DELGADO COMMUNITY COLLEGE",
                "hdnInactiveStateKey": ",2,3,4,5,7,18",
                "hdnInactiveProg": "2,5,7,13,",
                "hdnInactiveEmpStat": ",4_UNL, 5_NLF,",
                "IntakeOnlyProgram": "19",
                "EnrollPStat.IntakeDate": datetime.strftime(self.student.intake_date, "%m/%d/%Y"),
                "FirstName": self.student.first_name,
                "MiddleInitial": "",
                "LastName": self.student.last_name,
                "Suffix": title(self.student.title),
                "Suffixes": "",
                "Pronouns": pronouns(self.student.pronoun)[0],
                "OtherPronouns": pronouns(self.student.pronoun)[1],
                "Address.Street1": self.student.street_address_1[:50],
                "Address.Street2": self.student.street_address_2[:50],
                "Address.City": self.student.city,
                "Address.OtherCity": self.student.other_city,
                "Address.StateId": state(self.student.state),
                "Address.Zip": self.student.zip_code,
                "Address.VTCountyId": self.student.parish,
                "Email.Email1": self.student.email,
                "Telephone.PrimaryPhoneNumber": self.student.phone,
                "Telephone.PrimaryPhoneStatus": "true",
                "Telephone.AllowTexts": true_false(self.student.allow_texts),
                "Telephone.AlternativePhoneNumber1": "",
                "Emergency.FirstName": ec_name(self.student.emergency_contact)[0],
                "Emergency.LastName": ec_name(self.student.emergency_contact)[1],
                "Emergency.RelationshipId": ec_relation(self.student.ec_relation),
                "Emergency.Telephone1": self.student.ec_phone,
                "StudentId": "0",
                "SSN": get_SID(self.SID),
                "OtherID": "",
                "USCitizen": citizen(self.student.US_citizen),
                "DateOfBirth": datetime.strftime(self.student.dob, "%m/%d/%Y"),
                "Age": get_age_at_intake(self.student.dob, self.student.intake_date),
                "Gender": gender(self.student.gender),
                "MaritalStatusId": marital(self.student.marital_status),
                "Ethnicity_1": true_false(self.amer_indian),
                "Ethnicity_2": true_false(self.asian),
                "Ethnicity_3": true_false(self.black),
                "Ethnicity_5": true_false(self.white),
                "Ethnicity_4": true_false(self.pacific_islander),
                "Ethnicity_8": 'false',
                "HispanicLatino": hl_tf(self.hispanic_latino),
                "StudentWIOADetail.ParentalStatus": self.parental_status,
                "Program.NativeLanguage": self.native_language,
                "Program.OtherNativeLanguage": self.other_language,
                "CountryOfBirth":  self.country,
                "OtherCountryOfBirth": self.other_country,
                "StudentWIOADetail.Veteran": true_false(self.veteran),
                "Program.ProgramTypeId": "19",
                "HighestId": self.highest_level_completed,
                "HighLocId": self.school_location,
                "StudentWIOADetail.HighestSchCompletedEntry": self.highet_level_at_entry,
                "Disability_12": true_false(self.adhd),
                "Disability_13": true_false(self.autism),
                "Disability_9": true_false(self.deaf_blind),
                "Disability_3": true_false(self.deaf),
                "Disability_6": true_false(self.emotional_disturbance),
                "Disability_15": true_false(self.k12_iep),
                "Disability_2": true_false(self.hard_of_hearing),
                "Disability_1": true_false(self.intellectual_disability),
                "Disability_10": true_false(self.multiple_disabilities),
                "Disability_7": true_false(self.orthopedic_impairment),
                "Disability_8": true_false(self.other_health_impairment),
                "Disability_11": true_false(self.learning_disability),
                "Disability_4": true_false(self.speech_or_lang_impairment),
                "Disability_14": true_false(self.traumatic_brain_injury),
                "Disability_5": true_false(self.visual_impairment),
                "Dislearning_4": true_false(self.dyscalculia),
                "Dislearning_3": true_false(self.dysgraphia),
                "Dislearning_2": true_false(self.dyslexia),
                "Dislearning_1": true_false(self.neurological_impairments),
                "SpecLearningDisId": "11",
                "Program.PastEnrollment": true_false(self.student.prior_registration),
                "EmploymentStatusId": employment_status(self.current_employment_status),
                "EnrollPStat.FullTimeEmployed": full_time(self.current_employment_status),
                "EnrollPStat.NotInLaborForce": labor_force(self.current_employment_status),
                "EnrollPStat.NotWorkingButLookingForWork": looking_for_work(self.current_employment_status),
                "EnrollPStat.MoreThan6MonthsUnemployed": self.long_term_unemployed,
                "EnrollPStat.CurrentIndustry": self.current_industry,
                "EnrollPStat.IndustryPreference": self.industry_preference,
                "EnrollPStat.EmploymentLocation": self.employer,
                "EnrollPStat.Occupation": self.occupation,
                "StudentWIOADetail.TANF": true_false(self.TANF),
                "StudentWIOADetail.ReceivedTANFMoreThan2Yrs": self.TANF_2,
                "StudentWIOADetail.SNAP": true_false(self.SNAP),
                "StudentWIOADetail.SSI": true_false(self.SSI),
                "StudentWIOADetail.TState": true_false(self.Tstate),
                "StudentWIOADetail.NNRecievedAssistance": recieved_assistance(self),
                "EnrollSStat.AnnualIncome": self.household_income,
                "EnrollSStat.NoOfFamilyMembers": self.household_size,
                "EnrollSStat.LowHouseholdIncome": true_false(low_income(self)),
                "EnrollSStat.LowIncome": true_false(low_income(self)),
                "EnrollSStat.DisplayedHomemaker": true_false(self.displaced_homemaker),
                "EnrollSStat.SingleParent": true_false(self.single_parent),
                "StudentWIOADetail.NNLacksFixedNighttimeResidence": true_false(self.lacks_adequate_residence),
                "StudentWIOADetail.CriminalRecordHardToFindJob": true_false(self.criminal_record),
                "StudentWIOADetail.NNFostercareYouth": true_false(self.in_foster_care),
                "StudentWIOADetail.MigrantAndSeasonalFarmworker": migrant(self.migrant_seasonal_status),
                "chkFarmworker": check_farm(self),
                "chkNoneOfThese": check_statements(self),
                "StudentWIOADetail.PrimaryGoal": self.student.primary_goal,
                "chkPreferences_1": true_false(self.student.check_goal_1),
                "chkPreferences_2": true_false(self.student.check_goal_2),
                "chkPreferences_3": true_false(self.student.check_goal_3),
                "chkPreferences_4": true_false(self.student.check_goal_4),
                "chkPreferences_5": true_false(self.student.check_goal_5),
                "chkPreferences_6": true_false(self.student.check_goal_6),
                "chkPreferences_7": true_false(self.student.check_goal_7),
                "chkPreferences_8": true_false(self.student.check_goal_8),
                "chkPreferences_9": true_false(self.student.check_goal_9),
                "GoalId": '5',
                "StudentWIOADetail.HelpWithSchoolWork": true_false(self.help_with_schoolwork),
                "StudentWIOADetail.StudentTeacherContact": true_false(self.student_teacher_contact),
                "StudentWIOADetail.ParentVolunteering": true_false(self.parent_volunteering),
                "StudentWIOADetail.ReadToChildren": true_false(self.read_to_children),
                "StudentWIOADetail.VisitLibrary": true_false(self.visit_library),
                "StudentWIOADetail.PurchasingBooks": true_false(self.purchase_books),
                "chkClassInterest_1": true_false(self.student.on_campus),
                "chkClassInterest_2": true_false(self.student.online_solo),
                "chkClassInterest_3": true_false(self.student.online_cohort),
                "chkClassInterest_4": true_false(self.student.hybrid),
                "chkTimePreference_1": true_false(self.student.morning),
                "chkTimePreference_2": true_false(self.student.afternoon),
                "chkTimePreference_3": true_false(self.student.evening),
                "chkTimePreference_4": true_false(self.student.weekend),
                "StudentWIOADetail.ComputerAccess": self.student.computer_access,
                "StudentWIOADetail.InternetAccess": self.student.internet_access,
                "StudentWIOADetail.ReferredBy": self.referred_by,
                "SignaturePath": self.digital_signature,
                "StudentWIOADetail.Disability": self.disability_notice,
                "StudentWIOADetail.RequestAccommodation": true_false(self.request_accommodation),
                "btnSave": "Submit",
                "alertTextBox": ""
            }
            return student

    def send_to_state(self, session):
        if self.state_id_checked:
            student = self.prepare_student()
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36'
            }
            return session.post(
                'https://workreadyu.lctcs.edu/Student/CreateWithWIOAStepWise/CreateLink',
                files={k: (None, v) for k,v in student.items()},
                headers=headers,
                proxies=settings.PROXIE_DICT
            )

    def verify(self, session):
        search = {
            'LastNameTextBox': self.student.last_name,
            'FirstNameTextBox': self.student.first_name,
            'FromTextBox': self.student.intake_date,
            'btnFilter': 'Filter List'
        }
        wru = self.wru_search(session, search)
        try:
            wru = wru.decode('ascii')
        except AttributeError:
            pass
        self.student.WRU_ID = wru
        self.student.save()
        self.student.testify()
        self.student.track()

    def send(self, session):
        self.check_for_state_id(session)
        if self.student.WRU_ID == 'No ID':
            self.send_to_state(session)
            self.verify(session)
        elif 'x' in self.student.WRU_ID:
            merge_duplicates(self.student.WRU_ID)


class CollegeInterest(models.Model):

    YES_NO_MAYBE = (
        ('Y', 'Yes'),
        ('N', 'No'),
        ('C', "I don't know")
    )

    GED_HISET_CHOICES = (
        ('1', 'Yes, high school diploma'),
        ('2', 'Yes, high school equivalency'),
        ('3', 'No')
    )

    DEFAULT = 'D'
    REPAYMENT = 'R'
    PAID = 'P'
    OTHER = 'O'
    UNKNOWN = 'U'
    AID_STATUS_CHOICES = (
        (DEFAULT, 'Default'),
        (REPAYMENT, 'Repayment'),
        (PAID, 'Paid in full'),
        (UNKNOWN, "I don't know"),
        (OTHER, 'Other')
    )

    FULL_TIME = 'F'
    PART_TIME = 'P'
    LOOKING = 'L'
    NOT_LOOKING = 'N'
    EMPLOYMENT_STATUS_CHOICES = (
        (FULL_TIME, "Yes, I’m employed full-time (more than 30 hours per week)."),
        (PART_TIME, "Yes, I’m employed part-time (less than 30 hours per week)."),
        (LOOKING, "No, but I’m looking for work."),
        (NOT_LOOKING, "No, and I’m not looking for work right now.")

    )

    student = models.OneToOneField(
        Student,
        models.CASCADE,
        related_name='college_interest'
    )

    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        models.PROTECT,
        related_name='college_interest_records'
    )

    ged_hiset = models.CharField(
        max_length=1,
        choices=GED_HISET_CHOICES,
        verbose_name=_('Do you have your high school diploma or high school equivalency (GED/HiSET)?')
    )

    current_adult_ed = models.BooleanField(
        default=True,
        verbose_name=_('Check this box if you are currently attending adult education classes')
    )

    adult_ed_location = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('Where?')
    )

    bpcc = models.BooleanField(
        default=False,
        verbose_name=_('Bossier Parish Community College (BPCC)')
    )

    brcc = models.BooleanField(
        default=False,
        verbose_name=_('Baton Rouge Community College (BRCC)')
    )

    ctcc = models.BooleanField(
        default=False,
        verbose_name=_('Central Louisiana Technical Community College (CTCC)')
    )

    dcc = models.BooleanField(
        default=False,
        verbose_name=_('Delgado Community College')
    )

    ldcc = models.BooleanField(
        default=False,
        verbose_name=_('Louisiana Delta Community College')
    )

    ftcc = models.BooleanField(
        default=False,
        verbose_name=_('Fletcher Technical Community College')
    )

    ntcc = models.BooleanField(
        default=False,
        verbose_name=_('Northshore Technical Community College')
    )

    ncc = models.BooleanField(
        default=False,
        verbose_name=_('Nunez Community College')
    )

    nltc = models.BooleanField(
        default=False,
        verbose_name=_('Northwest Louisiana Technical College')
    )

    rpcc = models.BooleanField(
        default=False,
        verbose_name=_('River Parishes Community College (RPCC)')
    )

    scl = models.BooleanField(
        default=False,
        verbose_name=_('South Central Louisiana Technical College (SCL)')
    )

    slcc = models.BooleanField(
        default=False,
        verbose_name=_('South Louisiana Community College')
    )

    sowela = models.BooleanField(
        default=False,
        verbose_name=_('Southwest Louisiana Technical Community College (SOWELA)')
    )

    lola = models.CharField(
        max_length=15,
        blank=True,
        verbose_name=_('Do you know your LOLA number?')
    )

    other_college = models.BooleanField(
        default=False,
        verbose_name=_('Have you ever attended college before (anywhere)?')
    )

    other_college_location = models.CharField(
        max_length=30,
        blank=True,
        verbose_name=_('Where was that?')
    )

    other_college_name = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('Did you enroll under a different name than the one you gave us?')
    )

    prev_balance = models.CharField(
        max_length=1,
        choices=YES_NO_MAYBE,
        blank=True,
        verbose_name=_("If you've attended college before, do you owe a balance to that college?")
    )

    financial_aid = models.CharField(
        max_length=1,
        choices=YES_NO_MAYBE,
        blank=True,
        verbose_name=_('Have you ever used financial aid (student loans or grants) before?')
    )

    aid_status = models.CharField(
        max_length=1,
        choices=AID_STATUS_CHOICES,
        blank=True,
        verbose_name=_('If you have used financial aid before, what is your current financial aid status?')
    )

    nslds_notes = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('NLDS notes from ACE Staff:')
    )

    fafsa1617 = models.BooleanField(
        default=False,
        verbose_name='2016-2017'
    )
    fafsa1718 = models.BooleanField(
        default=False,
        verbose_name='2017-2018'
    )
    fafsa1819 = models.BooleanField(
        default=False,
        verbose_name='2018-2019'
    )

    delgado_classes = models.CharField(
        max_length=400,
        blank=True,
        verbose_name=_(
            "If you've taken college classes at Delgado,"
            " please list the classes you took and when,"
            " to the best of your knowledge."
            )
    )

    workforce_training = models.BooleanField(
        default=False,
        verbose_name=_('Have you ever take any workforce training classes?')
    )

    workforce_training_desc = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('What kind of workforce training classes?')
    )

    serv_safe = models.BooleanField(
        default=False,
        verbose_name="ServSafe Manager's Level Certification"
    )

    nccer = models.BooleanField(
        default=False,
        verbose_name='NCCER Core Certification'
    )

    ic3 = models.BooleanField(
        default=False,
        verbose_name='Internet and Computing Core (IC3) Certification'
    )

    first_aid = models.BooleanField(
        default=False,
        verbose_name='First Aid'
    )

    cpr = models.BooleanField(
        default=False,
        verbose_name='CPR'
    )

    employment_status = models.CharField(
        max_length=1,
        choices=EMPLOYMENT_STATUS_CHOICES,
        verbose_name=_('Are you currently employed?')
    )

    work_schedule = models.CharField(
        max_length=400,
        blank=True,
        verbose_name=_('What is your usual work schedule like?')
    )

    career_goals = models.CharField(
        max_length=2000,
        blank=True,
        verbose_name=_('What kind of career would you like to have when you finish school?')
    )

    notes = models.CharField(
        max_length=2000,
        blank=True
    )

    class Meta:
        verbose_name_plural = "College Interest Records"

    def __str__(self):
        return " | ".join([self.student.WRU_ID, self.student.__str__()])

    def get_absolute_url(self):
        return reverse('people:college interest detail', kwargs={'slug': self.student.slug})


class PoP(models.Model):

    student = models.ForeignKey(
        Student,
        models.CASCADE,
        related_name='pop'
    )

    start_date = models.DateField(
        verbose_name='Start Date'
    )

    last_service_date = models.DateField(
        verbose_name='Date of last service',
    )

    active = models.BooleanField(
        default=True
    )

    made_gain = models.BooleanField(
        default=False
    )

    pretest_date = models.DateField(
        null=True
    )

    pretest_type = models.CharField(
        max_length=20,
        blank=True
    )

    class Meta:
        verbose_name = "Period of Participation"
        verbose_name_plural = "Periods of Participation"
        unique_together = ['student', 'start_date']
        ordering = ['-start_date', 'student']
        get_latest_by = 'last_service_date'

    def total_hours(self):
        return self.student.total_hours(from_date=self.start_date, to_date=self.last_service_date)

    def __str__(self):
        period = " - ".join([self.start_date.strftime('%m/%d/%Y'), self.last_service_date.strftime('%m/%d/%Y')])
        return " | ".join([self.student.__str__(), period])


class Prospect(models.Model):

    CONTACT_CHOICES = (
        ('Call', 'Call'),
        ('Text', 'Text'),
        ('Email', 'Email'),
    )

    LANGUAGE_CHOICES = (
        ("english", "English"),
        ("spanish", "Spanish"),
        ("vietnamese", "Vietnamese"),
        ("arabic", "Arabic"),
        ("chinese", "Chinese"),
        ("french", "French"),
        ("korean", "Korean"),
        ("japanese", "Japanese"),
        ("creole", "Creole"),
        ("portugese", "Portugese"),
        ("turkish", "Turkish"),
        ("russian", "Russian"),
        ("other", "Other")
    )

    CONTACT_TIME_CHOICES = (
        ("M", "8am - 12pm"),
        ("A", "12pm - 4pm"),
        ("E", "4pm - 8pm")
    )

    student = models.ForeignKey(
        Student,
        models.PROTECT,
        related_name='prospects',
        null=True,
        blank=True
    )

    advisor = models.ForeignKey(
        Staff,
        models.PROTECT,
        related_name='prospects',
        null=True,
        blank=True
    )

    registration_date = models.DateField(
        default=timezone.now
    )

    first_name = models.CharField(
        max_length=50,
        verbose_name=_("First Name"),
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name=_("Last Name"),
    )
    email = models.EmailField(
        max_length=80,
        verbose_name=_("Email Address"),
        blank=True
    )
    phone = models.CharField(
        max_length=20,
        verbose_name=_("Phone Number"),
    )
    dob = models.DateField(
        verbose_name=_("Date of Birth")
    )
    contact_preference = models.CharField(
        max_length=5,
        choices=CONTACT_CHOICES,
        verbose_name=_('How do you prefer to be contacted?')
    )
    contact_time = models.CharField(
        max_length=1,
        choices=CONTACT_TIME_CHOICES,
        verbose_name=_('What time do you prefer to be contacted?'),
        blank=True
    )
    primary_language = models.CharField(
        max_length=20,
        choices=LANGUAGE_CHOICES,
        blank=True,
        verbose_name=_("Primary Language")
    )

    active = models.BooleanField(
        default=True
    )

    duplicate = models.BooleanField(
        default=False,
        verbose_name=_("Probable Duplicate")
    )

    returning_student = models.BooleanField(
        default=False,
        verbose_name=_("Probable Returning Student")
    )

    for_credit = models.BooleanField(
        default=False,
        verbose_name=_("For-credit Student")
    )
    
    slug = models.CharField(
        default=make_prospect_slug,
        max_length=5
    )

    advisor_assigned_date = models.DateTimeField(
        null=True,
        blank=True
    )

    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return '{0} {1}'.format(self.first_name, self.last_name)

    def get_absolute_url(self):
        return reverse('people:prospect detail', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        super(Prospect, self).save(*args, **kwargs)
        if self.advisor is not None and self.advisor_assigned_date is None:
            self.advisor_assigned_date = timezone.now()
            self.save()

    @property
    def status(self):
        if self.duplicate:
            return "Probable Duplicate"
        if self.for_credit:
            return "For Credit"
        if self.active:
            if self.student is None:
                if self.returning_student:
                    return "Probable Returner"
                else:
                    return "Unregistered"
            else:
                return "Registered"
        else:
            if self.student is None:
                return "Inactive"
            else:
                return "Closed"

    @property
    def folder(self):
        if self.student is not None:
            if self.student.folder == 'C':
                return "Complete"
            else:
                return "Incomplete"
        else:
            return "--"

    @property
    def orientation(self):
        if self.student is not None:
            if self.student.orientation =='C' or self.student.intake_quiz:
                return "Complete"
            else:
                return "Incomplete"
        else:
            return "--"

    @property
    def paperwork(self):
        if self.student is not None:
            if self.student.paperwork == 'C' or self.student.intake_form:
                return "Complete"
            else:
                return "Incomplete"
        else:
            return "--"

    @property
    def testing(self):
        if self.student is not None:
            try: 
                self.student.tests
                if self.student.tests.last_test_date is not None:
                    return datetime.strftime(
                        self.student.tests.last_test_date, "%m-%d-%y"
                    )
                else:
                    return "No Tests"
            except ObjectDoesNotExist:
                return "No Test History"
        else:
            return "--"

    @property
    def last_contact(self):
        if self.notes.exists():
            return datetime.strftime(
                self.notes.latest('contact_date').contact_date, "%m-%d-%y"
            )
        else:
            return "No Notes"

    @property
    def num_contacts(self):
        num = self.notes.count() if self.notes.exists() else 0
        return num


class ProspectNote(models.Model):

    CONTACT_CHOICES = (
        ('Call', 'Call'),
        ('Text', 'Text'),
        ('Email', 'Email'),
        ('In Person', 'In Person')
    )

    prospect = models.ForeignKey(
        Prospect,
        models.PROTECT,
        related_name="notes"
    )

    contact_date =  models.DateField()

    contact_method = models.CharField(
        max_length=10,
        choices=CONTACT_CHOICES,
    )

    successful = models.BooleanField(
        default=False
    )

    returning_student = models.BooleanField(
        default=False,
        verbose_name=_("Returning Student")
    )

    notes = models.TextField()

    class Meta: 
        ordering = ['contact_date', 'prospect']

    def __str__(self):
        return '{0} {1}ed {2}| {3}'.format(
            self.prospect.advisor,
            self.contact_method,
            self.prospect,
            self.contact_date
        )

    def get_absolute_url(self):
        return reverse('people:prospect note detail', kwargs={'pk': self.pk})
