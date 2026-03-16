from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from apps.customers.models import Customer
from .models import News, Banner, SMSLog
from .serializers import (
    CustomerSerializer, NewsSerializer, 
    BannerSerializer, SMSLogSerializer
)
from .utils import EskizClient

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all().order_by('-created_at')
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated]

class NewsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = News.objects.all().order_by('-publish_date')
    serializer_class = NewsSerializer

class BannerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Banner.objects.all().order_by('-created_at')
    serializer_class = BannerSerializer

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def send_bulk_sms_api(request):
    message = request.data.get('message')
    if not message:
        return Response({'error': 'Xabar matni kerak'}, status=status.HTTP_400_BAD_REQUEST)
    
    customers = Customer.objects.all()
    phones = [c.phone for c in customers]
    
    client = EskizClient()
    success_count = 0
    for phone in phones:
        if client.send_sms(phone, message):
            success_count += 1
            
    SMSLog.objects.create(message=message, total_sent=success_count)
    return Response({'success': True, 'sent_count': success_count})

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def add_points_api(request):
    customer_id = request.data.get('customer_id')
    points = request.data.get('points')
    
    try:
        customer = Customer.objects.get(id=customer_id)
        customer.points += int(points)
        customer.save()
        return Response({'success': True, 'new_points': customer.points, 'customer_name': customer.name})
    except (Customer.DoesNotExist, ValueError):
        return Response({'success': False, 'message': 'Mijoz topilmadi yoki ball noto\'g\'ri'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def dashboard_stats_api(request):
    return Response({
        'total_customers': Customer.objects.count(),
        'total_sms': SMSLog.objects.count(),
        'news_count': News.objects.count()
    })
