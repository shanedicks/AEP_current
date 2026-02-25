import logging
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone
from assessments.tasks import update_test_history_task

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        from assessments.models import TestHistory
        target = timezone.now().date() - timedelta(days=180)
        records = TestHistory.objects.filter(
            Q(student__classes__section__semester__end_date__gte=target) |
            Q(tabe_tests__test_date__gte=target) |
            Q(clas_e_tests__test_date__gte=target)
        ).distinct()
        count = records.count()
        logger.info(f"Updating TestHistory for {count} active students")
        for record in records:
            update_test_history_task.delay(record.id)
        logger.info(f"Dispatched {count} update_test_history_task tasks")