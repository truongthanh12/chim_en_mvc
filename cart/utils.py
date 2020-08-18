from .models import Order, Favorite, OrderItem, FavoriteProduct
from django.core.exceptions import ObjectDoesNotExist


def get_or_set_order_session(request):
    order_id = request.session.get('order_id', None)

    if order_id is None:
        order = Order()
        order.save()
        request.session['order_id'] = order.id
    else:
        try:
            order = Order.objects.get(id=order_id, ordered=False)
        except ObjectDoesNotExist:
            order = Order()
            order.save()
            request.session['order_id'] = order.id

    if request.user.is_authenticated and order.user is None:
        # xoa het order thuoc user
        delete_order = Order.objects.filter(user=request.user, ordered=False)
        delete_order.delete()

        order.user = request.user
        order.save()
        request.session['order_id'] = order.id

    request.session['products_in_cart'] = OrderItem.objects.filter(
        order=order.id).count() or 0
    return order


def get_or_set_favorite_session(request):
    favorite_id = request.session.get('favorite_id', None)

    if favorite_id is None:
        favorite = Favorite()
        favorite.save()
        request.session['favorite_id'] = favorite.id

    else:
        try:
            favorite = Favorite.objects.get(id=favorite_id)
        except ObjectDoesNotExist:
            favorite = Favorite()
            favorite.save()
            request.session['favorite_id'] = favorite.id

    if request.user.is_authenticated and order.user is None:
        favorite.user = request.user
        favorite.save()

    request.session['products_in_favorite'] = FavoriteProduct.objects.filter(
        favorite=favorite.id).count() or 0
    return favorite
