from __future__ import absolute_import, unicode_literals
from datetime import datetime
from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

def get_elearn_record(elearn_record_id):
	ElearnRecord = apps.get_model('coaching', 'ElearnRecord')
	return ElearnRecord.objects.get(id=elearn_record_id)

def elearn_status_task(elearn_record_id):
	loggerl.info("Updating status of ElearnRecord {0}".format(elearn_record_id))
	elearn_record = get_elearn_record(elearn_record_id)
	elearn_record.elearn_status = 'Pending'
	elearn_record.status_updated = datetime.today()
	elearn_record.save()
