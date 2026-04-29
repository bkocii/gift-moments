from orders.cart import cart_item_count


def cart_context(request):
    return {
        "cart_item_count": cart_item_count(request.session),
    }
