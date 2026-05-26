from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, OfficialSignature, BarangayResident


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Registration', {'fields': ('status', 'registration_date', 'rejection_reason')}),
        ('Profile', {'fields': ('address', 'birthday', 'contact_number')}),
        ('Permissions', {'fields': ('role', 'can_view_history', 'can_print_certificates', 'can_edit_records', 'can_delete_records', 'is_active_user')}),
    )
    list_display = ('username', 'get_full_name', 'role', 'status', 'is_active', 'date_created')
    list_filter = ('role', 'status', 'is_active', 'date_created')
    readonly_fields = ('registration_date', 'date_created')


@admin.register(OfficialSignature)
class OfficialSignatureAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'is_active', 'date_created')
    list_filter = ('is_active', 'position', 'date_created')
    search_fields = ('name', 'position')
    readonly_fields = ('date_created', 'date_updated')


@admin.register(BarangayResident)
class BarangayResidentAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'address', 'added_by', 'date_added')
    list_filter = ('date_added', 'date_updated')
    search_fields = ('full_name', 'address')
    readonly_fields = ('date_added', 'date_updated')
