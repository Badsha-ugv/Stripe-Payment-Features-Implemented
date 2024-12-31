from rest_framework import serializers
from products.models import Brand, Category, Medicine, Cart, CartItem
from subscriptions.models import Features, Packages
class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class MedicineSerializer(serializers.ModelSerializer):
    brand_id = serializers.PrimaryKeyRelatedField(
        queryset=Brand.objects.all(),
        source='brand',
        write_only=True
    )
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True
    )
    brand = BrandSerializer(read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Medicine
        fields = '__all__'

class CartItemSerializer(serializers.ModelSerializer):
    
    medicine = MedicineSerializer()
    class Meta:
        model = CartItem
        fields = '__all__'


class CartSerializer(serializers.ModelSerializer):
    cart_items = CartItemSerializer(
        source='cartitem_set',
        many=True
    )

    class Meta:
        model = Cart
        fields = ['id', 'grand_total', 'discount', 'coupon', 'shipping_address', 'cart_items']



class FeaturesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Features
        fields = '__all__'

class PackagesSerializer(serializers.ModelSerializer):
    features_id = serializers.ListField( 
        child=serializers.PrimaryKeyRelatedField(queryset=Features.objects.all()), source='features', write_only=True )

    features = FeaturesSerializer(read_only=True,many=True)
    class Meta:
        model = Packages
        fields = '__all__'

    

