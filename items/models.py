from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from user.models import College
import uuid

# Create your models here.

User = get_user_model()


class Category(models.Model):

    name = models.CharField(max_length=225)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

class Item(models.Model):

    STATUS_CHOICES = [
        ('lost','Lost'),
        ('found','Found'),
        ('recovered','Recovered')
    ]

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="items")
    item_name = models.CharField(max_length=225)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField()
    image = models.ImageField(upload_to='items/', null=True, blank=True)
    location = models.CharField(max_length=225)
    status = models.CharField(max_length=12,choices=STATUS_CHOICES, default='lost')
    college = models.ForeignKey(College,on_delete=models.CASCADE)
    verification_question = models.CharField(max_length=225,blank=True)
    date_happened = models.DateTimeField(default=timezone.localdate)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Claim(models.Model):

    CLAIM_STATUS_CHOICES = [
        ('pending','Pending'),
        ('approved','Approved'),
        ('rejected','Rejected')
    ]

    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="claims")
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="claims")
    verification_answer = models.CharField(max_length=225)
    proof_image = models.ImageField(upload_to='claims/', blank=True, null=True)
    status = models.CharField(max_length=12,choices=CLAIM_STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student','item')

    def __str__(self):
        return f"claimed by {self.student.full_name} for {self.item.item_name}."