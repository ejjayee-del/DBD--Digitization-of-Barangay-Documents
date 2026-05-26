from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from transactions.models import ActivityLog, RegistrationLog
from home import get_home_buttons
from .models import CustomUser, BarangayResident
from .forms import UserLoginForm, RequesterRegistrationForm, RegistrationApprovalForm, ResidentForm


def is_staff_or_admin(user):
    """Check if user is staff (secretary, officer, or admin)"""
    return user.is_authenticated and user.role in ['secretary', 'officer', 'admin']


def is_admin_or_officer(user):
    """Check if user is admin or officer"""
    return user.is_authenticated and user.role in ['officer', 'admin']


@require_http_methods(["GET", "POST"])
def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'register':
            register_form = RequesterRegistrationForm(request.POST)
            if register_form.is_valid():
                user = register_form.save()
                
                # Log registration
                RegistrationLog.objects.create(
                    subject_user=user,
                    action='registration_submitted' if user.status == 'pending' else 'auto_approved',
                    details=f"User registered with status: {user.status}"
                )
                
                if user.status == 'approved':
                    messages.success(request, 'Registration successful! Your account has been approved. You can now log in.')
                else:
                    messages.success(request, 'Registration submitted! Your account is pending approval.')
                
                return redirect('accounts:login')
            else:
                form = UserLoginForm()
        else:
            form = UserLoginForm(request.POST)
            register_form = RequesterRegistrationForm()
            if form.is_valid():
                username = form.cleaned_data['username']
                password = form.cleaned_data['password']
                
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    # Check if registration is approved
                    if user.role == 'requester' and user.status != 'approved':
                        messages.error(request, 'Your registration is pending approval or has been rejected. Please contact an administrator.')
                        return render(request, 'accounts/login.html', {
                            'form': form,
                            'register_form': register_form,
                            'buttons': get_home_buttons(),
                        })
                    
                    if not user.is_active_user:
                        messages.error(request, 'Your account is inactive. Please contact an administrator.')
                        return render(request, 'accounts/login.html', {
                            'form': form,
                            'register_form': register_form,
                            'buttons': get_home_buttons(),
                        })
                    
                    login(request, user)
                    
                    # Log the login activity
                    ActivityLog.objects.create(
                        user=user,
                        log_type='login',
                        action_description=f"User {username} logged in",
                        ip_address=request.META.get('REMOTE_ADDR', ''),
                        user_agent=request.META.get('HTTP_USER_AGENT', '')
                    )
                    
                    messages.success(request, f'Welcome back, {user.get_full_name()}!')
                    return redirect('dashboard')
                else:
                    messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm()
        register_form = RequesterRegistrationForm()
    
    return render(request, 'accounts/login.html', {
        'form': form,
        'register_form': register_form,
        'buttons': get_home_buttons(),
    })


