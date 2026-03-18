from django.shortcuts import render, redirect
from django.http import JsonResponse
from apps.customers.models import Customer
from apps.marketing.models import Banner, News
from django.views.decorators.csrf import csrf_exempt

def welcome(request):
    return render(request, 'main/welcome.html', {'hide_nav': True, 'hide_footer': True})

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
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'message': 'Siz allaqachon ro\'yxatdan o\'tgansiz, tizimga kirildi'}, status=200)
            return redirect('home')

        try:
            customer = Customer.objects.create(
                name=name,
                phone=phone,
                email=email,
                telegram=telegram
            )
            request.session['customer_id'] = customer.id
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'message': 'Muvaffaqiyatli ro\'yxatdan o\'tdingiz'}, status=201)
            return redirect('home')
        except Exception as e:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'error': str(e)}, status=500)
            return render(request, 'main/welcome.html', {'error': str(e), 'hide_nav': True, 'hide_footer': True})

    return JsonResponse({'error': 'Noto\'g\'ri so\'rov usuli'}, status=405)

def customer_logout(request):
    if 'customer_id' in request.session:
        del request.session['customer_id']
    return redirect('home')
