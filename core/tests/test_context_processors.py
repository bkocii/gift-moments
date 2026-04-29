from core.context_processors import cart_context


def test_cart_context_returns_item_count(rf):
    request = rf.get("/")
    request.session = {
        "cart_items": [
            {"name": "Gift 1", "quantity": 1},
            {"name": "Gift 2", "quantity": 1},
        ]
    }

    context = cart_context(request)

    assert context["cart_item_count"] == 2