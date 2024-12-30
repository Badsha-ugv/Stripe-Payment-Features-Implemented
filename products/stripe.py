import stripe 
from django.urls import reverse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.conf import settings
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime

from .models import (
    CartItem,
    Cart,
    Coupon,
    Medicine,
    Category,
    Brand,
    PaymentMethod,
    ShippingAddress,
    Order,
    OrderItem
)
from coins.models import Coin, CoinWallet
from subscriptions.models import Packages, Subscription

stripe.api_key = settings.STRIPE_SECRET_KEY

# stripe checkout session create 
@login_required
@require_POST
def create_checkout_session(request):
    try:
        cart = Cart.objects.get(user=request.user)
        print('checkout user',request.user)
        print('checkout cart', cart)

        if not cart.cartitem_set.exists():
            return redirect('cart')
        line_items = []
        for item in cart.cartitem_set.all():
            line_items.append({
                'price_data': {
                    'currency': 'usd',
                    'unit_amount' : int(item.price * 100),
                    'product_data': {
                        'name': item.medicine.name,
                        'description': item.medicine.description,
                        # 'images': [item.medicine.image.url],
                    },
                },
                'quantity': item.quantity,
            })

        checkout = stripe.checkout.Session.create(

            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url= settings.STRIPE_SUCCESS_URL,
            cancel_url=settings.STRIPE_CANCEL_URL,
            metadata = {
                'cart_id': str(cart.id),
                'user_id': str(request.user.id),
                'type': 'product_purchase',
            },
            customer_email=request.user.email,  # Preset customer email
            payment_intent_data={
                'metadata': {
                    'cart_id': str(cart.id),
                    'user_id': str(request.user.id),
                    'type': 'product_purchase',
                },
            }
            # saved_payment_method_options={"payment_method_save": "enabled"},
        )
        return redirect(checkout.url)
    except Exception as e:
        print(f'Error: {e}')
        return redirect('cart')

from django.http import HttpResponse
@csrf_exempt
def stripe_webhooks(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
        print('Webhook event type:', event.type)
        # print('event', event)
    except Exception as e:
        print(f'Webhook error: {e}')
        return HttpResponse(status=400)
    # exit()
    # Handle different event types
    if event.type == 'checkout.session.completed':
        # print('Checkout session completed')
        session = event.data.object  # Extract the session object
        metadata = session.get('metadata', {})
        # user_id = metadata.get('user_id')
        # print('user_id in coin', user_id)
        
        # Handle coin purchase
        if metadata.get('type') == 'coin_purchase':
            try:
                user_id = metadata.get('user_id')
                coin_amount = int(metadata.get('coin_amount', 0))
                user = User.objects.get(id=user_id)
                print('session complete user and coin amount', coin_amount, user)
                # Create or update user's coin wallet
                wallet, created = CoinWallet.objects.get_or_create(user=user)
                wallet.deposit(coin_amount)

                # wallet.balance += coin_amount
                # wallet.save()
                
                # Create coin transaction record if you have such a model
                # Coin.objects.create(
                #     user=user,
                #     amount=coin_amount,
                #     transaction_type='purchase'
                # )
                
                print(f'Coins added successfully: {coin_amount} to user {user.id}')
            except Exception as e:
                print(f'Error processing coin purchase: {e}')
                return HttpResponse(status=400)
        if metadata.get('type') == 'product_purchase':
            user_id = metadata.get('user_id')
            user = User.objects.filter(id=user_id).first()
            cart = Cart.objects.filter(user=user).first()

            if cart:
                # Create order
                order = Order.objects.create(
                    user=user,
                    cart=cart,
                    shipping_address=cart.shipping_address,
                    grand_total=cart.grand_total,
                    discount=cart.discount,
                    subtotal=cart.total
                )
                
                # Create order items
                for cart_item in cart.cartitem_set.all():
                    OrderItem.objects.create(
                        order=order,
                        medicine=cart_item.medicine,
                        quantity=cart_item.quantity,
                        price=cart_item.price,
                        discount=cart_item.medicine.discount
                    )
                cart.clear_cart
                return HttpResponse(status=200)
            else:
                return HttpResponse(status=400)
            

    # exit()

    # if event.type == 'payment_intent.succeeded':
    #     print('PaymentIntent succeeded')
    #     payment_intent = event.data.object
    #     print('PaymentIntent succeeded:', payment_intent.id)
    #     metadata = payment_intent.metadata
    #     print('Payment metadata:', metadata)
        
    #     cart_id = metadata.get('cart_id')
    #     user_id = metadata.get('user_id')
        
    #     if cart_id and user_id:
    #         try:
    #             cart = Cart.objects.get(id=cart_id)
    #             user = User.objects.get(id=user_id)
                
    #             # Create order
    #             order = Order.objects.create(
    #                 user=user,
    #                 cart=cart,
    #                 shipping_address=cart.shipping_address,
    #                 grand_total=cart.grand_total,
    #                 discount=cart.discount,
    #                 subtotal=cart.total
    #             )
                
    #             # Create order items
    #             for cart_item in cart.cartitem_set.all():
    #                 OrderItem.objects.create(
    #                     order=order,
    #                     medicine=cart_item.medicine,
    #                     quantity=cart_item.quantity,
    #                     price=cart_item.price,
    #                     discount=cart_item.medicine.discount
    #                 )
                
    #             # Clear cart after successful order
    #             cart.clear_cart()
    #             print(f'Order created successfully: {order.id}')
                
    #         except Exception as e:
    #             print(f'Error creating order: {e}')
    #             return HttpResponse(status=400)
    
    # elif event.type == 'checkout.session.completed':
    #     session = event.data.object
    #     print('Checkout session completed:', session.id)
    #     # You can add additional handling here if needed
    if event.type == 'customer.subscription.created':
        data = event['data']['object'] 
        metadata = data.get('metadata', {})
        user_id = metadata.get('user_id')
        package_id = metadata.get('package_id')
        stripe_subscription_id = data['id']

        print('user id sub', user_id, package_id, stripe_subscription_id)

        user = User.objects.filter(id=user_id).first()
        package = Packages.objects.get(id=package_id)

        print('userr', user)
        print('package', package)

        Subscription.objects.create(
            user=user,
            package=package,
            stripe_subscriptoin_id=stripe_subscription_id,
            # start_date=data['current_period_start'],
            end_date=datetime.fromtimestamp(data['current_period_end']),
            # status='active',
        )




    return HttpResponse(status=200)

@login_required
@require_POST
def coin_checkout(request):

    coin_amount = request.POST.get('coin_amount', 0)
    # coin_price = request.POST.get('coin_price',0)
    price = int(coin_amount) / 50
    user = request.user
    print('coin amount', coin_amount, price)
    print('user', user)

    if not coin_amount :
        return HttpResponse('Invalid coin amount', status=400)
    checkout = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'unit_amount': int(price * 100),
                'product_data': {
                    'name': 'Coin Purchase',
                    'description': 'Purchase of coins',
                },
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=settings.STRIPE_SUCCESS_URL,
        cancel_url=settings.STRIPE_CANCEL_URL,
        metadata={
            'user_id': str(user.id),
            'coin_amount': str(coin_amount),
            'type': 'coin_purchase'
        },
        customer_email=user.email,
        payment_intent_data={
            'metadata': {
                'user_id': str(user.id),
                'coin_amount': str(coin_amount),
                'type': 'coin_purchase'
            },
        }
    )
    return redirect(checkout.url)



