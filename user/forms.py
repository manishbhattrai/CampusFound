from django import forms
from .models import College
from django.contrib.auth import get_user_model
import os

User = get_user_model()


class RegistrationForm(forms.ModelForm):

    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    student_id = forms.CharField(required=True)
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['first_name','middle_name', 'last_name', 'email','student_id',
                  'profile_image', 'college', 'password','confirm_password']


    def clean_first_name(self):
        first_name = self.cleaned_data.get("first_name")

        if len(first_name) < 2:
            raise forms.ValidationError("First name is too short.")

        return first_name

    def clean_profile_image(self):
        profile_image = self.cleaned_data.get("profile_image")

        MAX_SIZE = 10*1024*1024

        if profile_image:
            ext = os.path.splitext(profile_image.name)[1].lower()

            if ext not in ['.jpg','.jpeg']:
                raise forms.ValidationError("Image should be in jpg or jpeg format")

            if profile_image.size > MAX_SIZE:
                raise forms.ValidationError("Image should be less than 10MB.")

        return profile_image

    def clean_email(self):
        email = self.cleaned_data.get("email")

        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists.")
        return email

    def clean_password(self):
        password = self.cleaned_data.get("password")

        if len(password) < 5:
            raise forms.ValidationError("Password should be more than 5 character.")

        return password

    def clean(self):
        cleaned_data = super().clean()

        first_name = cleaned_data.get("first_name")
        middle_name = cleaned_data.get("middle_name")
        last_name = cleaned_data.get("last_name")
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if first_name:
            cleaned_data['first_name'] = first_name.lower()

        if middle_name:
            cleaned_data['middle_name'] = middle_name.lower()

        if last_name:
            cleaned_data['last_name'] = last_name.lower()

        if password != confirm_password:
            raise forms.ValidationError("Password didn't match.")

        return cleaned_data

class LoginForm(forms.Form):

    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


class CollegeUserForm(forms.ModelForm):

    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['email','password','college']

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists.")

        return email

class CollegeRegistrationForm(forms.ModelForm):

    class Meta:
        model = College
        fields = ['name','address','logo']


    def clean_logo(self):
        logo = self.cleaned_data.get("logo")

        MAX_SIZE = 5 * 1024 * 1024

        if logo.size > MAX_SIZE:
            raise forms.ValidationError("Logo should be less than 5MB.")

        return logo

class UserProfileUpdateForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['first_name','middle_name','last_name','email','profile_image']


    def clean_first_name(self):
        first_name = self.cleaned_data.get("first_name")

        if len(first_name) < 2:
            raise forms.ValidationError("First name is too short.")

        return first_name

    def clean_profile_image(self):
        profile_image = self.cleaned_data.get("profile_image")

        MAX_SIZE = 10*1024*1024

        if profile_image:
            ext = os.path.splitext(profile_image.name)[1].lower()

            if ext not in ['.jpg','.jpeg']:
                raise forms.ValidationError("Image should be in jpg or jpeg format")

            if profile_image.size > MAX_SIZE:
                raise forms.ValidationError("Image should be less than 10MB.")

        return profile_image


class ChangePasswordForm(forms.Form):

    current_password = forms.CharField(widget=forms.PasswordInput)
    new_password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()

        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password and confirm_password:
            if new_password != confirm_password:
                raise forms.ValidationError("Password didn't match.")

        if len(new_password) < 5:
            raise forms.ValidationError("Password should be more than 5 characters.")

        return cleaned_data