@require_http_methods(["GET", "POST"])
def register_view(request):
    """Dedicated registration page"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = RequesterRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Log registration
            RegistrationLog.objects.create(
                subject_user=user,
                action='registration_submitted' if user.status == 'pending' else 'auto_approved',
                details=f"User registered with status: {user.status}"
            )
            
            if user.status == 'approved':
                messages.success(request, 'Registration successful! Your account has been approved. You can now log in.')
            else:
                messages.success(request, 'Registration submitted! Your account is pending approval.')
            
            return redirect('accounts:login')
    else:
        form = RequesterRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


@login_required
@require_http_methods(["POST"])
def logout_view(request):
    """User logout view"""
    user = request.user
    ActivityLog.objects.create(
        user=user,
        log_type='logout',
        action_description=f"User {user.username} logged out",
        ip_address=request.META.get('REMOTE_ADDR', ''),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('accounts:login')


@login_required
def dashboard_view(request):
    """Dashboard - shows different content based on user role"""
    from certificates.models import GeneratedCertificate, CertificateRequest
    from transactions.models import VisitHistory
    
    # Check registration status for requesters
    if request.user.role == 'requester' and request.user.status != 'approved':
        messages.warning(request, 'Your account registration is pending approval or has been rejected.')
    
    if request.user.role == 'requester':
        # Requester dashboard
        user_requests = CertificateRequest.objects.filter(requester=request.user).order_by('-created_date')[:10]
        context = {
            'user_requests': user_requests,
            'is_requester': True,
            'total_requests': CertificateRequest.objects.filter(requester=request.user).count(),
            'pending_requests': CertificateRequest.objects.filter(requester=request.user, status='pending').count(),
            'completed_requests': CertificateRequest.objects.filter(requester=request.user, status='completed').count(),
            'rejected_requests': CertificateRequest.objects.filter(requester=request.user, status='rejected').count(),
        }
        return render(request, 'accounts/requester_dashboard.html', context)
    
    # Staff dashboard
    if not request.user.can_view_history and not request.user.can_print_certificates:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('accounts:login')
    
    # Get stats
    total_certificates = GeneratedCertificate.objects.count()
    total_visits = CertificateRequest.objects.count()  # requests = visits
    pending_requests = CertificateRequest.objects.filter(status='pending').count()
    pending_registrations = CustomUser.objects.filter(role='requester', status='pending').count()
    recent_activities = ActivityLog.objects.select_related('user').all()[:10]
    
    context = {
        'total_certificates': total_certificates,
        'total_visits': total_visits,
        'pending_requests': pending_requests,
        'pending_registrations': pending_registrations,
        'recent_activities': recent_activities,
    }
    
    return render(request, 'accounts/dashboard.html', context)


@login_required
@user_passes_test(is_staff_or_admin)
def manage_registrations_view(request):
    """View for staff to manage pending registrations"""
    pending_registrations = CustomUser.objects.filter(role='requester', status='pending').order_by('-registration_date')
    approved_registrations = CustomUser.objects.filter(role='requester', status='approved').order_by('-registration_date')
    rejected_registrations = CustomUser.objects.filter(role='requester', status='rejected').order_by('-registration_date')
    
    context = {
        'pending_registrations': pending_registrations,
        'approved_registrations': approved_registrations,
        'rejected_registrations': rejected_registrations,
    }
    
    return render(request, 'accounts/manage_registrations.html', context)


@login_required
@user_passes_test(is_staff_or_admin)
def approve_registration_view(request, user_id):
    """Approve a pending registration"""
    user = get_object_or_404(CustomUser, id=user_id, role='requester')
    
    if user.status != 'pending':
        messages.error(request, 'This registration is not pending.')
        return redirect('accounts:manage_registrations')
    
    if request.method == 'POST':
        user.status = 'approved'
        user.save()
        
        # Log the approval
        RegistrationLog.objects.create(
            actor=request.user,
            subject_user=user,
            action='approved',
            details=f"Approved by {request.user.get_full_name()} ({request.user.role})"
        )
        
        messages.success(request, f'Registration for {user.get_full_name()} has been approved.')
        return redirect('accounts:manage_registrations')
    
    return render(request, 'accounts/approve_registration.html', {'registration': user})


@login_required
@user_passes_test(is_staff_or_admin)
def reject_registration_view(request, user_id):
    """Reject a pending registration"""
    user = get_object_or_404(CustomUser, id=user_id, role='requester')
    
    if user.status != 'pending':
        messages.error(request, 'This registration is not pending.')
        return redirect('accounts:manage_registrations')
    
    if request.method == 'POST':
        form = RegistrationApprovalForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['decision'] == 'reject':
                user.status = 'rejected'
                user.rejection_reason = form.cleaned_data.get('rejection_reason', '')
                user.save()
                
                # Log the rejection
                RegistrationLog.objects.create(
                    actor=request.user,
                    subject_user=user,
                    action='rejected',
                    details=f"Rejected by {request.user.get_full_name()} ({request.user.role}). Reason: {user.rejection_reason}"
                )
                
                messages.success(request, f'Registration for {user.get_full_name()} has been rejected.')
            return redirect('accounts:manage_registrations')
    else:
        form = RegistrationApprovalForm()
    
    return render(request, 'accounts/reject_registration.html', {'registration': user, 'form': form})


@login_required
@user_passes_test(is_admin_or_officer)
def manage_residents_view(request):
    """View and list barangay residents"""
    search_query = request.GET.get('search', '')
    
    residents = BarangayResident.objects.all()
    if search_query:
        residents = residents.filter(
            Q(full_name__icontains=search_query) | Q(address__icontains=search_query)
        )
    
    residents = residents.order_by('full_name')
    
    context = {
        'residents': residents,
        'search_query': search_query,
    }
    
    return render(request, 'accounts/manage_residents.html', context)


@login_required
@user_passes_test(is_admin_or_officer)
def create_resident_view(request):
    """Add a new barangay resident"""
    if request.method == 'POST':
        form = ResidentForm(request.POST)
        if form.is_valid():
            resident = form.save(commit=False)
            resident.added_by = request.user
            resident.save()
            
            # Log the addition
            RegistrationLog.objects.create(
                actor=request.user,
                action='resident_added',
                details=f"Resident added: {resident.full_name}, {resident.address[:100]}"
            )
            
            messages.success(request, f'Resident {resident.full_name} has been added.')
            return redirect('accounts:manage_residents')
    else:
        form = ResidentForm()
    
    return render(request, 'accounts/create_resident.html', {'form': form})


@login_required
@user_passes_test(is_admin_or_officer)
def edit_resident_view(request, resident_id):
    """Edit a barangay resident"""
    resident = get_object_or_404(BarangayResident, id=resident_id)
    
    if request.method == 'POST':
        form = ResidentForm(request.POST, instance=resident)
        if form.is_valid():
            form.save()
            
            # Log the update
            RegistrationLog.objects.create(
                actor=request.user,
                action='resident_updated',
                details=f"Resident updated: {resident.full_name}, {resident.address[:100]}"
            )
            
            messages.success(request, f'Resident {resident.full_name} has been updated.')
            return redirect('accounts:manage_residents')
    else:
        form = ResidentForm(instance=resident)
    
    return render(request, 'accounts/edit_resident.html', {'form': form, 'resident': resident})


@login_required
@user_passes_test(is_admin_or_officer)
def delete_resident_view(request, resident_id):
    """Delete a barangay resident"""
    resident = get_object_or_404(BarangayResident, id=resident_id)
    
    if request.method == 'POST':
        resident_name = resident.full_name
        
        # Log the deletion
        RegistrationLog.objects.create(
            actor=request.user,
            action='resident_deleted',
            details=f"Resident deleted: {resident.full_name}, {resident.address[:100]}"
        )
        
        resident.delete()
        messages.success(request, f'Resident {resident_name} has been deleted.')
        return redirect('accounts:manage_residents')
    
    return render(request, 'accounts/delete_resident.html', {'resident': resident})


@login_required
@user_passes_test(is_staff_or_admin)
def registration_logs_view(request):
    """View registration activity logs"""
    logs = RegistrationLog.objects.select_related('actor', 'subject_user').all().order_by('-timestamp')
    
    # Filter by action if provided
    action_filter = request.GET.get('action', '')
    if action_filter:
        logs = logs.filter(action=action_filter)
    
    context = {
        'logs': logs,
        'action_filter': action_filter,
        'actions': RegistrationLog.ACTION_CHOICES,
    }
    
    return render(request, 'accounts/registration_logs.html', context)
