from django.shortcuts import render, redirect
from django.conf import settings
from datetime import datetime
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
# Create your views here.
from .models import Packages, Features, Subscription

import stripe 
stripe.api_key = settings.STRIPE_SECRET_KEY


def subscriptoin(request):
    features = Features.objects.all()
    packages = Packages.objects.all().order_by('-created_at')
    context = {
        'features': features,
        'packages': packages
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
# @require_POST
@csrf_exempt
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
        except stripe.error.StripeError as e:
            # Handle any Stripe API errors
            print(f"Stripe error: {str(e)}")
            return redirect('home')
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
    #     payment_intent_data={
    #     'metadata': {
    #         'user_id': user.id,
    #         'package_id': package_id,
    #     }
    # },

        )
        return redirect(checkout_session.url)
    
    return redirect('home')


# customar portal
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
        return redirect('subscriptions')
    
    session = stripe.billing_portal.Session.create(
        customer=stripe_customer.id,
        return_url=settings.STRIPE_RETURN_URL,
    )
    return redirect(session.url)

# update package price 
def update_package_price(request, package_id):
    if request.method == 'POST':
        package = Packages.objects.get(id=package_id)
        price = int(request.POST['p_price'])
        price_type = request.POST['p_type']

        if package.stripe_price_id:
            stripe.Price.modify(package.stripe_price_id, active=False)
        
        stripe_price = stripe.Price.create(
            product=package.stripe_product_id,
            unit_amount=int(price*100),
            currency='usd',
            recurring={"interval": price_type}
        )
        package.price = price
        package.package_type = price_type
        package.stripe_price_id = stripe_price.id
        package.save()
        return redirect('subscriptions')
    
# cancel subscription

def cancel_subscription(request, subscription_id):
    # set database subscription status to cancel and cancel subscription from stripe    
    subscription = Subscription.objects.get(id=subscription_id)
    subscription.status = 'cancelled'
    subscription.save()
    stripe.Subscription.delete(subscription.stripe_subscriptoin_id)
    return redirect('home')


# delete package 
def delete_package(request, package_id):
    package = Packages.objects.get(id=package_id)
    stripe.Product.delete(package.stripe_product_id)
    package.delete()
    return redirect('subscriptions')