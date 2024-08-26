from django.contrib import messages
from product.models import Product

CART_SESSION_ID = 'cart'


class Cart:
    def __init__(self, request):
        self.request = request
        self.session = request.session
        self.post_price = 40000

        cart = self.session.get(CART_SESSION_ID)
        if not cart:
            cart = self.session[CART_SESSION_ID] = {}

        self.cart = cart

    def __iter__(self):
        cart = self.cart.copy()

        for item in cart.values():
            product = Product.objects.get(id=int(item['id']))
            item['product'] = product
            item['total'] = int(item['quantity']) * int(item['total_price'])
            yield item

    def remove_cart(self):
        self.session[CART_SESSION_ID] = {}

    def add(self, product, quantity):
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0,
                'total_price': product.price,
                'id': product.id,
            }

        total_quantity = int(quantity) + self.cart[product_id]['quantity']
        if total_quantity > product.stock:
            messages.error(self.request,
                           f"متاسفانه موجودی این محصول کمتر از مقدار درخواستی شماست. (موجودی فعلی: {product.stock})")
            return False

        self.cart[product_id]['quantity'] += int(quantity)
        self.save()
        return True

    def delete(self, product_id):
        del self.cart[str(product_id)]
        self.save()

    def total(self):
        cart = self.cart.values()
        total = sum(int(item['total_price']) * int(item['quantity']) for item in cart)
        return total

    def save(self):
        self.session.modified = True
