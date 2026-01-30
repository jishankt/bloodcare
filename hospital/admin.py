from django.contrib import admin
from django.core.mail import send_mail
from .models import Hospital

@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ('hospital_name', 'is_approved')
    list_editable = ('is_approved',)

    def save_model(self, request, obj, form, change):
        if change:
            old = Hospital.objects.get(pk=obj.pk)
            if not old.is_approved and obj.is_approved:
                send_mail(
                    subject="Hospital Account Approved",
                    message=(
                        "Your hospital account has been approved.\n\n"
                        "You can now login and request blood donors."
                    ),
                    from_email=None,
                    recipient_list=[obj.email],
                    fail_silently=False
                )
        super().save_model(request, obj, form, change)