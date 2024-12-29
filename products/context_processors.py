# total cart items count 

from products.models import CartItem

def cart_item_count(request):
    cart_item_count = CartItem.objects.filter(cart__user=request.user).count()
    return {'cart_item_count': cart_item_count}