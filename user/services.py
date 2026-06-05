from django.conf import settings
from django.core.mail import send_mail


def send_approval_email(user):

    send_mail(
        subject="Account Approved",
        message=f"Hi {user.full_name}, your account has been approved. you can log in to your account.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False
    )

def send_rejection_email(user):

    send_mail(
        subject="Account Rejected",
        message=f"Hi {user.full_name}, your account has been rejected. please contact college administration.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False
    )