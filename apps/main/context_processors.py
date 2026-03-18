from apps.customers.models import Customer

def customer_context(request):
    customer_id = request.session.get('customer_id')
    current_customer = None
    if customer_id:
        current_customer = Customer.objects.filter(id=customer_id).first()
    return {
        'current_customer': current_customer
    }