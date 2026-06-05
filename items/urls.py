from django.urls import path
from . import views



urlpatterns = [

    path('create/', views.create_report, name='create-report'),
    path('reports/', views.get_reports, name='get-reports'),
    path('my-reports/', views.my_reports, name='my-reports'),
    path('detail/<uuid:uuid>/', views.report_detail, name='report-detail'),
    path('create-claim/<int:id>/', views.claim_report, name='create-claim'),
    path('claims/incoming/',views.manage_incoming_claims, name='manage-incoming-claims'),
    path('claims/process/<int:claim_id>/', views.process_claim, name='process-claim'),
    path('claims/my-claims/', views.my_claims, name='my-claims'),
    path('category/create/', views.create_category, name='create-category'),
    path('categories/', views.category_list, name='category-list'),
    path('categories/update/<int:id>/', views.update_category, name='update-category'),
    path('categories/delete/<int:id>/', views.delete_category, name='delete-category'),
]