from django.db import models
from django.contrib.auth.models import User

class Donor(models.Model):
   
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    blood_group = models.CharField(max_length=5)
    location = models.CharField(max_length=100)  # readable location
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    phone = models.CharField(max_length=15) 
    is_approved = models.BooleanField(default=False) 
    email = models.EmailField()
    profile_photo = models.ImageField(
        upload_to='donor/profile/',
        null=True,
        blank=True
    )
    arrival_time = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    last_donation_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.user.username
