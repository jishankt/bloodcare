from django.db import models
from donor.models import Donor
from hospital.models import Hospital
from django.utils import timezone
from datetime import timedelta, date

class BloodRequest(models.Model):
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE)
    message = models.TextField()
    status = models.CharField(
        max_length=10,
        choices=[('pending','Pending'),('accepted','Accepted'),('rejected','Rejected')],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    arrival_time = models.CharField(max_length=50, blank=True, null=True)  # Arrival time option
    done = models.BooleanField(default=False)  # Mark donation done

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(hours=1)
