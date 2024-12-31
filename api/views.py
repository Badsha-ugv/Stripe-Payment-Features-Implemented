# make api endpoint for the features
import stripe

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics

from products.models import (
    Brand, Category, Medicine,
    Cart, CartItem
)
from subscriptions.models import (
    Features, Packages, Subscription
)
from .serializers import (
    BrandSerializer, CategorySerializer, MedicineSerializer,
    CartSerializer, FeaturesSerializer, PackagesSerializer
)

class ProductAPIView(APIView):
    def get(self, request, *args, **kwargs):
        products = Medicine.objects.all()
        serializer = MedicineSerializer(products, many=True)
        return Response(serializer.data)
    def post(self, request, *args, **kwargs):
        serializer = MedicineSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class CartAPIView(APIView):
    def get(self, request, *args, **kwargs):
        cart,_ = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    def post(self, request, *args, **kwargs):
        medicine_id = request.data.get('medicine_id')
        quantity = request.data.get('quantity')

        if not medicine_id:
            return Response({'error': 'Medicine id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            medicine = Medicine.objects.get(id=medicine_id)
            cart,_ = Cart.objects.get_or_create(user=request.user)
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                medicine=medicine,
                price=medicine.price
            )
            if not created:
                cart_item.quantity += int(quantity)
                cart_item.save()
            else:
                cart_item.quantity = int(quantity)
            cart_item.save()

            return Response({'message': 'Added to cart successfully'}, status=status.HTTP_201_CREATED)
        except Medicine.DoesNotExist:
            return Response({'error': 'Medicine not found'}, status=status.HTTP_404_NOT_FOUND)
        
class CartItemAPIView(APIView):

    def post(self, request,item_id):
        try:
            cart_item = CartItem.objects.get(id=item_id,cart__user=request.user)
        except CartItem.DoesNotExist:
            return Response({'error': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)
        
        cart_item.increment()
        return Response({'message': 'cart item increment successfully'}, status=status.HTTP_200_OK)
    
    def delete(self, request, item_id):
        try:
            cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
        except CartItem.DoesNotExist:
            return Response({'error': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if cart_item.quantity > 1:
            cart_item.decrement()
            return Response({'message' : 'cart item decrement successfully'}, status=status.HTTP_200_OK)
        else:
            cart_item.remove()
            return Response({'message': 'Cart item deleted successfully'}, status=status.HTTP_200_OK)
        
class PackageAPIView(APIView):
    def get(self, request, *args, **kwargs):
        packages = Packages.objects.all()
        serializer = PackagesSerializer(packages, many=True)
        return Response(serializer.data)
    
    def post(self, request, *args, **kwargs):
        print(request.data)
        serializers = PackagesSerializer(data=request.data)
        if serializers.is_valid():
            name = serializers.validated_data['name']
            price = serializers.validated_data['price']
            package_type = serializers.validated_data['package_type']
            features_list = serializers.validated_data['features']
            
            product = stripe.Product.create(name=name)
            stripe_price = stripe.Price.create(
                product=product.id,
                unit_amount= int(price * 100),
                currency='usd',
                recurring={"interval": package_type}
            )
            package = Packages.objects.create(
                name=name,
                price=price,
                package_type=package_type,
                stripe_product_id=product.id,
                stripe_price_id=stripe_price.id
            )
            package.features.set(features_list)
            package.save()
            return Response(serializers.data, status=status.HTTP_201_CREATED)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
    

# class SubscriptionList(generics.ListAPIView):
#     def get_queryset(self):
#         return Subscription.objects.filter(user=self.request.user, status='active')
    