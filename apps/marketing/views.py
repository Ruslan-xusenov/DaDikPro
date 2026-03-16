import csv
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from apps.customers.models import Customer
from .models import News, Banner, SMSLog
import openpyxl
from openpyxl.styles import Font
from .utils import EskizClient

@login_required
def dashboard_home(request):
    total_customers = Customer.objects.count()
    new_today = Customer.objects.filter(created_at__date=timezone.now().date()).count()
    total_sms = SMSLog.objects.count()
    recent_customers = Customer.objects.all().order_by('-created_at')[:5]
    
    context = {
        'total_customers': total_customers,
        'new_today': new_today,
        'total_sms': total_sms,
        'recent_customers': recent_customers
    }
    return render(request, 'dashboard/home.html', context)

@login_required
def admin_customers(request):
    query = request.GET.get('q')
    if query:
        customers = Customer.objects.filter(
            name__icontains=query
        ) | Customer.objects.filter(
            phone__icontains=query
        ) | Customer.objects.filter(
            email__icontains=query
        )
    else:
        customers = Customer.objects.all().order_by('-created_at')
    
    return render(request, 'dashboard/customers.html', {
        'customers': customers,
        'query': query
    })

@login_required
def admin_sms(request):
    if request.method == 'POST':
        message = request.POST.get('message')
        customers = Customer.objects.all()
        phones = [c.phone for c in customers]
        
        client = EskizClient()
        success_count = 0
        for phone in phones:
            if client.send_sms(phone, message):
                success_count += 1
        
        SMSLog.objects.create(
            message=message,
            total_sent=success_count
        )
        
        messages.success(request, f'SMS kampaniyasi muvaffaqiyatli yakunlandi. {success_count} mijozga xabar yuborildi.')
        return redirect('admin_sms')

    logs = SMSLog.objects.all().order_by('-created_at')
    total_customers = Customer.objects.count()
    return render(request, 'dashboard/sms.html', {
        'sms_logs': logs,
        'total_customers': total_customers
    })

@login_required
def admin_news(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        image = request.FILES.get('image')
        publish_date = request.POST.get('publish_date')
        
        News.objects.create(
            title=title,
            description=description,
            image=image,
            publish_date=publish_date
        )
        messages.success(request, 'News item created successfully!')
        return redirect('admin_news')

    news_items = News.objects.all().order_by('-publish_date')
    return render(request, 'dashboard/news.html', {'news': news_items})

@login_required
def admin_banners(request):
    if request.method == 'POST':
        image = request.FILES.get('image')
        link = request.POST.get('link')
        
        Banner.objects.create(image=image, link=link)
        messages.success(request, 'Banner uploaded successfully!')
        return redirect('admin_banners')

    banners = Banner.objects.all().order_by('-created_at')
    return render(request, 'dashboard/banners.html', {'banners': banners})

@login_required
def export_customers_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="customers_export.xlsx"'

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Customers"

    # Header
    headers = ['ID', 'Name', 'Phone', 'Email', 'Telegram', 'Registration Date']
    ws.append(headers)
    
    for cell in ws[1]:
        cell.font = Font(bold=True)

    # Data
    customers = Customer.objects.all().order_by('-created_at')
    for c in customers:
        ws.append([
            c.id, 
            c.name, 
            c.phone, 
            c.email or '', 
            c.telegram or '', 
            c.created_at.strftime('%Y-%m-%d %H:%M')
        ])

    wb.save(response)
    return response

@login_required
def export_customers_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="customers_export.csv"'

    writer = csv.writer(response)
    writer.writerow(['Name', 'Phone', 'Email', 'Telegram', 'Registration Date'])

    customers = Customer.objects.all()
    for c in customers:
        writer.writerow([c.name, c.phone, c.email, c.telegram, c.created_at])

    return response

@login_required
def admin_add_points(request):
    if request.method == 'POST':
        customer_id = request.POST.get('customer_id')
        amount = request.POST.get('amount')
        
        try:
            customer = Customer.objects.get(id=customer_id)
            customer.points += int(amount)
            customer.save()
            messages.success(request, f"{customer.name}ga {amount} ball muvaffaqiyatli qo'shildi!")
        except (Customer.DoesNotExist, ValueError):
            messages.error(request, "Xatolik: Mijoz topilmadi yoki ball noto'g'ri kiritildi.")
        
        return redirect('admin_add_points')

    return render(request, 'dashboard/add_points.html')

@login_required
def get_customer_info(request):
    customer_id = request.GET.get('id')
    try:
        customer = Customer.objects.get(id=customer_id)
        return JsonResponse({
            'success': True,
            'name': customer.name,
            'current_points': customer.points
        })
    except Customer.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Mijoz topilmadi'})
