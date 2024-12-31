

import stripe
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