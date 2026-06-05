from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ReportItemForm, ClaimForm, CategoryForm
from .models import Item, Claim, Category
from .utils import match_items
from user.decorators import student_required, admin_required


# Create your views here.



@login_required(login_url='login')
@admin_required
def create_category(request):

    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,'Category added successfully.')
            return redirect('category-list')

    else:
        form = CategoryForm()

    context ={
        'form':form
    }

    return render(request,'admin/create_category.html',context=context)

@login_required(login_url='login')
@admin_required
def update_category(request,id):

    category = get_object_or_404(Category,id=id)
    if request.method == 'POST':
        form = CategoryForm(instance=category)
        if form.is_valid():
            form.save()
            messages.success(request,'Category updated successfully.')
            return redirect('admin-dashboard')

    else:
        form = CategoryForm(instance=category)

    context = {
        'form':form
    }

    return render(request,'admin/update_category.html',context=context)

@login_required(login_url='login')
@admin_required
def category_list(request):

    categories = Category.objects.all()

    return render(request,'admin/category_list.html',{'categories':categories})

@login_required(login_url='login')
@admin_required
def delete_category(request,id):

    category = get_object_or_404(Category, id=id)
    category.delete()
    messages.success(request,'Category deleted successfully.')
    return redirect('category-list')


@login_required(login_url="login")
@student_required
def create_report(request):

    user = request.user
    if request.method == 'POST':
        form = ReportItemForm(request.POST, request.FILES)

        if form.is_valid():
            item = form.save(commit=False)
            item.reported_by = user
            item.college = user.college
            item.save()
            messages.success(request,'Report created successfully.')
            return redirect('student-dashboard')

    else:
        form = ReportItemForm()

    return render(request, 'report/create_report.html', {"form":form})


@login_required(login_url="login")
@student_required
def get_reports(request):
    user = request.user
    items = Item.objects.filter(college=user.college).exclude(reported_by=user).exclude(status='recovered')
    search = request.GET.get('search')

    if search:
        items = Item.objects.filter(college=user.college, item_name__icontains=search).exclude(reported_by=user)


    paginator = Paginator(items,10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj':page_obj
    }

    return render(request, 'report/get_reports.html', context=context)


@login_required(login_url="login")
@student_required
def my_reports(request):

    user = request.user
    items = Item.objects.filter(reported_by=user)

    name = request.GET.get('search')

    if name:
        items = Item.objects.filter(reported_by=user, item_name__icontains=name)

    paginator = Paginator(items, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj':page_obj
    }

    return render(request, 'report/my-reports.html', context=context)

@login_required(login_url='login')
@student_required
def report_detail(request,uuid):

    item = Item.objects.select_related('reported_by','category').get(uuid=uuid)
    active_claim = None
    if request.user.is_authenticated:
        active_claim = Claim.objects.filter(item=item, student=request.user).exclude(status='rejected').first()

    matches = []

    if item.status == 'lost' and request.user == item.reported_by:
        matches = match_items(item)

    context = {

        'item':item,
        'active_claim': active_claim,
        'matches': matches
    }
    return render(request, 'report/report_detail.html', context=context)

@login_required(login_url='login')
@student_required
def claim_report(request,id):

    item = get_object_or_404(Item, id=id)

    if item.reported_by == request.user:
        messages.error(request, "You cannot claim your own report.")
        return redirect('report-detail', id=item.id)

    if item.status in ['lost','recovered']:
        messages.error(request,'Only found item can be claimed.')
        return redirect('report-detail', id=item.id)

    existing_claim = Claim.objects.filter(student=request.user,
                                          item =item,
                                          status__in = ['pending','approved']
                                          ).exists()

    if existing_claim:
        messages.error(request,"Item already claimed.")
        return redirect('report-detail', id=item.id)


    if request.method == 'POST':

        rejected_claim = Claim.objects.filter(student = request.user, item=item).first()

        form = ClaimForm(request.POST, request.FILES)
        if form.is_valid():

            if rejected_claim and rejected_claim.status == 'rejected':
                rejected_claim.verification_answer = form.cleaned_data['verification_answer']
                rejected_claim.status = 'pending'
                rejected_claim.save()

            else:
                claim = form.save(commit=False)
                claim.student = request.user
                claim.item = item
                claim.save()

            messages.success(request,"Item claimed successfully.")
            return redirect('get-reports')


    else:
        form = ClaimForm()

    context = {

        'form':form,
        'item':item
    }

    return render(request,'report/claim_report.html',context=context)


@login_required(login_url='login')
@student_required
def manage_incoming_claims(request):
    incoming_claims = (Claim.objects.select_related('student','item')
                       .filter(
                            item__reported_by=request.user,
                            status='pending')
                       .order_by('-created_at')
                       )

    return render(request, 'report/manage_incoming_claims.html', {
        'incoming_claims': incoming_claims
    })


@login_required
@student_required
def process_claim(request, claim_id):
    claim = get_object_or_404(Claim, id=claim_id, item__reported_by=request.user)

    if request.method == "POST":
        action = request.POST.get('action')

        if action == 'approve':
            claim.status = 'approved'
            claim.save()

            item = claim.item
            item.status = 'recovered'
            item.save()

            messages.success(request, "Claim approved and item marked as Recovered!")

        elif action == 'reject':
            claim.status = 'rejected'
            claim.save()
            messages.info(request, "Claim rejected.")

    return redirect('manage-incoming-claims')

@login_required(login_url='login')
@student_required
def my_claims(request):
    claims = (Claim.objects.select_related('item','item__reported_by')
              .filter(student=request.user)
              .order_by('-created_at')
              )

    status = request.GET.get('status')

    if status:
        claims = (Claim.objects.select_related('item','item__reported_by')
                  .filter(student=request.user, status=status)
                  .order_by('created_at')
                  )

    paginator = Paginator(claims, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj':page_obj
    }
    return render(request,'report/my_claims.html',context=context)