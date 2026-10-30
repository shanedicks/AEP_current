"""remove_TA_task: Classroom is the source of truth for which courses each TA is on.

The Classroom service is a MagicMock; courses().list() pages are keyed by TA so
each test controls exactly what Classroom reports.
"""
import datetime
from unittest.mock import MagicMock

import pytest
from django.utils import timezone

import sections.tasks
from sections.models import Section
from sections.tasks import program_ta, remove_TA_task
from tests.factories import SectionFactory, SemesterFactory

pytestmark = pytest.mark.django_db

ESL_TA = program_ta['ELL']
CCR_TA = program_ta['CCR']


def fake_service(pages_by_ta):
    """pages_by_ta: {ta: [[course_id, ...], [course_id, ...]]} -- one inner list per page."""
    service = MagicMock()

    def list_courses(teacherId, pageSize, pageToken):
        pages = pages_by_ta.get(teacherId, [[]])
        index = int(pageToken) if pageToken else 0
        response = {'courses': [{'id': cid} for cid in pages[index]]}
        if index + 1 < len(pages):
            response['nextPageToken'] = str(index + 1)
        request = MagicMock()
        request.execute.return_value = response
        return request

    service.courses.return_value.list.side_effect = list_courses
    return service


@pytest.fixture
def service(monkeypatch):
    holder = {}

    def install(pages_by_ta):
        holder['service'] = fake_service(pages_by_ta)
        monkeypatch.setattr(sections.tasks, 'classroom_service', lambda: holder['service'])
        return holder['service']

    return install


def deleted(service):
    return {
        (c.kwargs['courseId'], c.kwargs['id'])
        for c in service.courses.return_value.teachers.return_value.delete.call_args_list
    }


def old_section(g_suite_id, program=Section.ESL, days_ago=6 * 365):
    end = timezone.now().date() - datetime.timedelta(days=days_ago)
    semester = SemesterFactory(
        title=f'Semester ending {end}',
        start_date=end - datetime.timedelta(days=90),
        end_date=end,
    )
    return SectionFactory(semester=semester, program=program, g_suite_id=g_suite_id)


class TestRemoveTATask:

    def test_follows_pagination_to_last_page(self, service):
        old_section('a')
        old_section('b')
        old_section('c')
        svc = service({ESL_TA: [['a'], ['b'], ['c']]})
        counts = remove_TA_task()
        assert counts[ESL_TA] == {'courses': 3, 'to_remove': 3}
        assert deleted(svc) == {('a', ESL_TA), ('b', ESL_TA), ('c', ESL_TA)}

    def test_cutoff_boundary(self, service):
        old_section('past', days_ago=5 * 365 + 1)
        old_section('on_cutoff', days_ago=5 * 365)
        old_section('recent', days_ago=365)
        svc = service({ESL_TA: [['past', 'on_cutoff', 'recent']]})
        remove_TA_task()
        assert deleted(svc) == {('past', ESL_TA)}

    def test_only_removes_ta_from_courses_classroom_reports(self, service):
        old_section('still_on')
        old_section('already_removed')
        svc = service({ESL_TA: [['still_on']]})
        remove_TA_task()
        assert deleted(svc) == {('still_on', ESL_TA)}

    def test_each_ta_removed_only_from_its_own_courses(self, service):
        old_section('esl', program=Section.ESL)
        old_section('ccr', program=Section.CCR)
        svc = service({ESL_TA: [['esl']], CCR_TA: [['ccr']]})
        remove_TA_task()
        assert deleted(svc) == {('esl', ESL_TA), ('ccr', CCR_TA)}

    def test_every_program_ta_is_queried(self, service):
        svc = service({})
        remove_TA_task()
        queried = {c.kwargs['teacherId'] for c in svc.courses.return_value.list.call_args_list}
        assert queried == set(program_ta.values())

    def test_dry_run_counts_without_deleting(self, service):
        old_section('a')
        svc = service({ESL_TA: [['a', 'unlinked']]})
        counts = remove_TA_task(dry_run=True)
        assert counts[ESL_TA] == {'courses': 2, 'to_remove': 1}
        assert deleted(svc) == set()

    def test_http_error_is_logged_and_skipped(self, service):
        from googleapiclient.errors import HttpError
        old_section('bad')
        old_section('good')
        svc = service({ESL_TA: [['bad', 'good']]})
        delete = svc.courses.return_value.teachers.return_value.delete

        def delete_side_effect(courseId, id):
            request = MagicMock()
            if courseId == 'bad':
                request.execute.side_effect = HttpError(MagicMock(status=404), b'not found')
            return request

        delete.side_effect = delete_side_effect
        remove_TA_task()
        assert deleted(svc) == {('bad', ESL_TA), ('good', ESL_TA)}
