import requests as req
import json

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites import requests
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.views import View
from django.utils import timezone

from .cart_module import Cart
from product.models import Product
from .models import Order, OrderItem
from account.models import Address

PRODUCT = Product


class CartDetailView(View):
    def get(self, request):
        if request.session.get('cart') != {}:
            cart = Cart(request)
        else:
            cart = None
        return render(request, 'order/Cart.html', {'cart': cart})


class CartAddView(View):
    def post(self, request, pk):
        product = get_object_or_404(PRODUCT, id=pk)
        quantity = request.POST.get('quantity')
        cart = Cart(request)
        cart.add(product, quantity)
        return redirect('order:cart_detail')


class CartItemRemoveView(View):
    def get(self, request, pk):
        cart = Cart(request)
        cart.delete(pk)
        return redirect('order:cart_detail')


class CartDeleteView(View):
    def get(self, request):
        cart = Cart(request)
        cart.remove_cart()
        return redirect('order:cart_detail')


class OrderDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        order = get_object_or_404(Order, id=pk)
        address = request.user.addresses.first()
        return render(request, 'order/Checkout.html', {'order': order, 'address': address})


class OrderCreationView(LoginRequiredMixin, View):
    def get(self, request):
        cart = Cart(request)
        user = request.user
        order = None

        # Only pass total_price if post_price is not part of the Order model
        order_data = {
            "total_price": cart.total(),
        }

        unpaid_order = Order.objects.filter(user=user, is_paid=False).first()
        if unpaid_order:
            order = unpaid_order
            order.total_price = order_data["total_price"]
            order.save()
            OrderItem.objects.filter(order=order).delete()
        else:
            order_data['user'] = user
            order = Order.objects.create(**order_data)

        order_items = [
            OrderItem(
                order=order,
                product=item['product'],
                quantity=item['quantity'],
                total_price=item['total'],
            )
            for item in cart
        ]
        OrderItem.objects.bulk_create(order_items)

        # cart.remove_cart()
        return redirect('order:order_detail', order.id)


if settings.SANDBOX:
    sandbox = 'sandbox'
else:
    sandbox = 'www'

ZP_API_REQUEST = f"https://{sandbox}.zarinpal.com/pg/rest/WebGate/PaymentRequest.json"
ZP_API_VERIFY = f"https://{sandbox}.zarinpal.com/pg/rest/WebGate/PaymentVerification.json"
ZP_API_STARTPAY = f"https://{sandbox}.zarinpal.com/pg/StartPay/"

description = "از خرید شما سپاسگذاریم"  # Required
# Important: need to edit for realy server.
call_back_url = 'http://127.0.0.1:8000/cart/order/verify/'


class SendRequestView(View):
    def get(self, request, pk):
        order = get_object_or_404(Order, id=pk, user=request.user)
        request.session['order_id'] = str(order.id)
        data = {
            "MerchantID": settings.MERCHANT,
            "Amount": order.total_price,
            "Description": description,
            "Phone": request.user.phone_number,
            "CallbackURL": call_back_url,
        }
        data = json.dumps(data)
        headers = {'content-type': 'application/json', 'content-length': str(len(data))}
        response = req.post(ZP_API_REQUEST, data=data, headers=headers)

        if response.status_code == 200:
            response = response.json()
            if response['Status'] == 100:
                url = f'{ZP_API_STARTPAY}{response["Authority"]}'
                return redirect(url)
        else:
            HttpResponse(str(response.json()['errors']))


class VerifyOrderView(View):
    def get(self, request):
        authority = request.GET.get('Authority')
        status = request.GET.get('Status')
        order_id = request.session.get('order_id')
        order = Order.objects.get(id=int(order_id))
        data = {
            "MerchantID": settings.MERCHANT,
            "Amount": order.total_price,
            "Authority": authority,
        }
        data = json.dumps(data)
        headers = {'content-type': 'application/json', 'content-length': str(len(data))}
        response = req.post(ZP_API_VERIFY, data=data, headers=headers)
        if response.status_code == 200:
            response = response.json()
            if response['Status'] == 100:
                cart = Cart(request)
                cart.remove_cart()
                order.is_paid = True
                order.payment_date = timezone.now()
                order.ref_id = response["RefID"]
                order.status = Order.STATUS_CHOICES[0][0]
                receiver_info = Address.objects.get(user=request.user, is_active=True)
                order.receiver_info = f'{receiver_info.address}| {receiver_info.postal_code} | {receiver_info.receiver} | {receiver_info.phone}'
                order.save()
                return redirect('account:user_profile')
            else:
                return redirect('order:order_detail', order_id)
        else:
            response = response.json()
            return redirect('order:order_detail', order_id)


