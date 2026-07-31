"""assessments/rules.py -- the testing-eligibility predicates.

These gate who shows as needing a pre-test or post-test, so the boundaries are
pinned exactly. Dates are computed relative to today rather than frozen, because
the predicates call timezone.now() internally.

Two behaviours here are characterised, not endorsed -- see the docstrings on
test_read_nrs_alone_is_not_a_tabe_pretest and
test_180_day_boundary_is_inclusive_here_but_exclusive_in_test_within_six_months.
"""
import datetime

import pytest
from django.utils import timezone

from assessments import rules
from assessments.models import Clas_E, Tabe
from tests import factories

pytestmark = pytest.mark.django_db


def days_ago(n):
    return timezone.now().date() - datetime.timedelta(days=n)


@pytest.fixture
def student():
    return factories.StudentFactory()


@pytest.fixture
def history(student):
    return factories.TestHistoryFactory(student=student)


def add_tabe(history, days, **nrs):
    values = {'read_nrs': '', 'math_nrs': '', 'lang_nrs': ''}
    values.update(nrs)
    return Tabe.objects.create(
        student=history, test_date=days_ago(days), form='11', **values
    )


def add_clas_e(history, days, read_nrs='2'):
    return Clas_E.objects.create(
        student=history, test_date=days_ago(days), form='A', read_nrs=read_nrs
    )


class TestHasTabeAndClasE:

    def test_false_when_student_has_no_test_history(self, student):
        """No TestHistory at all must not raise -- ObjectDoesNotExist is caught."""
        assert rules.has_tabe(student) is False
        assert rules.has_clas_e(student) is False
        assert rules.needs_pretest(student) is True

    def test_false_with_history_but_no_tests(self, student, history):
        assert rules.has_tabe(student) is False
        assert rules.has_clas_e(student) is False

    def test_true_once_a_test_exists(self, student, history):
        add_tabe(history, 10, math_nrs='2')
        assert rules.has_tabe(student) is True
        assert rules.has_clas_e(student) is False


class TestTabePretest:

    @pytest.mark.parametrize('field', ['math_nrs', 'lang_nrs'])
    def test_math_or_lang_nrs_qualifies(self, student, history, field):
        add_tabe(history, 10, **{field: '1'})
        assert rules.has_tabe_pretest(student) is True
        assert rules.needs_pretest(student) is False

    def test_read_nrs_alone_is_not_a_tabe_pretest(self, student, history):
        """has_tabe_pretest filters on math_nrs OR lang_nrs -- read is absent.

        Characterising current behaviour. A student with only a reading NRS
        still reads as needing a pre-test.
        """
        add_tabe(history, 10, read_nrs='4')
        assert rules.has_tabe_pretest(student) is False
        assert rules.needs_pretest(student) is True

    def test_blank_nrs_does_not_qualify(self, student, history):
        add_tabe(history, 10)
        assert rules.has_tabe_pretest(student) is False

    @pytest.mark.parametrize('days,expected', [
        (0, True),
        (179, True),
        (180, True),    # test_date__gte=target, so exactly 180 days counts
        (181, False),
        (365, False),
    ])
    def test_180_day_window(self, student, history, days, expected):
        add_tabe(history, days, math_nrs='2')
        assert rules.has_tabe_pretest(student) is expected

    def test_recent_test_rescues_an_expired_one(self, student, history):
        add_tabe(history, 400, math_nrs='2')
        assert rules.has_tabe_pretest(student) is False
        add_tabe(history, 5, math_nrs='2')
        assert rules.has_tabe_pretest(student) is True


class TestClasEPretest:

    def test_read_nrs_qualifies(self, student, history):
        add_clas_e(history, 10, read_nrs='2')
        assert rules.has_clas_e_pretest(student) is True

    def test_blank_read_nrs_does_not(self, student, history):
        add_clas_e(history, 10, read_nrs='')
        assert rules.has_clas_e_pretest(student) is False

    @pytest.mark.parametrize('days,expected', [
        (179, True), (180, True), (181, False),
    ])
    def test_180_day_window(self, student, history, days, expected):
        add_clas_e(history, days)
        assert rules.has_clas_e_pretest(student) is expected

    def test_either_test_type_satisfies_has_current_pretest(
        self, student, history
    ):
        assert rules.has_current_pretest(student) is False
        add_clas_e(history, 10)
        assert rules.has_current_pretest(student) is True


class TestWithinSixMonths:

    @pytest.mark.parametrize('days,expected', [
        (0, True),
        (179, True),
        (180, False),   # strict >, unlike the __gte used by the pretest rules
        (181, False),
    ])
    def test_boundary(self, student, history, days, expected):
        history.last_test_date = days_ago(days)
        history.save()
        assert rules.test_within_six_months(student) is expected

    def test_false_when_last_test_date_is_null(self, student, history):
        assert history.last_test_date is None
        assert rules.test_within_six_months(student) is False

    def test_180_day_boundary_is_inclusive_here_but_exclusive_in_pretest(
        self, student, history
    ):
        """The two 180-day windows disagree at exactly 180 days.

        has_tabe_pretest uses test_date__gte=target (inclusive);
        test_within_six_months uses last_test_date > target (exclusive).
        Pinned so any attempt to unify them is a deliberate decision.
        """
        add_tabe(history, 180, math_nrs='2')
        history.last_test_date = days_ago(180)
        history.save()
        assert rules.has_tabe_pretest(student) is True
        assert rules.test_within_six_months(student) is False


class TestPostTestByHours:

    @pytest.mark.parametrize('hours,expected', [
        (0, False), (39, False), (39.99, False),
        (40, True), (40.01, True), (100, True),
    ])
    def test_40_hour_threshold(self, student, history, hours, expected):
        history.active_hours = hours
        history.save()
        assert rules.can_post_test_by_hours(student) is expected
        assert rules.needs_post_test(student) is expected

    def test_false_without_test_history(self, student):
        assert rules.can_post_test_by_hours(student) is False


class TestHasValidTestRecord:
    """has_valid_test_record = has_current_pretest & ~needs_post_test."""

    def test_requires_a_current_pretest(self, student, history):
        history.active_hours = 0
        history.save()
        assert rules.has_valid_test_record(student) is False

    def test_true_with_pretest_and_under_40_hours(self, student, history):
        add_tabe(history, 10, math_nrs='2')
        history.active_hours = 39
        history.save()
        assert rules.has_valid_test_record(student) is True

    def test_false_once_40_hours_reached(self, student, history):
        add_tabe(history, 10, math_nrs='2')
        history.active_hours = 40
        history.save()
        assert rules.has_valid_test_record(student) is False

    def test_false_when_pretest_expired_even_under_40_hours(
        self, student, history
    ):
        add_tabe(history, 200, math_nrs='2')
        history.active_hours = 10
        history.save()
        assert rules.has_valid_test_record(student) is False


class TestRegisteredRules:
    """The two names registered with the rules registry."""

    def test_pretested_matches_has_current_pretest(self, student, history):
        import rules as rules_lib
        assert rules_lib.test_rule('pretested', student) is False
        add_tabe(history, 10, math_nrs='2')
        assert rules_lib.test_rule('pretested', student) is True

    def test_can_enroll_matches_has_valid_test_record(self, student, history):
        import rules as rules_lib
        add_tabe(history, 10, math_nrs='2')
        history.active_hours = 5
        history.save()
        assert rules_lib.test_rule('can_enroll', student) is True
        history.active_hours = 50
        history.save()
        assert rules_lib.test_rule('can_enroll', student) is False
