from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin

from .managers import CustomUserManager


class College(models.Model):

    name = models.CharField(max_length=200)
    address = models.TextField()
    logo = models.ImageField(upload_to="logo/")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} {self.address}"

class CustomUser(AbstractBaseUser, PermissionsMixin):

    USER_ROLE_CHOICES = [
        ('college','College'),
        ('student', 'Student'),
    ]

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=225, null=True, blank=True)
    middle_name = models.CharField(max_length=225, null=True, blank=True)
    last_name = models.CharField(max_length=225, null=True, blank=True)
    profile_image = models.ImageField(upload_to='profile/', null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    student_id = models.CharField(max_length=100, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    college = models.ForeignKey(College, on_delete=models.SET_NULL, null=True, blank=True)
    trust_score = models.IntegerField(default=0)
    role = models.CharField(choices=USER_ROLE_CHOICES, max_length=10, default='student')
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)


    objects = CustomUserManager()

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = []

    @property
    def full_name(self):

        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.email
