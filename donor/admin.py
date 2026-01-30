from django.contrib import admin
from django.core.mail import send_mail
from .models import Donor

@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    list_display = ('user', 'blood_group', 'is_approved', 'is_active')
    list_editable = ('is_approved', 'is_active')

    def save_model(self, request, obj, form, change):
        if change:
            old = Donor.objects.get(pk=obj.pk)
            if not old.is_approved and obj.is_approved:
                send_mail(
                    subject="Donor Account Approved",
                    message=(
                        "Your donor account has been approved.\n\n"
                        "You can now login and receive blood donation requests."
                    ),
                    from_email=None,
                    recipient_list=[obj.email],
                    fail_silently=False
                )
        super().save_model(request, obj, form, change)
