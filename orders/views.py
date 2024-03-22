from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from .forms import OrderForm
from carts.models import CartItem
from .models import Order, Payment, Order_Product
import datetime
import json
from store.models import Product
from django.core.mail import EmailMessage
from django.template.loader import render_to_string


def place_order(request, total=0, quantity=0):
    current_user = request.user
    
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')
    
    grand_total = 0
    tax = 0
    
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
        
    tax = (2 * total)/100
    grand_total = total + tax
    
    if request.method == 'POST':
        
        data = Order()
        data.user = current_user
        data.first_name = request.POST['first_name']
        data.last_name = request.POST['last_name']
        data.phone = request.POST['phone']
        data.email = request.POST['email']
        data.address_line_1 = request.POST['address_line_1']
        data.address_line_2 = request.POST['address_line_2']
        data.country = request.POST['country']
        data.state = request.POST['state']
        data.city = request.POST['city']
        data.order_note = request.POST['order_note']
        data.order_total = grand_total
        data.tax = tax
        data.ip = request.META.get('REMOTE_ADDR')
        data.save()
        
        
        yr = int(datetime.date.today().strftime('%Y'))
        dt = int(datetime.date.today().strftime('%d'))
        mt = int(datetime.date.today().strftime('%m'))
        d = datetime.date(yr,mt,dt)
        current_date = d.strftime("%Y%m%d")
        order_number = current_date + str(data.id)
        data.order_number = order_number
        data.save()
        
        order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
        
        context = {
            'order': order,
            'cart_items': cart_items,
            'tax': tax,
            'grand_total': grand_total,
            'total': total
        }
        
        return render(request, 'orders/payments.html', context)
        
        # if form.is_valid():
        #     data = Order()
        #     data.user = current_user
        #     data.first_name = form.cleaned_data['first_name']
        #     data.last_name = form.cleaned_data['last_name']
        #     data.phone = form.cleaned_data['phone']
        #     data.email = form.cleaned_data['email']
        #     data.address_line_1 = form.cleaned_data['address_line_1']
        #     data.address_line_2 = form.cleaned_data['address_line_2']
        #     data.country = form.cleaned_data['country']
        #     data.state = form.cleaned_data['state']
        #     data.city = form.cleaned_data['city']
        #     data.order_note = form.cleaned_data['order_note']
        #     data.order_total = grand_total
        #     data.tax = tax
        #     data.ip = request.META.get('REMOTE_ADDR')
        #     data.save()
            
            
        #     yr = int(datetime.date.today().strftime('%Y'))
        #     dt = int(datetime.date.today().strftime('%d'))
        #     mt = int(datetime.date.today().strftime('%m'))
        #     d = datetime.date(yr, dt, mt)
        #     current_date = d.strftime("%Y%m%d")
        #     order_number = current_date + str(data.id)
        #     data.order_number = order_number
        #     data.save()
        #     return redirect('checkout')
        
    else:
        return redirect('checkout')
        
        
        
def payments(request):
    body = json.loads(request.body)
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])
    
    payment = Payment(
        user = request.user,
        payment_id = body['transID'],
        payment_method = body['payment_method'],
        amount_paid = order.order_total,
        status = body['status']
    )
    payment.save()
    
    order.payment = payment
    order.is_ordered = True
    order.save()
    
    cart_items = CartItem.objects.filter(user=request.user)
    
    for item in cart_items:
        order_product = Order_Product()
        order_product.order_id = order.id
        order_product.payment = payment
        order_product.user_id = request.user.id
        order_product.product_id = item.product_id
        order_product.quantity = item.quantity
        order_product.product_price = item.product.price
        order_product.ordered = True
        order_product.save()
        
        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variations.all()
        order_product = Order_Product.objects.get(id=order_product.id)
        order_product.variations.set(product_variation)
        order_product.save()
        
        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()
        
        
    CartItem.objects.filter(user=request.user).delete()
    
    mail_subject = 'Thank you for your order!'
    message = render_to_string('orders/order_received_email.html', {
        'user': request.user,
        'order': order
    })
            
    to_email = request.user.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()
    
    data = {
        'order_number': order.order_number,
        'transID': payment.payment_id
    }
    
    return JsonResponse(data)



def order_complete(request):
    return render(request, 'orders/order_complete.html')