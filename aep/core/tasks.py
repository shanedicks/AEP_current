from __future__ import absolute_import, unicode_literals
import csv
from django.apps import apps
from django.core.mail import send_mail, EmailMultiAlternatives
from django.core.mail.message import EmailMessage
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

@shared_task
def model_report_task(email_address, app, model):
    model_object = apps.get_model(app, model)
    records = model_object.objects.all()
    fieldnames = [f.name for f in model_object._meta.get_fields(include_hidden=True)]
    filename = '{}.csv'.format(model)
    with open(filename, 'w', newline='') as out:
        writer = csv.writer(out)
        writer.writerow(fieldnames)

        for record in records:
            writer.writerow([getattr(record, item) for item in fieldnames])
    email = EmailMessage(
        '{} model report'.format(model),
        'This is a full table export',
        'reporter@dccaep.org',
        [email_address]
    )
    email.attach_file(filename)
    email.send()
    return True
