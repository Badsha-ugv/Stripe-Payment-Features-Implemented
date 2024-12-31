

import stripe
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse


from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

from products.models import (
    Cart,
    CartItem, 
    Medicine,

)
from subscriptions.models import (
    Packages,
    Subscription,
)


stripe.api_key = settings.STRIPE_SECRET_KEY



# @login_required
@api_view(['POST'])
def coin_checkout(request):

    coin_amount = request.data.get('coin_amount', 0)
    # coin_price = request.POST.get('coin_price',0)
    price = int(coin_amount) / 50
    user = request.user
    print('coin amount api', coin_amount, price)
    print('user api', user)

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
    response_data = {
        'status': status.HTTP_200_OK,
        'message': 'Checkout session created successfully',
        'url': checkout.url,
    }
    return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
def create_checkout_session(request):
    try:
        cart = Cart.objects.get(user=request.user)
        print('checkout user',request.user)
        print('checkout cart', cart)

        if not cart.cartitem_set.exists():
            return Response({"message": "Cart items is empty"}, status=status.HTTP_404_NOT_FOUND)
        
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
        response_data = {
            "status": status.HTTP_200_OK,
            "message": "success",
            "url" : checkout.url,
        }
        return Response(response_data)
    except Exception as e:
        print(f'Error: {e}')
        return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "something went wrong"})
    
@api_view(['POST'])
def subscriptoin_checkout(request, package_id):
    user = request.user
    print('user from api ', user)
    package = Packages.objects.get(id=package_id)
    # Get or create Stripe customer
    try:
        # Search for existing customer by email
        customers = stripe.Customer.list(email=user.email)
        if customers.data:
            stripe_customer = customers.data[0]
        else:
            # Create new customer if not found
            stripe_customer = stripe.Customer.create(
                email=user.email,
                name=f"{user.first_name} {user.last_name}"
            )
    except stripe.error.StripeError as e:
        # Handle any Stripe API errors
        print(f"Stripe error: {str(e)}")
        return Response({'status': status.HTTP_400_BAD_REQUEST})
    
    # fetch current subscription
    try:
        current_subscription = Subscription.objects.get(user=user, status='active')
        stripe_subscription = stripe.Subscription.retrieve(current_subscription.stripe_subscriptoin_id)
    except Subscription.DoesNotExist:
        current_subscription = None
        stripe_subscription = None
    
    if stripe_subscription:
        try:
            update_subscription = stripe.Subscription.modify(
                stripe_subscription.id,
                items=[{
                    'id': stripe_subscription['items']['data'][0].id,
                    'price': package.stripe_price_id
                }],
                proration_behavior='create_prorations',
            )
            current_subscription.status = 'cancelled'
            current_subscription.save()

            new_subscription = Subscription.objects.create(
                user=user,
                package=package,
                stripe_subscriptoin_id=update_subscription.id,
                end_date=datetime.fromtimestamp(update_subscription['current_period_end']),
                status='active',
            )
            return Response({'status': status.HTTP_200_OK,'message': 'Subscription cancelled and new one created'})
        except stripe.error.StripeError as e:
            # Handle any Stripe API errors
            print(f"Stripe error: {str(e)}")
            return Response({'status': status.HTTP_400_BAD_REQUEST})
    else:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            mode='subscription',
            line_items=[{'price':package.stripe_price_id, 'quantity': 1}],
            customer=stripe_customer.id,
            success_url=settings.STRIPE_SUCCESS_URL,
            cancel_url=settings.STRIPE_CANCEL_URL,
            metadata={'package_id': str(package_id), 'user_id': str(user.id)},
            subscription_data={
            'metadata': {
                'user_id':str(user.id),
                'package_id': str(package_id),
            }
        },

        )
        response_data = {
            "status": status.HTTP_200_OK,
            "message": "success",
            "url" : checkout_session.url,
        }
        return Response(response_data)
    
    # return Response()
@api_view(['GET'])
def customer_portal(request):
    user = request.user
    try:
        # Search for existing customer by email
        customers = stripe.Customer.list(email=user.email)
        if customers.data:
            stripe_customer = customers.data[0]
        else:
            # Create new customer if not found
            stripe_customer = stripe.Customer.create(
                email=user.email,
                name=f"{user.first_name} {user.last_name}"
            )
    except stripe.error.StripeError as e:
        # Handle any Stripe API errors
        print(f"Stripe error: {str(e)}")
        return Response('subscriptions error')
    
    session = stripe.billing_portal.Session.create(
        customer=stripe_customer.id,
        return_url=settings.STRIPE_RETURN_URL,
    )
    response_data = {
        "status": status.HTTP_200_OK,
        "message": "success",
        "url": session.url,
    }
    return Response(response_data)
@api_view(['POST'   ])
def cancel_subscription(request, subscription_id):
    # set database subscription status to cancel and cancel subscription from stripe    
    subscription = Subscription.objects.get(id=subscription_id)
    subscription.status = 'cancelled'
    subscription.save()
    stripe.Subscription.delete(subscription.stripe_subscriptoin_id)
    response_data = {
        "status": status.HTTP_200_OK,
        "message": "Subscription cancelled successfully"
    }
    return Response(response_data)