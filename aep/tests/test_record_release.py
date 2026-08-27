"""RecordRelease: form validation, staff create/upload, public sign view, link send, merge."""
import datetime

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils import timezone

from core.utils import DriveUploadError
from people.forms import RecordReleaseUploadForm
from people.models import RecordRelease, move_record_releases
from tests import factories

pytestmark = pytest.mark.django_db

BASE = {
    'released_to': 'Jefferson Parish Schools',
    'relationship': 'SCH',
    'purpose': 'Transcript and attendance',
}


def _png():
    return SimpleUploadedFile('release.png', b'\x89PNG\r\n', content_type='image/png')


# -- form ---------------------------------------------------------------------

def test_upload_form_requires_signature_or_file():
    form = RecordReleaseUploadForm(data=BASE)
    assert not form.is_valid()
    assert 'Type a signature or upload' in str(form.non_field_errors())


def test_upload_form_valid_with_signature_only():
    form = RecordReleaseUploadForm(data={**BASE, 'signature': 'Pat Guardian'})
    assert form.is_valid(), form.errors


def test_upload_form_valid_with_file_only():
    form = RecordReleaseUploadForm(data=BASE, files={'release_file': _png()})
    assert form.is_valid(), form.errors


def test_upload_form_rejects_unsupported_file_type():
    bad = SimpleUploadedFile('release.gif', b'GIF89a', content_type='image/gif')
    form = RecordReleaseUploadForm(data=BASE, files={'release_file': bad})
    assert not form.is_valid()
    assert 'release_file' in form.errors


def test_upload_form_update_keeps_existing_file_without_signature():
    release = factories.RecordReleaseFactory(release_file='existingid')
    form = RecordReleaseUploadForm(data=BASE, instance=release)
    assert form.is_valid(), form.errors


# -- staff create -------------------------------------------------------------

def test_staff_create_with_file_uploads_to_drive(auth_client, staff_user, monkeypatch):
    student = factories.StudentFactory()
    monkeypatch.setattr('people.views.file_to_drive', lambda **kw: 'fakeid')
    url = reverse('people:record release create', kwargs={'slug': student.slug})
    resp = auth_client.post(url, {**BASE, 'release_file': _png()})
    release = RecordRelease.objects.get(student=student)
    assert resp.status_code == 302
    assert resp.url == release.get_absolute_url()
    assert release.release_file == 'fakeid'
    assert release.created_by == staff_user
    assert release.sig_date is None


def test_staff_create_drive_error_shows_form_error(auth_client, monkeypatch):
    student = factories.StudentFactory()

    def boom(**kw):
        raise DriveUploadError('drive down')

    monkeypatch.setattr('people.views.file_to_drive', boom)
    url = reverse('people:record release create', kwargs={'slug': student.slug})
    resp = auth_client.post(url, {**BASE, 'release_file': _png()})
    assert resp.status_code == 200
    assert 'drive down' in resp.content.decode()
    assert not RecordRelease.objects.filter(student=student).exists()


def test_staff_create_with_typed_signature_stamps_date(auth_client):
    student = factories.StudentFactory()
    url = reverse('people:record release create', kwargs={'slug': student.slug})
    auth_client.post(url, {**BASE, 'signature': 'Sam Student', 'guardian_signature': 'Pat Guardian'})
    release = RecordRelease.objects.get(student=student)
    assert release.sig_date == timezone.localdate()
    assert release.g_sig_date == timezone.localdate()
    assert release.release_file == ''


def test_staff_views_require_login(client):
    student = factories.StudentFactory()
    release = factories.RecordReleaseFactory(student=student)
    for url in (
        reverse('people:record release list', kwargs={'slug': student.slug}),
        reverse('people:record release create', kwargs={'slug': student.slug}),
        reverse('people:record release detail', kwargs={'pk': release.pk}),
        reverse('people:record release edit', kwargs={'pk': release.pk}),
        reverse('people:send record release link', kwargs={'slug': student.slug}),
    ):
        assert client.get(url).status_code == 302, url


# -- public sign view ---------------------------------------------------------

def test_public_sign_view_get_is_anonymous(client):
    student = factories.StudentFactory()
    url = reverse('people:sign record release', kwargs={'slug': student.slug})
    assert client.get(url).status_code == 200


def test_public_sign_view_requires_signature(client):
    student = factories.StudentFactory()
    url = reverse('people:sign record release', kwargs={'slug': student.slug})
    resp = client.post(url, BASE)
    assert resp.status_code == 200
    assert not RecordRelease.objects.filter(student=student).exists()


def test_public_sign_view_creates_a_row_per_submission(client):
    student = factories.StudentFactory()
    url = reverse('people:sign record release', kwargs={'slug': student.slug})
    resp = client.post(url, {**BASE, 'signature': 'Sam Student'})
    assert resp.status_code == 302
    assert resp.url == reverse('people:paperwork success')
    client.post(url, {**BASE, 'released_to': 'Another Org', 'signature': 'Sam Student',
                      'guardian_signature': 'Pat Guardian'})
    releases = RecordRelease.objects.filter(student=student).order_by('pk')
    assert releases.count() == 2
    first, second = releases
    assert first.sig_date == timezone.localdate()
    assert first.g_sig_date is None
    assert second.g_sig_date == timezone.localdate()
    assert first.created_by is None


def test_public_sign_view_redirects_duplicate_slug(client):
    canonical = factories.StudentFactory()
    dup = factories.StudentFactory(duplicate=True, duplicate_of=canonical)
    url = reverse('people:sign record release', kwargs={'slug': dup.slug})
    resp = client.get(url)
    assert resp.status_code == 302
    assert resp.url == reverse('people:sign record release', kwargs={'slug': canonical.slug})


# -- send link ----------------------------------------------------------------

def test_send_link_dispatches_task(auth_client, celery_calls):
    student = factories.StudentFactory()
    url = reverse('people:send record release link', kwargs={'slug': student.slug})
    resp = auth_client.get(url)
    assert resp.status_code == 302
    assert resp.url == reverse('people:link sent', kwargs={'slug': student.slug})
    calls = celery_calls.for_task('send_paperwork_link_task')
    assert len(calls) == 1
    assert calls[0][1] == (student.id, 'sign record release')


def test_link_methods_send_without_completion_gate(celery_calls):
    student = factories.StudentFactory(phone='5045551234', email='s@example.com')
    factories.RecordReleaseFactory(student=student)  # existing release must not block
    student.email_form_link('sign record release')
    student.text_form_link('sign record release')
    assert len(celery_calls.for_task('send_mail_task')) == 1
    sms = celery_calls.for_task('send_sms_task')
    assert len(sms) == 1
    assert student.record_release_form_link() in sms[0][1][1]


# -- merge --------------------------------------------------------------------

def test_move_record_releases_repoints_to_surviving_student():
    orig = factories.StudentFactory()
    survivor = factories.StudentFactory()
    a = factories.RecordReleaseFactory(student=orig)
    b = factories.RecordReleaseFactory(student=orig)
    move_record_releases(orig, survivor)
    assert set(survivor.record_releases.values_list('pk', flat=True)) == {a.pk, b.pk}
    assert not orig.record_releases.exists()
