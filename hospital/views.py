from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from requests_app.models import BloodRequest
from django.utils import timezone



from .models import Hospital, HospitalImage
from donor.models import Donor


def hospital_register(request):
    """Register a new hospital"""
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Prevent duplicate usernames
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('hospital:hospital_register')

        # Create the user
        user = User.objects.create_user(username=username, password=password)

        # Get coordinates safely
        latitude = request.POST.get('latitude') or None
        longitude = request.POST.get('longitude') or None

        # Create the hospital object
        hospital = Hospital.objects.create(
            user=user,
            hospital_name=request.POST.get('hospital_name'),
            location=request.POST.get('location'),
            latitude=float(latitude) if latitude else None,
            longitude=float(longitude) if longitude else None,
            phone=request.POST.get('phone'),
            email=request.POST.get('email'),
            profile_photo=request.FILES.get('profile_photo'),
            is_approved=False
        )

        # Save multiple hospital images if uploaded
        for img in request.FILES.getlist('hospital_images'):
            HospitalImage.objects.create(hospital=hospital, image=img)

        messages.success(request, "Registration successful. Wait for admin approval.")
        return redirect('hospital:hospital_login')

    return render(request, 'hospital/register.html')


def hospital_login(request):
    """Hospital login view"""
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            try:
                hospital = Hospital.objects.get(user=user)
            except Hospital.DoesNotExist:
                messages.error(request, "Hospital profile not found.")
                return redirect('hospital:hospital_login')

            if not hospital.is_approved:
                messages.warning(request, "⏳ Your account is pending admin approval.")
                return redirect('hospital:hospital_login')

            login(request, user)
            messages.success(request, f"Welcome {hospital.hospital_name}!")
            return redirect('hospital:hospital_dashboard')

        messages.error(request, "Invalid username or password.")
        return redirect('hospital:hospital_login')

    return render(request, 'hospital/login.html')


@login_required
def hospital_dashboard(request):
    hospital = get_object_or_404(Hospital, user=request.user)

    # Available donors (active & approved)
    donors = Donor.objects.filter(is_active=True, is_approved=True)

    # Blood requests sent by this hospital
    requests = BloodRequest.objects.filter(hospital=hospital).order_by('-created_at')

    return render(request, 'hospital/dashboard.html', {
        'hospital': hospital,
        'donors': donors,
        'requests': requests
    })


@login_required
def hospital_logout(request):
    """Logout hospital"""
    logout(request)
    return redirect('/')


@login_required
def hospital_profile(request, hospital_id):
    """View hospital profile"""
    hospital = get_object_or_404(Hospital, id=hospital_id)
    return render(request, 'hospital/profile.html', {'hospital': hospital})

@login_required
def hospital_requests(request):
    hospital = get_object_or_404(Hospital, user=request.user)

    # Get all requests sent by this hospital
    requests = BloodRequest.objects.filter(hospital=hospital).order_by('-created_at')

    if request.method == "POST":
        action = request.POST.get("action")
        req_id = request.POST.get("request_id")
        req = get_object_or_404(BloodRequest, id=req_id, hospital=hospital)

        if action == "done":
            req.done = True
            req.save()

            donor = req.donor
            donor.is_active = False
            donor.last_donation_date = timezone.now().date()
            donor.save()

            messages.success(request, f"Marked {donor.user.username} donation as done.")
            return redirect('hospital:hospital_requests')

    return render(request, 'hospital/hospital_requests.html', {
        'hospital': hospital,
        'requests': requests
    })

