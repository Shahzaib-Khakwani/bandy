import random
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_otp_email(to_email, otp):

    subject = "Your OTP Code"
    message = f"Your OTP code is: {otp}. Please do not share this code with anyone."
    from_email = settings.DEFAULT_FROM_EMAIL
    return send_mail(subject, message, from_email, [to_email])
