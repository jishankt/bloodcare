from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from donor.models import Donor
from hospital.models import Hospital
from .models import BloodRequest
from django.core.mail import send_mail
from django.conf import settings


@login_required
def send(request, donor_id):
    """Hospital sends a blood request to a donor"""
    hospital = get_object_or_404(Hospital, user=request.user)
    donor = get_object_or_404(Donor, id=donor_id)

    if request.method == "POST":
        message = request.POST.get(
            'message',
            'You are requested to donate blood.'
        )

        # Create blood request
        BloodRequest.objects.create(
            hospital=hospital,
            donor=donor,
            message=message
        )

        # Send email notification to donor
        if donor.email:
            send_mail(
                subject="🩸 Blood Donation Request",
                message=(
                    f"Dear {donor.user.username},\n\n"
                    f"You have received a blood donation request.\n\n"
                    f"Hospital: {hospital.hospital_name}\n"
                    f"Location: {hospital.location}\n\n"
                    f"Message:\n{message}\n\n"
                    "Please login to your account to respond.\n\n"
                    "Thank you for saving lives ❤️"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[donor.email],
                fail_silently=True
            )

        messages.success(request, "Blood request sent and email notified.")
        return redirect('hospital:hospital_dashboard')

    return render(request, 'requests_app/send.html', {'donor': donor})


@login_required
def accept(request, request_id):
    """Donor accepts a blood request"""
    req = get_object_or_404(BloodRequest, id=request_id, donor__user=request.user)
    req.status = 'accepted'
    req.save()

    messages.success(request, "Request accepted.")
    return redirect('donor:donor_dashboard')


@login_required
def reject(request, request_id):
    """Donor rejects a blood request"""
    req = get_object_or_404(BloodRequest, id=request_id, donor__user=request.user)
    req.status = 'rejected'
    req.save()

    messages.warning(request, "Request rejected.")
    return redirect('donor:donor_dashboard')


@login_required
def view_request(request, request_id):
    """Donor views and responds to a blood request"""
    req_obj = get_object_or_404(BloodRequest, id=request_id, donor__user=request.user)

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "accept":
            req_obj.status = "accepted"
            req_obj.save()
            messages.success(request, "Request accepted.")
            return redirect('donor:donor_dashboard')

        elif action == "reject":
            req_obj.status = "rejected"
            req_obj.save()
            messages.warning(request, "Request rejected.")
            return redirect('donor:donor_dashboard')

        elif action == "arrival_time":
            arrival_time = request.POST.get("arrival_time")
            if arrival_time:
                req_obj.arrival_time = arrival_time
                req_obj.save()
                messages.success(request, "Arrival time sent.")
            return redirect('donor:donor_dashboard')

        elif action == "done":
            req_obj.done = True
            req_obj.save()
            donor = req_obj.donor
            donor.is_active = False
            donor.last_donation_date = timezone.now().date()
            donor.save()
            messages.success(request, "Donation marked as done.")
            return redirect('donor:donor_dashboard')

    return render(request, 'requests_app/view.html', {
        'request_obj': req_obj
    })


@login_required
def send_arrival_time(request, request_id):
    """Donor sends arrival time to hospital"""
    req_obj = get_object_or_404(BloodRequest, id=request_id, donor__user=request.user)

    if request.method == "POST":
        req_obj.arrival_time = request.POST.get('arrival_time')
        req_obj.save()

        messages.success(request, "Arrival time sent.")
        return redirect('donor:donor_dashboard')

    return render(request, 'requests_app/send_arrival_time.html', {'req': req_obj})


@login_required
def mark_done(request, request_id):
    # Only hospital users can mark done
    try:
        hospital = request.user.hospital
    except Hospital.DoesNotExist:
        # Optionally, show error if donor tries to access this
        return redirect('donor:donor_dashboard')

    br = get_object_or_404(BloodRequest, id=request_id, hospital=hospital)

    # Only mark done if request was accepted
    if br.status == "accepted" and not br.done:
        br.done = True
        br.save()

    return redirect('hospital:hospital_dashboard')