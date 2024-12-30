from django.shortcuts import render, redirect
from .models import CartItem, Cart, Coupon


from .models import Medicine, Category, Brand, PaymentMethod, Order, OrderItem
from .forms import MedicineForm
from .models import ShippingAddress
from coins.models import CoinWallet
from subscriptions.models import Packages, Subscription

def home(request):
    medicines = Medicine.objects.all()
    wallet = CoinWallet.objects.filter(user=request.user).first()
    packages = Packages.objects.all()
    subscription = Subscription.objects.filter(user=request.user, status='active').first()

    context = {
        'medicines': medicines,
        'wallet': wallet,
        'packages': packages,
        'subscription': subscription
    }
    return render(request, 'home.html', context)

def product_details(request,pk):
    medicine = Medicine.objects.get(id=pk)
    context = {
        'medicine': medicine
    }
    return render(request, 'products/product_details.html', context)

def cart(request):
    cart_items = CartItem.objects.filter(cart__user=request.user)
    cart = Cart.objects.get(user=request.user)
    shipping_address = ShippingAddress.objects.filter(user=request.user)
    context = {
        'cart_items': cart_items,
        'cart': cart,
        'shipping_address': shipping_address
    }
    return render(request, 'products/cart.html', context)

def add_to_cart(request, pk):
    medicine = Medicine.objects.get(id=pk)
    cart, created = Cart.objects.get_or_create(user=request.user)
    #  if cart is empty, delete coupon
    
    cart_item, created = CartItem.objects.get_or_create(cart=cart, medicine=medicine, price=medicine.price)
    if not created:
        cart_item.increment()
    return redirect('cart')

def increment_cart(request, pk):
    cart_item = CartItem.objects.get(id=pk)
    cart_item.increment()
    return redirect('cart')

def decrement_cart(request, pk):
    cart_item = CartItem.objects.get(id=pk)
    cart_item.decrement()
    return redirect('cart')

def remove_from_cart(request, pk):
    cart_item = CartItem.objects.get(id=pk)
    cart = Cart.objects.get(user = request.user)
    
    cart_item.remove()
    if cart.cartitem_set.count() == 0:
        cart.clear_cart

    return redirect('cart')

def apply_coupon(request):
    if request.method == 'POST':
        user = request.user
        code = request.POST['coupon_code']
        coupon = Coupon.objects.filter(code__iexact=code).first()
        
        if coupon.active:
            if user in coupon.user.all():
                # messages.warning(request,'Coupon already used')
                return redirect('cart')
            coupon.user.add(request.user)

            cart = Cart.objects.get(user=user)
            cart.coupon = coupon
            cart.save()
        
    return redirect('cart')

def place_order(request):
    cart = Cart.objects.get(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    shipping_address = ShippingAddress.objects.filter(user=request.user, current=True).first()
    payment_methods = PaymentMethod.objects.all()

    if request.method == 'POST':
        order = Order.objects.create(
            user=request.user, 
            cart=cart,
            shipping_address=cart.shipping_address,
            grand_total= cart.grand_total,
            discount=cart.discount,
            subtotal=cart.total
            )
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order, 
                medicine=cart_item.medicine,
                quantity=cart_item.quantity,
                price = cart_item.price,
                discount  = cart_item.medicine.discount

                )
        cart.clear_cart
        return redirect('order-success')
    elif not shipping_address:
        return redirect('cart')
    elif not cart_items.exists():
        return redirect('cart')
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'address': shipping_address,
        'payment_methods': payment_methods
        
    }
    return render(request, 'products/checkout_page.html', context)


def order_success(request):
    return render(request, 'products/order_success.html')

def order_cancel(request):
    return render(request, 'products/order_cancel.html')