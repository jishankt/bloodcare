# utils/email.py
"""
Email utility module for LifeStream Blood Donation Platform
"""

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

def send_blood_request_email(request):
    """
    Send blood request email to donor
    """
    donor = request.donor
    hospital = request.hospital
    
    # Email subject with emoji
    subject = f"🩸 Urgent Blood Donation Request from {hospital.hospital_name}"
    
    # Create HTML email
    context = {
        'request': request,
        'donor': donor,
        'hospital': hospital,
        'expiry_time': request.created_at + timedelta(hours=1),
        'time_remaining': request.time_remaining,
        'login_url': f"{settings.SITE_URL}/donor/login/",
        'view_request_url': f"{settings.SITE_URL}/requests/view/{request.id}/",
        'emergency_contact': hospital.phone,
    }
    
    html_content = render_to_string('emails/blood_request.html', context)
    text_content = strip_tags(html_content)
    
    # Create email
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[donor.email],
        reply_to=[hospital.email]
    )
    
    email.attach_alternative(html_content, "text/html")
    
    # Add urgency headers
    if request.urgency in ['high', 'critical']:
        email.extra_headers['Priority'] = 'urgent'
        email.extra_headers['Importance'] = 'high'
        email.extra_headers['X-Priority'] = '1'
    
    try:
        email.send(fail_silently=False)
        return True, "Email sent successfully"
    except Exception as e:
        return False, str(e)


def send_approval_email(user_type, instance):
    """
    Send approval email to donor or hospital
    """
    if user_type == 'donor':
        subject = "🎉 Your Donor Account Has Been Approved!"
        template = 'emails/donor_approval.html'
        recipient = instance.email
    else:  # hospital
        subject = "🏥 Your Hospital Account Has Been Approved!"
        template = 'emails/hospital_approval.html'
        recipient = instance.email
    
    context = {
        'instance': instance,
        'login_url': f"{settings.SITE_URL}/{user_type}/login/",
        'support_email': settings.SUPPORT_EMAIL,
    }
    
    html_content = render_to_string(template, context)
    text_content = strip_tags(html_content)
    
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient]
    )
    
    email.attach_alternative(html_content, "text/html")
    
    try:
        email.send(fail_silently=False)
        return True
    except Exception as e:
        print(f"Approval email failed: {e}")
        return False


def send_arrival_confirmation_email(request):
    """
    Send email confirming donor's arrival time to hospital
    """
    subject = f"🕒 Donor Arrival Confirmed: {request.donor.user.username}"
    
    context = {
        'request': request,
        'donor': request.donor,
        'hospital': request.hospital,
        'arrival_time': request.arrival_time,
        'estimated_arrival': request.estimated_arrival,
        'donor_phone': request.donor.phone,
        'whatsapp_link': f"https://wa.me/{request.donor.phone}",
    }
    
    html_content = render_to_string('emails/arrival_confirmation.html', context)
    text_content = strip_tags(html_content)
    
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[request.hospital.email]
    )
    
    email.attach_alternative(html_content, "text/html")
    
    try:
        email.send(fail_silently=False)
        return True
    except Exception as e:
        print(f"Arrival confirmation email failed: {e}")
        return False


def send_donation_completion_email(request):
    """
    Send thank you email to donor after donation completion
    """
    subject = "🎉 Thank You for Donating Blood and Saving a Life!"
    
    context = {
        'request': request,
        'donor': request.donor,
        'hospital': request.hospital,
        'completion_time': request.donation_completed or timezone.now(),
        'next_donation_date': request.donor.last_donation_date + timedelta(days=56),
        'total_donations': request.donor.total_donations,
        'certificate_url': f"{settings.SITE_URL}/donor/certificate/{request.id}/",
    }
    
    html_content = render_to_string('emails/donation_thankyou.html', context)
    text_content = strip_tags(html_content)
    
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[request.donor.email]
    )
    
    # Attach certificate PDF if available
    # certificate_pdf = generate_certificate_pdf(request)
    # if certificate_pdf:
    #     email.attach('donation_certificate.pdf', certificate_pdf, 'application/pdf')
    
    email.attach_alternative(html_content, "text/html")
    
    try:
        email.send(fail_silently=False)
        return True
    except Exception as e:
        print(f"Donation completion email failed: {e}")
        return False


