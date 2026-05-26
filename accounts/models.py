from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class CustomUser(AbstractUser):
    """Extended User model with role-based access control and registration tracking"""
    ROLE_CHOICES = (
        ('requester', 'Requester - Request Certificates'),
        ('secretary', 'Secretary - View & Print'),
        ('officer', 'Officer - View, Print & Edit'),
        ('admin', 'Admin - Full Access (View, Print, Edit, Delete)'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='secretary')
    
    # Registration tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='approved')
    registration_date = models.DateTimeField(auto_now_add=True)
    rejection_reason = models.TextField(blank=True)
    
    # Additional registration fields
    address = models.TextField(blank=True)
    birthday = models.DateField(blank=True, null=True)
    contact_number = models.CharField(max_length=20, blank=True)
    
    # Permissions
    can_view_history = models.BooleanField(default=True)
    can_print_certificates = models.BooleanField(default=True)
    can_edit_records = models.BooleanField(default=False)
    can_delete_records = models.BooleanField(default=False)
    is_active_user = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"
    
    def save(self, *args, **kwargs):
        # Set permissions based on role
        if self.role == 'requester':
            self.can_view_history = False
            self.can_print_certificates = False
            self.can_edit_records = False
            self.can_delete_records = False
        elif self.role == 'secretary':
            self.can_view_history = True
            self.can_print_certificates = True
            self.can_edit_records = False
            self.can_delete_records = False
        elif self.role == 'officer':
            self.can_view_history = True
            self.can_print_certificates = True
            self.can_edit_records = True
            self.can_delete_records = False
        elif self.role == 'admin':
            self.can_view_history = True
            self.can_print_certificates = True
            self.can_edit_records = True
            self.can_delete_records = True
        super().save(*args, **kwargs)
    
    def has_permission(self, permission):
        """Check if user has specific permission"""
        perms = {
            'view_history': self.can_view_history,
            'print_certificates': self.can_print_certificates,
            'edit_records': self.can_edit_records,
            'delete_records': self.can_delete_records,
        }
        return perms.get(permission, False)


class BarangayResident(models.Model):
    """Barangay residents database for automatic registration approval"""
    full_name = models.CharField(max_length=300)
    address = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    added_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='residents_added'
    )
    
    class Meta:
        ordering = ['full_name']
        verbose_name = 'Barangay Resident'
        verbose_name_plural = 'Barangay Residents'
    
    def __str__(self):
        return f"{self.full_name} - {self.address[:50]}"
    
    @staticmethod
    def match_resident(full_name, address):
        """Find matching resident in database (case-insensitive, partial match)"""
        full_name_lower = full_name.lower().strip()
        address_lower = address.lower().strip()
        
        residents = BarangayResident.objects.all()
        for resident in residents:
            resident_name_lower = resident.full_name.lower().strip()
            resident_address_lower = resident.address.lower().strip()
            
            # Check for name match and address overlap
            if full_name_lower in resident_name_lower or resident_name_lower in full_name_lower:
                if address_lower in resident_address_lower or resident_address_lower in address_lower:
                    return resident
        
        return None


class OfficialSignature(models.Model):
    """Barangay official signatures for certificates"""
    name = models.CharField(max_length=150)
    position = models.CharField(max_length=150)
    signature_image = models.ImageField(upload_to='signatures/')
    is_active = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_active', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.position}"


class OfficialSignature(models.Model):
    """Store signature images of barangay officials"""
    name = models.CharField(max_length=150)
    position = models.CharField(max_length=150)  # e.g., "Barangay Captain", "Secretary"
    signature_image = models.ImageField(upload_to='signatures/')
    is_active = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_active', 'position']
    
    def __str__(self):
        return f"{self.name} - {self.position}"
