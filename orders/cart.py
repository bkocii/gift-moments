from decimal import Decimal

CART_SESSION_KEY = "cart_items"


def get_cart(session):
    return session.get(CART_SESSION_KEY, [])


def save_cart(session, cart_items):
    session[CART_SESSION_KEY] = cart_items
    session.modified = True


def _cart_item_identity(item):
    item_type = item.get("item_type", "gift_box")

    if item_type == "build_your_own":
        return (
            item_type,
            item["package_id"],
            item["recipient_name"],
            item["gift_message"],
            item["delivery_date"],
            item["unit_price"],
            item["selected_options"],
        )

    return (
        item_type,
        item["gift_box_id"],
        item["recipient_name"],
        item["gift_message"],
        item["delivery_date"],
        item["unit_price"],
        item["selected_options"],
    )


def add_to_cart(session, item_data):
    cart_items = get_cart(session)
    new_identity = _cart_item_identity(item_data)

    for existing_item in cart_items:
        if _cart_item_identity(existing_item) == new_identity:
            existing_quantity = int(existing_item["quantity"])
            added_quantity = int(item_data["quantity"])
            new_quantity = existing_quantity + added_quantity

            unit_price = Decimal(str(existing_item["unit_price"]))
            existing_item["quantity"] = new_quantity
            existing_item["line_total"] = str(unit_price * new_quantity)

            save_cart(session, cart_items)
            return

    cart_items.append(item_data)
    save_cart(session, cart_items)


def update_cart_item_quantity(session, index, quantity):
    cart_items = get_cart(session)

    if 0 <= index < len(cart_items):
        if quantity <= 0:
            cart_items.pop(index)
        else:
            cart_items[index]["quantity"] = quantity
            unit_price = Decimal(str(cart_items[index]["unit_price"]))
            cart_items[index]["line_total"] = str(unit_price * quantity)

        save_cart(session, cart_items)


def remove_from_cart(session, index):
    cart_items = get_cart(session)

    if 0 <= index < len(cart_items):
        cart_items.pop(index)
        save_cart(session, cart_items)


def clear_cart(session):
    session[CART_SESSION_KEY] = []
    session.modified = True


def cart_item_count(session):
    return sum(int(item.get("quantity", 0)) for item in get_cart(session))


def cart_total(session):
    total = Decimal("0.00")

    for item in get_cart(session):
        total += Decimal(str(item["line_total"]))

    return total
