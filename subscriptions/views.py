from django.shortcuts import render, redirect
from django.conf import settings
# Create your views here.
from .models import Packages, Features, Subscription

import stripe 
stripe.api_key = settings.STRIPE_SECRET_KEY


def subscriptoin(request):
    features = Features.objects.all()
    context = {
        'features': features
    }
    return render(request, 'subscriptions/subscriptions.html',context)

def create_feature(request):
    if request.method == 'POST':
        name = request.POST['f_name']
        print('name', name)
        Features.objects.create(name=name)
        return redirect('subscriptions')
    
def create_packages(request):
    if request.method == 'POST':
        name = request.POST['p_name']
        price = int(request.POST['p_price'])
        type = request.POST['p_type']
        features_list = request.POST.getlist('features')
        
        product = stripe.Product.create(
            name=name,
        )
        stripe_price = stripe.Price.create(
            product=product.id,
            unit_amount=int(price*100),
            currency='usd',
            recurring={"interval": type}
        )

        package = Packages.objects.create(
            name=name,
            price=price,
            package_type=type,
            stripe_product_id=product.id,
            stripe_price_id=stripe_price.id

        )
        package.features.set(Features.objects.filter(id__in=features_list))
        package.save()

        return redirect('subscriptions')
    
def subscriptoin_checkout(request, package_id):
    user = request.user
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
        return redirect('subscriptions')
    
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
    #     payment_intent_data={
    #     'metadata': {
    #         'user_id': user.id,
    #         'package_id': package_id,
    #     }
    # },

    )
    return redirect(checkout_session.url)
