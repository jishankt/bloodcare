from django.core.mail import send_mail
from django.conf import settings

def send_approval_email(email, role):
    send_mail(
        'Account Approved',
        f'Your {role} account has been approved. You can now login.',
        settings.EMAIL_HOST_USER,
        [email],
    )
