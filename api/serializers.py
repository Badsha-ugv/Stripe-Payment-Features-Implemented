from rest_framework import serializers
from products.models import Brand, Category, Medicine, Cart, CartItem

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
            

