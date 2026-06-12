from functools import wraps

from django.http import Http404
from django.shortcuts import redirect


def admin_required(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff:
            #return redirect('home')
            raise Http404("Page not found.")
        return func(request, *args, **kwargs)
    return wrapper


def college_required(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not request.user.role == 'college':
            #return redirect('home')
            raise Http404("Page not found.")
        return func(request, *args, **kwargs)
    return wrapper

def student_required(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not request.user.role =='student':
            #return redirect('home')
            raise Http404("Page not found.")
        return func(request, *args, **kwargs)
    return wrapper
