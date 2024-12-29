from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from decimal import Decimal

class Brand(models.Model):
    name = models.CharField(max_length=255)
    logo = models.ImageField(blank=True, null=True, upload_to='images/brand_logo/')

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Medicine(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    description = models.TextField()
    image = models.ImageField(blank=True, null= True, upload_to='images/medicine/')
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.name
    def get_absolute_url(self):
        return reverse('product-detail', kwargs={'pk': self.pk})

class Coupon(models.Model):
    code = models.CharField(max_length=20)
    discount = models.DecimalField(max_digits=10, decimal_places=2)
    user = models.ManyToManyField(User, blank=True, related_name="coupon_user")
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code
class ShippingCharge(models.Model):
    name = models.CharField(max_length=255)
    charge = models.DecimalField(max_digits=10, decimal_places=2)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class ShippingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    zipcode = models.CharField(max_length=255)
    inside_dhaka = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    current = models.BooleanField(default=True)
    def __str__(self):
        return self.address
    

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, blank=True, null=True)
    shipping_address = models.ForeignKey(ShippingAddress, on_delete=models.SET_NULL, blank=True,null=True)

    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} Cart'
    
    @property
    def total(self):
        cart_items = self.cartitem_set.all()
        total = sum([item.total for item in cart_items])
        return total
    def save(self, *args, **kwargs):
        try:
            shipping = ShippingAddress.objects.filter(current=True).first()
            self.shipping_address = shipping
        except ShippingAddress.DoesNotExist:
            pass 

        try:
            cart_items = self.cartitem_set.all()
            total = sum([item.total for item in cart_items])
        except:
            total = 0
            
        if self.coupon and self.coupon.active:
            self.discount = (total * self.coupon.discount) / 100
        self.grand_total = float(total) - float(self.discount)
        super().save(*args, **kwargs)
    
    @property
    def clear_cart(self):
        # delete coupn and discount 
        self.coupon = None
        self.shipping_address = None
        self.discount = 0.00
        self.grand_total = 0.00
        # delete all cart items from database
        self.cartitem_set.all().delete()
        self.save()  # update cart total and discount

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f'{self.medicine.name} in cart'
    
    
    def save(self, *args, **kwargs):
        discount_amouont = (self.medicine.price * self.medicine.discount ) / 100
        self.price = self.medicine.price - discount_amouont
        self.total = self.quantity * self.price
        super().save(*args, **kwargs)
        self.cart.save()
    
    def increment(self, *args, **kwargs):
        self.quantity += 1
        self.save()
    
    def decrement(self, *args, **kwargs):
        if self.quantity > 1:
            self.quantity -= 1
            self.save()
        else:
            self.delete()
    
    def remove(self, *args, **kwargs):
        self.delete()
        self.cart.save()

class PaymentMethod(models.Model):
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name

ORDER_STATUS = (
    ('PENDING', 'PENDING'),
    ('PROCESSING', 'PROCESSING'),
    ('COMPLETED', 'COMPLE'),
    ('CANCELLED', 'CANCELLED'),
)

class Order(models.Model):
    ORDER_PREFIX = 'ORD'
    
    order_id = models.CharField(max_length=50, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=10, choices=ORDER_STATUS, default="PENDING")
    shipping_address = models.ForeignKey(ShippingAddress, on_delete=models.SET_NULL, null=True)
    # payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True)
    
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    # shipping_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2)
    
    payment_status = models.BooleanField(default=False)
    payment_id = models.CharField(max_length=100, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.order_id
    
    def save(self, *args, **kwargs):
        if not self.order_id:
            # Generate order ID: ORD-YYYYMMDD-XXXX
            last_order = Order.objects.all().order_by('-id').first()
            if last_order:
                last_id = int(last_order.order_id.split('-')[-1])
                new_id = last_id + 1
            else:
                new_id = 1
            
            from datetime import datetime
            date_str = datetime.now().strftime('%Y%m%d')
            self.order_id = f'{self.ORDER_PREFIX}-{date_str}-{new_id:04d}'
        
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    medicine = models.ForeignKey(Medicine, on_delete=models.SET_NULL, null=True)
    medicine_name = models.CharField(max_length=255)  # Store name in case medicine is deleted
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.medicine_name} in {self.order.order_id}"
    
    def save(self, *args, **kwargs):
        if self.medicine:
            self.medicine_name = self.medicine.name
            discount_amount = (self.price * Decimal(str(self.discount))) / Decimal('100.0')
            self.total = (self.price - discount_amount) * Decimal(str(self.quantity))
        super().save(*args, **kwargs)