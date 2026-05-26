from django.urls import include, path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    
    # Registration Management
    path('manage-registrations/', views.manage_registrations_view, name='manage_registrations'),
    path('approve-registration/<int:user_id>/', views.approve_registration_view, name='approve_registration'),
    path('reject-registration/<int:user_id>/', views.reject_registration_view, name='reject_registration'),
    
    # Resident Management
    path('manage-residents/', views.manage_residents_view, name='manage_residents'),
    path('create-resident/', views.create_resident_view, name='create_resident'),
    path('edit-resident/<int:resident_id>/', views.edit_resident_view, name='edit_resident'),
    path('delete-resident/<int:resident_id>/', views.delete_resident_view, name='delete_resident'),
    
    # Logs
    path('registration-logs/', views.registration_logs_view, name='registration_logs'),
]
