from celery import shared_task
from django.core.mail import send_mail
from django.template.defaultfilters import striptags
from django.template.loader import render_to_string
from Uni_Automation import settings

@shared_task
def send_emails(template_name,subject,to,context):
    tags=striptags(template_name,context)
    message=render_to_string(tags)
    from_email=settings.EMAIL_HOST_USER
    send_mail(html_message=message,message=tags,from_email=from_email,recipient_list=[to],subject=subject)