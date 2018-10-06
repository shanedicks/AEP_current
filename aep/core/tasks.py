from __future__ import absolute_import, unicode_literals
from django.core.mail import send_mail
from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@shared_task
def send_mail_task(subject,message,from_email,recipient_list, html_message=None):
	logger.info('Sent email to {0}. Subject:{1}'.format(recipient_list, subject))
	return send_mail(
		subject=subject,
		message=message,
		html_message=html_message,
		from_email=from_email,
		recipient_list=recipient_list
	)
