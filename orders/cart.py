from decimal import Decimal

CART_SESSION_KEY = "cart_items"


def get_cart(session):
    return session.get(CART_SESSION_KEY, [])


def save_cart(session, cart_items):
    session[CART_SESSION_KEY] = cart_items
    session.modified = True


def add_to_cart(session, item_data):
    cart_items = get_cart(session)
    cart_items.append(item_data)
    save_cart(session, cart_items)


def remove_from_cart(session, index):
    cart_items = get_cart(session)

    if 0 <= index < len(cart_items):
        cart_items.pop(index)
        save_cart(session, cart_items)


def cart_item_count(session):
    return len(get_cart(session))


def cart_total(session):
    total = Decimal("0.00")

    for item in get_cart(session):
        total += Decimal(str(item["line_total"]))

    return total
