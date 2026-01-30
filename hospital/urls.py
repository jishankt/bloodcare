from django.urls import path
from . import views

app_name = 'hospital'

urlpatterns = [
    path('register/', views.hospital_register, name='hospital_register'),
    path('login/', views.hospital_login, name='hospital_login'),
    path('dashboard/', views.hospital_dashboard, name='hospital_dashboard'),
    path('logout/', views.hospital_logout, name='hospital_logout'),
    path('profile/<int:hospital_id>/', views.hospital_profile, name='hospital_profile'),

]
