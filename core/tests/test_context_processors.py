from core.context_processors import cart_context


def test_cart_context_returns_item_count(rf):
    request = rf.get("/")
    request.session = {
        "cart_items": [
            {"name": "Gift 1"},
            {"name": "Gift 2"},
        ]
    }

    context = cart_context(request)

    assert context["cart_item_count"] == 2
