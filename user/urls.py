from django.urls import path
from .views import (
    create_user, user_login, college_registration,
    college_dashboard, create_college_user, admin_dashboard, student_dashboard,
    user_logout, home_page, user_profile, deactivate_account, change_password, update_user_profile,
    get_student_list, registration_request, approve_student, reject_student,
)

urlpatterns = [

    path('signup/', create_user, name='student-register'),
    path('login/', user_login, name='login'),
    path('college/register/',college_registration, name='create-college'),
    path('accounts/college/create/',create_college_user, name='create-college-user'),
    path('admin-dashboard/', admin_dashboard, name='admin-dashboard'),
    path('student/dashboard/',student_dashboard, name='student-dashboard'),
    path('college/dashboard/', college_dashboard, name='college-dashboard'),
    path('', home_page, name='home'),
    path('logout/', user_logout, name='logout'),
    path('student/profile/', user_profile, name='profile'),
    path('student/update-profile/', update_user_profile, name='update-profile'),
    path('accounts/deactivate/', deactivate_account, name='deactivate-account'),
    path('accounts/change-password/', change_password, name='change-password'),
    path('college/student-list/', get_student_list, name='student-list'),
    path('college/registration/requests/', registration_request, name='registration-requests'),
    path('college/approve-student/<int:user_id>/', approve_student, name='approve-student'),
    path('college/reject-student/<int:user_id>/', reject_student, name='reject-student'),

]