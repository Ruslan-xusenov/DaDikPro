from django.shortcuts import render, redirect
from django.http import JsonResponse
from apps.customers.models import Customer
from apps.marketing.models import Banner, News
from django.views.decorators.csrf import csrf_exempt

def home(request):
    banners = Banner.objects.all().order_by('-created_at')
    customer_id = request.session.get('customer_id')
    current_customer = None
    if customer_id:
        current_customer = Customer.objects.filter(id=customer_id).first()
    
    context = {
        'banners': banners,
        'current_customer': current_customer
    }
    return render(request, 'main/index.html', context)

def bonus(request):
    return render(request, 'main/bonus.html')

def support(request):
    return render(request, 'main/support.html')

def news(request):
    news_items = News.objects.all().order_by('-publish_date')
    return render(request, 'main/news.html', {'news': news_items})

@csrf_exempt
def register_customer(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        telegram = request.POST.get('telegram')

        if not name or not phone:
            return JsonResponse({'error': 'Ism va telefon raqami majburiy'}, status=400)

        existing_customer = Customer.objects.filter(phone=phone).first()
        if existing_customer:
            request.session['customer_id'] = existing_customer.id
            return JsonResponse({'message': 'Siz allaqachon ro\'yxatdan o\'tgansiz, tizimga kirildi'}, status=200)

        try:
            customer = Customer.objects.create(
                name=name,
                phone=phone,
                email=email,
                telegram=telegram
            )
            request.session['customer_id'] = customer.id
            return JsonResponse({'message': 'Muvaffaqiyatli ro\'yxatdan o\'tdingiz'}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Noto\'g\'ri so\'rov usuli'}, status=405)

def customer_logout(request):
    if 'customer_id' in request.session:
        del request.session['customer_id']
    return redirect('home')
