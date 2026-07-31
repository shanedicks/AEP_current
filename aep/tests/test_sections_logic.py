"""Pure date/time logic in sections/models.py -- no database.

Section and Attendance are built unsaved, which keeps these fast and avoids the
Attendance.save() -> pop_update_task cascade.
"""
import datetime

import pytest

from sections.models import Attendance, Enrollment, Section
from semesters.models import Semester


def make_section(**kwargs):
    defaults = {
        'title': 'Test',
        'start_time': datetime.time(9, 0),
        'end_time': datetime.time(11, 0),
    }
    defaults.update(kwargs)
    return Section(**defaults)


class TestSectionDays:

    def test_get_days_returns_tuples_in_week_order(self):
        section = make_section(wednesday=True, monday=True)
        assert section.get_days() == [
            ('monday', 'M', 0),
            ('wednesday', 'W', 2),
        ]

    def test_get_days_empty_when_no_days_set(self):
        assert make_section().get_days() == []

    @pytest.mark.parametrize('flags,expected', [
        ({'monday': True, 'wednesday': True}, 'MW'),
        ({'tuesday': True, 'thursday': True}, 'TR'),
        ({'saturday': True}, 'Sa'),
        ({'sunday': True}, 'Su'),
        ({'saturday': True, 'sunday': True}, 'SaSu'),
        ({}, ''),
    ])
    def test_get_days_str(self, flags, expected):
        assert make_section(**flags).get_days_str() == expected

    @pytest.mark.parametrize('flags,expected', [
        ({'monday': True}, 'Monday'),
        ({'monday': True, 'wednesday': True}, 'Monday and Wednesday'),
        (
            {'monday': True, 'wednesday': True, 'friday': True},
            'Monday, Wednesday and Friday',
        ),
        ({}, ''),
    ])
    def test_get_days_names(self, flags, expected):
        assert make_section(**flags).get_days_names() == expected


class TestSectionClassDates:

    def test_expands_weekly_pattern_across_range(self):
        section = make_section(
            monday=True,
            wednesday=True,
            starting=datetime.date(2026, 1, 5),   # a Monday
            ending=datetime.date(2026, 1, 16),
        )
        assert section.get_class_dates() == [
            datetime.date(2026, 1, 5),
            datetime.date(2026, 1, 7),
            datetime.date(2026, 1, 12),
            datetime.date(2026, 1, 14),
        ]

    def test_range_is_inclusive_of_both_endpoints(self):
        section = make_section(
            monday=True,
            starting=datetime.date(2026, 1, 5),
            ending=datetime.date(2026, 1, 5),
        )
        assert section.get_class_dates() == [datetime.date(2026, 1, 5)]

    def test_no_days_selected_yields_nothing(self):
        section = make_section(
            starting=datetime.date(2026, 1, 5),
            ending=datetime.date(2026, 3, 5),
        )
        assert section.get_class_dates() == []

    def test_falls_back_to_semester_dates(self):
        """starting/ending override the semester; absent, the semester wins."""
        semester = Semester(
            title='S',
            start_date=datetime.date(2026, 1, 5),
            end_date=datetime.date(2026, 1, 9),
        )
        section = make_section(monday=True, friday=True)
        section.semester = semester
        assert section.get_class_dates() == [
            datetime.date(2026, 1, 5),
            datetime.date(2026, 1, 9),
        ]

    def test_section_dates_take_precedence_over_semester(self):
        semester = Semester(
            title='S',
            start_date=datetime.date(2026, 1, 5),
            end_date=datetime.date(2026, 3, 31),
        )
        section = make_section(
            monday=True,
            starting=datetime.date(2026, 1, 12),
            ending=datetime.date(2026, 1, 12),
        )
        section.semester = semester
        assert section.get_class_dates() == [datetime.date(2026, 1, 12)]

    def test_end_before_start_yields_nothing(self):
        section = make_section(
            monday=True,
            starting=datetime.date(2026, 3, 5),
            ending=datetime.date(2026, 1, 5),
        )
        assert section.get_class_dates() == []


class TestAttendanceHours:

    def make(self, **kwargs):
        defaults = {
            'attendance_date': datetime.date(2026, 1, 7),
            'time_in': datetime.time(9, 0),
            'time_out': datetime.time(11, 0),
            'attendance_type': Attendance.PRESENT,
        }
        defaults.update(kwargs)
        return Attendance(**defaults)

    def test_present_computes_from_time_in_and_out(self):
        assert self.make().hours == 2.0

    def test_present_rounds_to_two_places(self):
        att = self.make(time_out=datetime.time(10, 50))
        assert att.hours == 1.83

    @pytest.mark.parametrize('att_type', ['A', 'X', 'C'])
    def test_non_present_is_zero_without_override(self, att_type):
        assert self.make(attendance_type=att_type).hours == 0

    def test_att_hours_override_wins_for_present(self):
        assert self.make(att_hours=1.5).hours == 1.5

    @pytest.mark.parametrize('att_type', ['A', 'X', 'C'])
    def test_att_hours_override_applies_to_non_present_too(self, att_type):
        """Subtle: a non-present record with att_hours set still reports it."""
        att = self.make(attendance_type=att_type, att_hours=3.0)
        assert att.hours == 3.0

    def test_zero_att_hours_override_is_respected_not_recomputed(self):
        """0.0 is not None, so it must win over the time_in/time_out maths."""
        assert self.make(att_hours=0.0).hours == 0.0

    def test_enrolled_hours_uses_section_times_regardless_of_type(self):
        section = make_section(
            start_time=datetime.time(9, 0), end_time=datetime.time(12, 30)
        )
        att = self.make(attendance_type='A')
        att.enrollment = Enrollment(section=section)
        assert att.enrolled_hours == 3.5
