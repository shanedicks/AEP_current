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

has_pretest = has_tabe | has_clas_e

@rules.predicate
def test_within_six_months(student):
    try:
        tests = student.tests
    except ObjectDoesNotExist:
        return False
    if student.tests.last_test_date == None:
        return False
    else:
        target = timezone.now().date() - timedelta(days=180)    
        return student.tests.last_test_date > target

has_current_pretest = has_pretest & test_within_six_months

needs_pretest = ~has_current_pretest

@rules.predicate
def completed_class_since_last_test(student):
    completed_classes = student.completed_classes().exclude(
        section__program='ADMIN'
    ).exclude(
        section__program='TRANS'
    )
    try:
        last_test_date = student.tests.last_test_date
    except ObjectDoesNotExist:
        return completed_classes.count() > 0
    ccslt = [c for c in completed_classes if c.start_date > last_test_date]
        return len(ccslt) > 0


@rules.predicate
def can_post_test_by_hours(student):
    try:
        tests = student.tests
    except ObjectDoesNotExist:
        return False
    if tests.last_test_type == 'Clas_E'
        return tests.active_hours >= 50
    else:
        return tests.active_hours >= 40

needs_post_test = completed_class_since_last_test | can_post_test_by_hours

has_valid_test_record = has_current_pretest & ~needs_post_test

rules.add_rule('pretested', has_current_pretest)
rules.add_rule('can_enroll', has_valid_test_record)
