from django.urls import path
from . import views

app_name = 'donor'

urlpatterns = [
    path('register/', views.donor_register, name='donor_register'),
    path('login/', views.donor_login, name='donor_login'),
    path('dashboard/', views.donor_dashboard, name='donor_dashboard'),
    path('logout/', views.donor_logout, name='donor_logout'),
    path('profile/<int:donor_id>/', views.donor_profile, name='donor_profile'),

]
