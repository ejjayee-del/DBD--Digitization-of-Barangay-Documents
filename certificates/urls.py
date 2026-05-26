from django.urls import include, path
from . import views

app_name = 'certificates'

urlpatterns = [
    path('types/', views.certificate_types_view, name='types'),
    path('generate/<int:template_id>/', views.generate_certificate_view, name='generate'),
    path('preview/<int:certificate_id>/', views.preview_certificate_view, name='preview'),
    path('download/<int:certificate_id>/', views.download_certificate_view, name='download'),
    path('print/<int:certificate_id>/', views.print_certificate_view, name='print'),
    path('list/', views.list_certificates_view, name='list'),
    path('edit/<int:certificate_id>/', views.edit_certificate_view, name='edit_certificate'),
    path('print-from-system/<int:certificate_id>/', views.print_certificate_from_system, name='print_from_system'),
    
    # Requester URLs
    path('request/types/', views.request_certificate_types_view, name='request_types'),
    path('request/<int:template_id>/', views.request_certificate_view, name='request'),
    path('my-requests/', views.my_requests_view, name='my_requests'),
    
    # Staff URLs
    path('manage-requests/', views.manage_requests_view, name='manage_requests'),
    path('preview-request/<int:request_id>/', views.preview_request_staff_view, name='preview_request_staff'),
    path('approve-request/<int:request_id>/', views.approve_request_view, name='approve_request'),
    path('reject-request/<int:request_id>/', views.reject_request_view, name='reject_request'),
    path('release/<int:certificate_id>/', views.release_certificate_view, name='release'),
]
