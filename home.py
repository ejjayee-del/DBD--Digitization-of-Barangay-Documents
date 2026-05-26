from django.shortcuts import render
from django.urls import reverse


def get_home_buttons():
    home_url = reverse("home")
    return [
        {
            "label": "Home",
            "description": "Main overview of the site and system.",
            "url": home_url,
        },
        {
            "label": "Certificates",
            "description": "View the list of available certificates.",
            "url": reverse("public_certificates"),
        },
        {
            "label": "Processing Time",
            "description": "Learn the estimated processing times.",
            "url": f"{home_url}#processing-time",
        },
        {
            "label": "Fees",
            "description": "Review applicable fees and charges.",
            "url": f"{home_url}#fees",
        },
        {
            "label": "Contact Us",
            "description": "Find help and support contacts.",
            "url": f"{home_url}#contact-us",
        },
        {
            "label": "Login",
            "description": "Sign in to your account.",
            "url": reverse("accounts:login"),
        },
    ]


def home_view(request):
    """Render the public system overview home page."""
    overview_content = (
        "Welcome to the DBD system overview. This page gives you quick access "
        "to certificate offerings, estimated processing times, fee information, "
        "and contact details. Use the menu button to open navigation options."
    )

    buttons = get_home_buttons()

    certificates = [
        "Barangay Clearance",
        "Certificate of Residency",
        "Certificate of Non-Residency",
        "Certificate of Financial Assistance",
        "Certificate of Participation",
        "Certificate of Indigency",
        "Other Certificates and Forms are Available"
    ]

    processing_times = [
        {"service": "Certificate requests", "time": "1-2 business days"},
        {"service": "Verification and approval", "time": "1-3 business days"},
        {"service": "Generated Document Release", "time": "Same day once approved"},
    ]

    fees = [
        {"item": "Barangay Clearance", "amount": "₱10.00"},
        {"item": "Residency Certificate", "amount": "₱10.00"},
        {"item": "Non-Residency Certificate", "amount": "₱10.00"},
        {"item": "Forms", "amount": "₱50.00"},
    ]

    contact = {
        "email": "support@dbd.local",
        "phone": "(02) 1234-5678",
        "address": "Barangay Hall, Main Street, Barangay Center",
    }

    context = {
        "overview_content": overview_content,
        "buttons": buttons,
        "certificates": certificates,
        "processing_times": processing_times,
        "fees": fees,
        "contact": contact,
    }

    return render(request, "home.html", context)


def public_certificates_view(request):
    """Render the public certificates list page without requiring login."""
    from certificates.models import CertificateTemplate

    certificates = CertificateTemplate.objects.filter(is_active=True).order_by('template_name')
    context = {
        'certificates': certificates,
        'buttons': get_home_buttons(),
    }
    return render(request, 'home_certificates.html', context)
