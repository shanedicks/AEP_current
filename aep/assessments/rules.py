from datetime import timedelta
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
import rules

# predicates

@rules.predicate
def has_tabe(student):
    try:
        tests = student.tests
    except ObjectDoesNotExist:
        return False
    return student.tests.tabe_tests.count() > 0


@rules.predicate
def has_clas_e(student):
    try:
        tests = student.tests
    except ObjectDoesNotExist:
        return False
    return student.tests.clas_e_tests.count() > 0


@rules.predicate
def has_gain(student):
    try:
        tests = student.tests
    except ObjectDoesNotExist:
        return False
    return student.tests.gain_tests.count() > 0


has_pretest = has_tabe | has_clas_e | has_gain


@rules.predicate
def within_six_months(student):
    try:
        tests = student.tests
    except ObjectDoesNotExist:
        return False
    if student.tests.last_test_date == None:
        return False
    else:
        target = timezone.now().date() - timedelta(days=150)    
        return student.tests.last_test_date > target


has_current_pretest = has_pretest & within_six_months

needs_pretest = ~has_current_pretest


@rules.predicate
def has_completed_classes(student):
    return student.completed_classes().count() > 0


@rules.predicate
def needs_post_test(student):
    classes = student.completed_classes().exclude(
        section__program='ADMIN'
    ).exclude(
        section__program='TRANS'
    )
    return classes.count() > 0


@rules.predicate
def has_post_tested(student):
    last_test = student.tests.last_test_date
    classes = student.completed_classes().exclude(
        section__program='ADMIN'
    ).exclude(
        section__program='TRANS'
    )
    semester_end = classes.latest('section__semester__end_date').section.semester.end_date
    section_end = classes.latest('section__ending').section.ending
    if section_end is not None:
        return last_test_date > section_end
    else:
        return last_test_date > semester_end


has_post_test = ~needs_post_test | has_post_tested

has_valid_test_record = has_current_pretest & has_post_test


rules.add_rule('pretested', has_current_pretest)
rules.add_rule('can_enroll', has_valid_test_record)
