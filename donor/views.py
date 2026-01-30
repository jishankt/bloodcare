from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Donor
from requests_app.models import BloodRequest


def donor_register(request):
    """Register a new donor"""
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Check duplicate username
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('donor:donor_register')

        # Create user
        user = User.objects.create_user(username=username, password=password)

        # Get coordinates safely
        latitude = request.POST.get('latitude') or None
        longitude = request.POST.get('longitude') or None

        # Create donor
        Donor.objects.create(
            user=user,
            blood_group=request.POST.get('blood_group'),
            location=request.POST.get('location'),
            latitude=float(latitude) if latitude else None,
            longitude=float(longitude) if longitude else None,
            phone=request.POST.get('phone'),
            email=request.POST.get('email'),
            profile_photo=request.FILES.get('profile_photo'),
            is_approved=False
        )

        messages.success(request, "Registration successful. Wait for admin approval.")
        return redirect('donor:donor_login')

    return render(request, 'donor/register.html')


def donor_login(request):
    """Donor login view"""
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            try:
                donor = Donor.objects.get(user=user)
            except Donor.DoesNotExist:
                messages.error(request, "Donor profile not found.")
                return redirect('donor:donor_login')

            if not donor.is_approved:
                messages.warning(request, "⏳ Your account is pending admin approval.")
                return redirect('donor:donor_login')

            login(request, user)
            messages.success(request, "Login successful.")
            return redirect('donor:donor_dashboard')

        messages.error(request, "Invalid username or password.")
        return redirect('donor:donor_login')

    return render(request, 'donor/login.html')


@login_required
def donor_dashboard(request):
    """Donor dashboard showing blood requests"""
    donor = get_object_or_404(Donor, user=request.user)

    requests = BloodRequest.objects.filter(donor=donor).order_by('-created_at')

    return render(request, 'donor/dashboard.html', {
        'donor': donor,
        'requests': requests
    })


@login_required
def donor_logout(request):
    """Logout donor"""
    logout(request)
    return redirect('index')  # Replace 'index' with your home page URL name


@login_required
def donor_profile(request, donor_id):
    """View donor profile"""
    donor = get_object_or_404(Donor, id=donor_id)
    return render(request, 'donor/profile.html', {'donor': donor})
