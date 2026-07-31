"""Smoke sweep over the Django admin.

The admin modules churn constantly and a list_display referencing a renamed
field is exactly the bug that only surfaces when a staff member clicks it.
"""
import pytest
from django.contrib import admin
from django.urls import reverse

REGISTERED = sorted(
    admin.site._registry.keys(), key=lambda m: m._meta.label
)
IDS = [m._meta.label for m in REGISTERED]


@pytest.mark.django_db
@pytest.mark.parametrize('model', REGISTERED, ids=IDS)
def test_admin_changelist(auth_client, seed_data, model):
    opts = model._meta
    url = reverse(f'admin:{opts.app_label}_{opts.model_name}_changelist')
    response = auth_client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
@pytest.mark.parametrize('model', REGISTERED, ids=IDS)
def test_admin_add_form(auth_client, seed_data, model):
    opts = model._meta
    url = reverse(f'admin:{opts.app_label}_{opts.model_name}_add')
    response = auth_client.get(url)
    # 403 is legitimate for models whose ModelAdmin denies add permission.
    assert response.status_code in (200, 403)
