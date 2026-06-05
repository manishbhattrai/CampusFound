from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import College
from .forms import (
    LoginForm, RegistrationForm, CollegeRegistrationForm,
    CollegeUserForm, UserProfileUpdateForm,ChangePasswordForm
    )
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from .decorators import admin_required, college_required, student_required
from .services import send_approval_email, send_rejection_email
from items.models import Item, Claim

User = get_user_model()

# Create your views here.


def user_login(request):


    if request.user.is_authenticated:

        if request.user.is_staff:
            return redirect('admin-dashboard')

        elif request.user.role == 'student':
            return  redirect('student-dashboard')

        elif request.user.role == 'college':
            return redirect('college-dashboard')

    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")

            user = authenticate(request, username=email, password=password)

            if user is not None:
                if user.is_verified:
                    if user.is_active:
                        login(request, user)
                        if user.is_staff:
                            return redirect("admin-dashboard")
                        elif user.role == "college":
                            return redirect("college-dashboard")
                        elif user.role == "student":
                            messages.success(request, f"Welcome back {user.full_name}!")
                            return redirect("student-dashboard")

                    else:
                        messages.error(request,"Your id is deactivated. please contact college administration.")
                else:
                    messages.error(request, "Your Account is not verified yet. please contact college administration.")
            else:
                messages.error(request, "Invalid credentials.")
    else:
        form = LoginForm()

    return render(request, "auth/login.html", {"form":form})

def create_user(request):

    colleges = College.objects.all()

    if request.method == "POST":

        form = RegistrationForm(request.POST, request.FILES)

        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'student'
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request," Account registered successfully.")
            return redirect("login")



    else:
        form = RegistrationForm()

    context = {
        "form":form,
        "colleges":colleges
    }

    return render(request, "auth/student_register.html", context=context)

@login_required(login_url='login')
@admin_required
def college_registration(request):

    if request.method == 'POST':
        form = CollegeRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "College added successfully.")
            return redirect("admin-dashboard")

    else:
        form = CollegeRegistrationForm()

    return render(request, "admin/create_college.html", {"form":form})

@login_required(login_url='login')
@admin_required
def create_college_user(request):

    colleges = College.objects.all()

    if request.method == "POST":
        form = CollegeUserForm(request.POST)
        if form.is_valid():

            user = form.save(commit=False)
            user.role = 'college'
            user.is_verified = True
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, "College account created successfully.")
            return redirect("admin-dashboard")

    else:
        form = CollegeUserForm()

    context = {
        'form':form,
        'colleges':colleges
    }

    return render(request, 'admin/college_user.html', context=context)

@login_required(login_url='login')
@college_required
def college_dashboard(request):

    college = request.user.college
    recent_requests = User.objects.filter(
        college=college,
        role='student',
        is_verified=False
    ).order_by('-date_joined')[:10]

    pending_requests = User.objects.filter(
        college=college,
        role='student',
        is_verified=False
    ).count()

    total_students = User.objects.filter(
        college=college,
        role='student',
        is_verified=True
    ).count()

    context = {
        'recent_requests':recent_requests,
        'pending_requests':pending_requests,
        'total_students':total_students
    }

    return render(request, 'college/college_dashboard.html', context=context)

@login_required(login_url='login')
@college_required
def get_student_list(request):

    college = request.user.college
    students = User.objects.filter(college=college, role='student' ,is_verified=True)

    student_id = request.GET.get('search')

    if student_id:
        students = User.objects.filter(college=college, role='student', is_verified=True,
                                       student_id__icontains=student_id)

    context = {
        'students':students
    }
    return render(request, 'college/student_list.html', context=context)

@login_required(login_url='login')
@college_required
def registration_request(request):

    college = request.user.college
    pending_users = User.objects.filter(college=college, role='student', is_verified=False)

    context = {
        'pending_users':pending_users
    }

    return render(request, 'college/registration_requests.html', context=context)

@login_required(login_url='login')
@college_required
def approve_student(request,user_id):

    user = get_object_or_404(User, id=user_id, college=request.user.college)

    if request.method == 'POST':
        user.is_verified = True
        user.save()
        send_approval_email(user)

        messages.success(request,f"Approved {user.full_name}'s account.")

    return redirect('college-dashboard')

@login_required(login_url='login')
@college_required
def reject_student(request, user_id):

    user = get_object_or_404(User, id=user_id, college = request.user.college)

    if request.method == 'POST':
        user.is_verified = False
        user.save()
        send_rejection_email(user)

        messages.warning(request, 'Registration request rejected.')
        return redirect('college-dashboard')

@login_required(login_url='login')
@student_required
def student_dashboard(request):

    user = request.user
    my_items = Item.objects.filter(reported_by=user).select_related('category').order_by('-created_at')
    user_claims = Claim.objects.filter(student=user).select_related('item').order_by('-created_at')
    total_active_reports = my_items.exclude(status='recovered').count()
    total_pending_claims = user_claims.filter(status='pending').count()
    total_item_found = my_items.filter(status='recovered').count()

    context = {
        'my_items': my_items[:10],
        'user_claims': user_claims[:5],
        'total_active_reports': total_active_reports,
        'total_pending_claims': total_pending_claims,
        'total_item_found': total_item_found,
    }

    return render(request, 'student/student_dashboard.html', context=context)

@login_required(login_url='login')
@admin_required
def admin_dashboard(request):

    colleges = College.objects.all()
    total_colleges = College.objects.all().count()
    total_students = User.objects.filter(role='student',is_verified=True).count()
    total_staff_accounts = User.objects.filter(role='college').count()


    context = {
        'colleges':colleges,
        'total_colleges':total_colleges,
        'total_students':total_students,
        'total_staff_accounts':total_staff_accounts
    }
    return render(request, 'admin/admin_dashboard.html', context=context)

@login_required(login_url='login')
def user_logout(request):
    logout(request)
    return redirect("home")

def home_page(request):

    if request.user.is_authenticated:
        if request.user.role == 'student':
            return redirect('student-dashboard')

        elif request.user.role == 'college':
            return redirect('college-dashboard')

        elif request.user.is_staff:
            return redirect('admin-dashboard')

    return render(request, 'index.html')

@login_required(login_url='login')
@student_required
def user_profile(request):
    return render(request,'student/student_profile.html')

@login_required(login_url='login')
@student_required
def update_user_profile(request):

    if request.method == "POST":
        form = UserProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request,"Profile updated successfully.")
            return redirect("profile")

    else:
        form = UserProfileUpdateForm(instance=request.user)

    return render(request, 'student/update_profile.html', {"form":form})

@login_required(login_url='login')
@student_required
def deactivate_account(request):

    user = request.user.email
    user = User.objects.get(user=user)
    user.is_active=False
    user.save()
    messages.success(request,"Account deactivated successfully.")
    return redirect('student_profile')

@login_required(login_url='login')
@student_required
def change_password(request):

    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)

        if form.is_valid():

            current_password = form.cleaned_data["current_password"]
            new_password = form.cleaned_data["new_password"]

            user = request.user

            if not user.check_password(current_password):
                form.add_error("current_password", "Invalid Password.")

            else:
                user.set_password(new_password)
                user.save()

                update_session_auth_hash(request, user)
                messages.success(request, "Password changed successfully.")
                return redirect("profile")

    else:
        form = ChangePasswordForm()

    return render(request, 'student/change-password.html', {"form":form})
