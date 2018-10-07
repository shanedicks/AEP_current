from __future__ import absolute_import, unicode_literals
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import get_template
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

@shared_task
def email_multi_alternatives_task(subject, to, from_email, text_template, html_template):
    logger.info('Sent email to {0}. Subject: {1}'.format(to, subject))
    text_content = get_template(text_template).render()
    html_content = get_template(html_template).render()
    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        to=to,
        from_email=from_email,
    )
    msg.attach_alternative(html_content, 'text/html')
    return msg.send()
