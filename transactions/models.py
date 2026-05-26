from django.db import models
from django.contrib.contenttypes.models import ContentType

class Visitor(models.Model):
    """Individual visitor/person to the barangay"""
    first_name = models.CharField(max_length=150)
    middle_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(blank=True)
    contact_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date_created']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.middle_name} {self.last_name}".strip()


class VisitHistory(models.Model):
    """Record of each visit/transaction with the barangay - now serves as certificate request tracker"""
    VISIT_TYPE_CHOICES = (
        ('walk_in', 'Walk-in Visitor'),
        ('online_request', 'Online Certificate Request'),
        ('request_approved', 'Request Approved'),
        ('certificate_ready', 'Certificate Ready for Pickup'),
        ('certificate_completed', 'Certificate Completed'),
    )
    
    # Optional: For walk-in visitors (traditional visits)
    visitor = models.ForeignKey(
        Visitor, 
        on_delete=models.CASCADE, 
        related_name='visits',
        null=True,
        blank=True
    )
    
    # Optional: For registered requesters (certificate tracking)
    requester = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.CASCADE,
        related_name='certificate_visits',
        null=True,
        blank=True
    )
    
    # Optional: Link to certificate request (new - for tracking certificate requests as visits)
    certificate_request = models.ForeignKey(
        'certificates.CertificateRequest',
        on_delete=models.CASCADE,
        related_name='visit_records',
        null=True,
        blank=True
    )
    
    # Visit details
    visit_date = models.DateTimeField(auto_now_add=True)
    visit_type = models.CharField(
        max_length=25, 
        choices=VISIT_TYPE_CHOICES, 
        default='walk_in'
    )
    purpose_of_visit = models.CharField(max_length=255)
    
    # Processing details
    accommodated_by = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='accommodated_visits'
    )
    
    # Generated certificates in this visit
    generated_certificates = models.ManyToManyField(
        'certificates.GeneratedCertificate',
        related_name='visit_transactions',
        blank=True
    )
    
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-visit_date']
    
    def __str__(self):
        if self.requester:
            return f"{self.requester.get_full_name()} - {self.purpose_of_visit} ({self.get_visit_type_display()}) - {self.visit_date.strftime('%Y-%m-%d %H:%M')}"
        elif self.visitor:
            return f"{self.visitor.full_name} - {self.visit_date.strftime('%Y-%m-%d %H:%M')}"
        return f"Visit on {self.visit_date.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def outputs(self):
        """Get list of certificate outputs from this visit"""
        return list(self.generated_certificates.all())
    
    def get_visit_summary(self):
        """Return dictionary with visit summary"""
        visitor_name = self.visitor.full_name if self.visitor else (self.requester.get_full_name() if self.requester else 'Unknown')
        return {
            'visitor': visitor_name,
            'visit_date': self.visit_date,
            'visit_type': self.get_visit_type_display(),
            'purpose': self.purpose_of_visit,
            'accommodated_by': self.accommodated_by.get_full_name() if self.accommodated_by else 'N/A',
            'certificates_issued': self.generated_certificates.count(),
            'outputs': [cert.template.template_name for cert in self.generated_certificates.all()],
            'status': self.certificate_request.get_status_display() if self.certificate_request else 'Completed'
        }


class ActivityLog(models.Model):
    """Detailed audit log of all system activities"""
    LOG_TYPES = (
        ('login', 'User Login'),
        ('logout', 'User Logout'),
        ('certificate_generated', 'Certificate Generated'),
        ('certificate_printed', 'Certificate Printed'),
        ('certificate_deleted', 'Certificate Deleted'),
        ('certificate_requested', 'Certificate Requested'),
        ('record_modified', 'Record Modified'),
        ('record_deleted', 'Record Deleted'),
        ('history_viewed', 'History Viewed'),
        ('user_created', 'User Created'),
        ('user_deleted', 'User Deleted'),
        ('user_permissions_changed', 'User Permissions Changed'),
        ('template_modified', 'Template Modified'),
        ('other', 'Other Activity'),
    )
    
    user = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        related_name='activity_logs'
    )
    
    log_type = models.CharField(max_length=30, choices=LOG_TYPES)
    action_description = models.TextField()
    
    # Optional: Reference to object being acted upon
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['log_type', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user.username if self.user else 'Deleted User'} - {self.log_type} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"


class RegistrationLog(models.Model):
    """Audit log for registration activities"""
    ACTION_CHOICES = (
        ('registration_submitted', 'Registration Submitted'),
        ('auto_approved', 'Auto-Approved via Resident List'),
        ('approved', 'Approved by Staff'),
        ('rejected', 'Rejected by Staff'),
        ('resident_added', 'Resident Added'),
        ('resident_updated', 'Resident Updated'),
        ('resident_deleted', 'Resident Deleted'),
    )
    
    timestamp = models.DateTimeField(auto_now_add=True)
    actor = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='registration_logs_created'
    )
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    subject_user = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='registration_logs'
    )
    details = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Registration Log'
        verbose_name_plural = 'Registration Logs'
    
    def __str__(self):
        actor_name = self.actor.get_full_name() if self.actor else 'System'
        return f"[{self.get_action_display()}] by {actor_name} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