def send_reminder_email(request):
    """
    Send reminder email for pending requests
    """
    if request.status != 'pending' or request.done:
        return False
    
    subject = f"⏰ Reminder: Blood Donation Request from {request.hospital.hospital_name}"
    
    context = {
        'request': request,
        'donor': request.donor,
        'hospital': request.hospital,
        'time_remaining': request.time_remaining,
        'view_request_url': f"{settings.SITE_URL}/requests/view/{request.id}/",
        'emergency_contact': request.hospital.phone,
    }
    
    html_content = render_to_string('emails/request_reminder.html', context)
    text_content = strip_tags(html_content)
    
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[request.donor.email]
    )
    
    email.attach_alternative(html_content, "text/html")
    
    try:
        email.send(fail_silently=False)
        return True
    except Exception as e:
        print(f"Reminder email failed: {e}")
        return False


def send_weekly_digest(donor):
    """
    Send weekly digest email to donors
    """
    from requests_app.models import BloodRequest
    
    # Get recent activity
    recent_requests = BloodRequest.objects.filter(
        donor=donor,
        created_at__gte=timezone.now() - timedelta(days=7)
    ).order_by('-created_at')
    
    stats = {
        'total_requests': recent_requests.count(),
        'accepted': recent_requests.filter(status='accepted').count(),
        'completed': recent_requests.filter(status='completed').count(),
        'pending': recent_requests.filter(status='pending').count(),
    }
    
    subject = f"📊 Your Weekly LifeStream Digest"
    
    context = {
        'donor': donor,
        'recent_requests': recent_requests[:5],
        'stats': stats,
        'days_since_last_donation': donor.days_since_last_donation,
        'can_donate': donor.can_donate,
        'profile_url': f"{settings.SITE_URL}/donor/profile/",
        'update_availability_url': f"{settings.SITE_URL}/donor/availability/",
    }
    
    html_content = render_to_string('emails/weekly_digest.html', context)
    text_content = strip_tags(html_content)
    
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[donor.email]
    )
    
    email.attach_alternative(html_content, "text/html")
    
    try:
        email.send(fail_silently=False)
        return True
    except Exception as e:
        print(f"Weekly digest email failed: {e}")
        return False


def send_emergency_alert(donors, hospital, message):
    """
    Send emergency blood requirement alert to multiple donors
    """
    subject = f"🚨 EMERGENCY: Critical Blood Requirement at {hospital.hospital_name}"
    
    successful_sends = 0
    failed_sends = []
    
    for donor in donors:
        context = {
            'donor': donor,
            'hospital': hospital,
            'message': message,
            'emergency_contact': hospital.phone,
            'login_url': f"{settings.SITE_URL}/donor/login/",
        }
        
        html_content = render_to_string('emails/emergency_alert.html', context)
        text_content = strip_tags(html_content)
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[donor.email],
            headers={
                'Priority': 'urgent',
                'Importance': 'high',
                'X-Priority': '1',
            }
        )
        
        email.attach_alternative(html_content, "text/html")
        
        try:
            email.send(fail_silently=False)
            successful_sends += 1
        except Exception as e:
            failed_sends.append(donor.email)
    
    return successful_sends, failed_sends


def send_password_reset_email(user, reset_url):
    """
    Send password reset email
    """
    subject = "🔐 Password Reset Request - LifeStream"
    
    context = {
        'user': user,
        'reset_url': reset_url,
        'expiry_hours': 24,
    }
    
    html_content = render_to_string('emails/password_reset.html', context)
    text_content = strip_tags(html_content)
    
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email]
    )
    
    email.attach_alternative(html_content, "text/html")
    
    try:
        email.send(fail_silently=False)
        return True
    except Exception as e:
        print(f"Password reset email failed: {e}")
        return False


def send_welcome_email(user_type, instance):
    """
    Send welcome email after registration
    """
    if user_type == 'donor':
        subject = "👋 Welcome to LifeStream - Thank You for Registering as a Donor!"
        template = 'emails/welcome_donor.html'
        recipient = instance.email
        name = instance.user.username
    else:  # hospital
        subject = "👋 Welcome to LifeStream - Hospital Registration Received"
        template = 'emails/welcome_hospital.html'
        recipient = instance.email
        name = instance.hospital_name
    
    context = {
        'name': name,
        'user_type': user_type,
        'instance': instance,
        'approval_pending': not instance.is_approved,
        'support_email': settings.SUPPORT_EMAIL,
        'help_center_url': f"{settings.SITE_URL}/help/",
    }
    
    html_content = render_to_string(template, context)
    text_content = strip_tags(html_content)
    
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient]
    )
    
    email.attach_alternative(html_content, "text/html")
    
    try:
        email.send(fail_silently=False)
        return True
    except Exception as e:
        print(f"Welcome email failed: {e}")
        return False