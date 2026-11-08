"""remove_TA_task: Classroom is the source of truth for which courses each TA is on.

The Classroom service is built from the real classroom v1 discovery document, so
method and parameter names are validated exactly as in production. Only the HTTP
layer is faked: FakeClassroomHttp answers courses.list from per-TA pages and
records teachers.delete calls.
"""
import datetime
import json
from urllib.parse import parse_qs, unquote, urlparse

import httplib2
import pytest
from django.utils import timezone
from googleapiclient.discovery import build_from_document
from googleapiclient.discovery_cache import get_static_doc

import sections.tasks
from sections.models import Section
from sections.tasks import program_ta, remove_TA_task
from tests.factories import SectionFactory, SemesterFactory

pytestmark = pytest.mark.django_db

ESL_TA = program_ta['ELL']
CCR_TA = program_ta['CCR']


class FakeClassroomHttp:
    """pages_by_ta: {ta: [[course_id, ...], ...]} -- one inner list per page.
    fail_courses: course ids whose teachers.delete returns 404."""

    def __init__(self, pages_by_ta, fail_courses=()):
        self.pages_by_ta = pages_by_ta
        self.fail_courses = set(fail_courses)
        self.listed_tas = []
        self.deleted = set()

    def request(self, uri, method='GET', body=None, headers=None, **kwargs):
        url = urlparse(uri)
        parts = [unquote(p) for p in url.path.split('/') if p]
        if method == 'GET' and parts == ['v1', 'courses']:
            query = parse_qs(url.query)
            ta = query['teacherId'][0]
            self.listed_tas.append(ta)
            pages = self.pages_by_ta.get(ta, [[]])
            index = int(query.get('pageToken', ['0'])[0])
            payload = {'courses': [{'id': cid} for cid in pages[index]]}
            if index + 1 < len(pages):
                payload['nextPageToken'] = str(index + 1)
            return self._response(200, payload)
        if method == 'DELETE' and len(parts) == 5 and parts[3] == 'teachers':
            course_id, user_id = parts[2], parts[4]
            self.deleted.add((course_id, user_id))
            if course_id in self.fail_courses:
                return self._response(404, {'error': {'code': 404, 'message': 'not found'}})
            return self._response(200, {})
        raise AssertionError(f'unexpected Classroom request: {method} {uri}')

    @staticmethod
    def _response(status, payload):
        return httplib2.Response({'status': str(status)}), json.dumps(payload).encode()


@pytest.fixture
def classroom(monkeypatch):
    def install(pages_by_ta, fail_courses=()):
        http = FakeClassroomHttp(pages_by_ta, fail_courses)
        service = build_from_document(get_static_doc('classroom', 'v1'), http=http)
        monkeypatch.setattr(sections.tasks, 'classroom_service', lambda: service)
        return http

    return install


def old_section(g_suite_id, program=Section.ESL, days_ago=6 * 365):
    end = timezone.now().date() - datetime.timedelta(days=days_ago)
    semester = SemesterFactory(
        title=f'Semester ending {end}',
        start_date=end - datetime.timedelta(days=90),
        end_date=end,
    )
    return SectionFactory(semester=semester, program=program, g_suite_id=g_suite_id)


class TestRemoveTATask:

    def test_follows_pagination_to_last_page(self, classroom):
        old_section('a')
        old_section('b')
        old_section('c')
        http = classroom({ESL_TA: [['a'], ['b'], ['c']]})
        counts = remove_TA_task()
        assert counts[ESL_TA] == {'courses': 3, 'to_remove': 3}
        assert http.deleted == {('a', ESL_TA), ('b', ESL_TA), ('c', ESL_TA)}

    def test_cutoff_boundary(self, classroom):
        old_section('past', days_ago=5 * 365 + 1)
        old_section('on_cutoff', days_ago=5 * 365)
        old_section('recent', days_ago=365)
        http = classroom({ESL_TA: [['past', 'on_cutoff', 'recent']]})
        remove_TA_task()
        assert http.deleted == {('past', ESL_TA)}

    def test_only_removes_ta_from_courses_classroom_reports(self, classroom):
        old_section('still_on')
        old_section('already_removed')
        http = classroom({ESL_TA: [['still_on']]})
        remove_TA_task()
        assert http.deleted == {('still_on', ESL_TA)}

    def test_each_ta_removed_only_from_its_own_courses(self, classroom):
        old_section('esl', program=Section.ESL)
        old_section('ccr', program=Section.CCR)
        http = classroom({ESL_TA: [['esl']], CCR_TA: [['ccr']]})
        remove_TA_task()
        assert http.deleted == {('esl', ESL_TA), ('ccr', CCR_TA)}

    def test_every_program_ta_is_queried(self, classroom):
        http = classroom({})
        remove_TA_task()
        assert set(http.listed_tas) == set(program_ta.values())

    def test_dry_run_counts_without_deleting(self, classroom):
        old_section('a')
        http = classroom({ESL_TA: [['a', 'unlinked']]})
        counts = remove_TA_task(dry_run=True)
        assert counts[ESL_TA] == {'courses': 2, 'to_remove': 1}
        assert http.deleted == set()

    def test_http_error_is_logged_and_skipped(self, classroom):
        old_section('bad')
        old_section('good')
        http = classroom({ESL_TA: [['bad', 'good']]}, fail_courses={'bad'})
        remove_TA_task()
        assert http.deleted == {('bad', ESL_TA), ('good', ESL_TA)}
