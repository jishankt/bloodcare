from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Hospital

@receiver(post_save, sender=Hospital)
def hospital_approval_email(sender, instance, created, **kwargs):
    if instance.is_approved:
        send_mail(
            subject="Hospital Account Approved",
            message="Your hospital account has been approved. You can now login.",
            from_email=None,
            recipient_list=[instance.email],
            fail_silently=True,
        )
