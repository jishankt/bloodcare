from django.db import models
from django.contrib.auth.models import User


class Hospital(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    hospital_name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)  # city / area
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    is_approved = models.BooleanField(default=False)

    profile_photo = models.ImageField(
        upload_to='hospital/profile/',
        null=True,
        blank=True
    )

    def __str__(self):
        return self.hospital_name


class HospitalImage(models.Model):
    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='hospital/gallery/')

    def __str__(self):
        return f"{self.hospital.hospital_name} Image"
