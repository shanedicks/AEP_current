"""The two cheapest tests in the suite."""
import pytest
from django.core.management import call_command


@pytest.mark.django_db
def test_no_missing_migrations():
    """Model changed without a migration is a deploy-breaker on Heroku."""
    call_command('makemigrations', '--check', '--dry-run', verbosity=0)


def test_system_checks_pass():
    call_command('check', verbosity=0)
