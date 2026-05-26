from django.contrib import admin
from .models import Visitor, VisitHistory, ActivityLog, RegistrationLog


@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'contact_number', 'date_created')
    search_fields = ('first_name', 'last_name', 'email', 'contact_number')
    list_filter = ('date_created',)
    readonly_fields = ('date_created', 'date_updated')


@admin.register(VisitHistory)
class VisitHistoryAdmin(admin.ModelAdmin):
    list_display = ('visitor', 'requester', 'visit_type', 'visit_date', 'purpose_of_visit')
    list_filter = ('visit_type', 'visit_date', 'accommodated_by')
    search_fields = ('visitor__first_name', 'visitor__last_name', 'requester__username', 'purpose_of_visit')
    readonly_fields = ('visit_date',)


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'log_type', 'timestamp', 'action_description')
    list_filter = ('log_type', 'timestamp', 'user')
    search_fields = ('user__username', 'action_description')
    readonly_fields = ('timestamp', 'user')


@admin.register(RegistrationLog)
class RegistrationLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'actor', 'action', 'subject_user', 'details')
    list_filter = ('action', 'timestamp')
    search_fields = ('actor__username', 'subject_user__username', 'details')
    readonly_fields = ('timestamp',)
