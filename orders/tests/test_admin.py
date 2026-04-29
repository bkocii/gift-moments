import pytest
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from django.core import mail
from django.test import RequestFactory

from orders.admin import (
    OrderAdmin,
    mark_as_cancelled,
    mark_as_confirmed,
    mark_as_delivered,
    mark_as_preparing,
)
from orders.models import Order


def attach_messages_middleware(request):
    session_middleware = SessionMiddleware(lambda req: None)
    session_middleware.process_request(request)
    request.session.save()

    setattr(request, "_messages", FallbackStorage(request))
    return request


@pytest.mark.django_db
def test_order_admin_item_count():
    site = AdminSite()
    admin_instance = OrderAdmin(Order, site)

    order = Order.objects.create(
        sender_name="Burim",
        sender_email="burim@example.com",
        recipient_name="Sara",
        delivery_address="Main street 10",
        total_amount="100.00",
    )

    assert admin_instance.item_count(order) == 0


@pytest.mark.django_db
def test_mark_as_confirmed_action():
    order = Order.objects.create(
        sender_name="Burim",
        sender_email="burim@example.com",
        recipient_name="Sara",
        delivery_address="Main street 10",
        total_amount="100.00",
        status=Order.Status.PENDING,
    )

    modeladmin = OrderAdmin(Order, AdminSite())
    request = RequestFactory().get("/admin/")
    request = attach_messages_middleware(request)
    request.user = get_user_model().objects.create_superuser(
        username="admin1",
        email="admin1@example.com",
        password="testpass123",
    )

    queryset = Order.objects.filter(id=order.id)
    mark_as_confirmed(modeladmin, request, queryset)

    order.refresh_from_db()
    assert order.status == Order.Status.CONFIRMED


@pytest.mark.django_db
def test_mark_as_preparing_action():
    order = Order.objects.create(
        sender_name="Burim",
        sender_email="burim@example.com",
        recipient_name="Sara",
        delivery_address="Main street 10",
        total_amount="100.00",
        status=Order.Status.PENDING,
    )

    modeladmin = OrderAdmin(Order, AdminSite())
    request = RequestFactory().get("/admin/")
    request = attach_messages_middleware(request)
    request.user = get_user_model().objects.create_superuser(
        username="admin2",
        email="admin2@example.com",
        password="testpass123",
    )

    queryset = Order.objects.filter(id=order.id)
    mark_as_preparing(modeladmin, request, queryset)

    order.refresh_from_db()
    assert order.status == Order.Status.PREPARING


@pytest.mark.django_db
def test_mark_as_delivered_action():
    order = Order.objects.create(
        sender_name="Burim",
        sender_email="burim@example.com",
        recipient_name="Sara",
        delivery_address="Main street 10",
        total_amount="100.00",
        status=Order.Status.PENDING,
    )

    modeladmin = OrderAdmin(Order, AdminSite())
    request = RequestFactory().get("/admin/")
    request = attach_messages_middleware(request)
    request.user = get_user_model().objects.create_superuser(
        username="admin3",
        email="admin3@example.com",
        password="testpass123",
    )

    queryset = Order.objects.filter(id=order.id)
    mark_as_delivered(modeladmin, request, queryset)

    order.refresh_from_db()
    assert order.status == Order.Status.DELIVERED


@pytest.mark.django_db
def test_mark_as_cancelled_action():
    order = Order.objects.create(
        sender_name="Burim",
        sender_email="burim@example.com",
        recipient_name="Sara",
        delivery_address="Main street 10",
        total_amount="100.00",
        status=Order.Status.PENDING,
    )

    modeladmin = OrderAdmin(Order, AdminSite())
    request = RequestFactory().get("/admin/")
    request = attach_messages_middleware(request)
    request.user = get_user_model().objects.create_superuser(
        username="admin4",
        email="admin4@example.com",
        password="testpass123",
    )

    queryset = Order.objects.filter(id=order.id)
    mark_as_cancelled(modeladmin, request, queryset)

    order.refresh_from_db()
    assert order.status == Order.Status.CANCELLED


@pytest.mark.django_db
def test_mark_as_confirmed_sends_status_email():
    order = Order.objects.create(
        sender_name="Burim",
        sender_email="burim@example.com",
        recipient_name="Sara",
        delivery_address="Main street 10",
        total_amount="100.00",
        status=Order.Status.PENDING,
    )

    modeladmin = OrderAdmin(Order, AdminSite())
    request = RequestFactory().get("/admin/")
    request = attach_messages_middleware(request)
    request.user = get_user_model().objects.create_superuser(
        username="admin5",
        email="admin5@example.com",
        password="testpass123",
    )

    queryset = Order.objects.filter(id=order.id)
    mark_as_confirmed(modeladmin, request, queryset)

    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == ["burim@example.com"]
    assert "confirmed" in mail.outbox[0].subject.lower()


@pytest.mark.django_db
def test_mark_as_cancelled_sends_status_email():
    order = Order.objects.create(
        sender_name="Burim",
        sender_email="burim@example.com",
        recipient_name="Sara",
        delivery_address="Main street 10",
        total_amount="100.00",
        status=Order.Status.PENDING,
    )

    modeladmin = OrderAdmin(Order, AdminSite())
    request = RequestFactory().get("/admin/")
    request = attach_messages_middleware(request)
    request.user = get_user_model().objects.create_superuser(
        username="admin6",
        email="admin6@example.com",
        password="testpass123",
    )

    queryset = Order.objects.filter(id=order.id)
    mark_as_cancelled(modeladmin, request, queryset)

    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == ["burim@example.com"]
    assert "cancelled" in mail.outbox[0].subject.lower()


@pytest.mark.django_db
def test_order_admin_save_model_sends_email_when_status_changes():
    site = AdminSite()
    admin_instance = OrderAdmin(Order, site)

    order = Order.objects.create(
        sender_name="Burim",
        sender_email="burim@example.com",
        recipient_name="Sara",
        delivery_address="Main street 10",
        total_amount="100.00",
        status=Order.Status.PENDING,
    )

    request = RequestFactory().post("/admin/orders/order/1/change/")
    request = attach_messages_middleware(request)
    request.user = get_user_model().objects.create_superuser(
        username="admin7",
        email="admin7@example.com",
        password="testpass123",
    )

    order.status = Order.Status.CONFIRMED

    class DummyForm:
        cleaned_data = {}

    admin_instance.save_model(request, order, DummyForm(), change=True)

    order.refresh_from_db()
    assert order.status == Order.Status.CONFIRMED
    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == ["burim@example.com"]
    assert "confirmed" in mail.outbox[0].subject.lower()


@pytest.mark.django_db
def test_order_admin_save_model_does_not_send_email_when_status_unchanged():
    site = AdminSite()
    admin_instance = OrderAdmin(Order, site)

    order = Order.objects.create(
        sender_name="Burim",
        sender_email="burim@example.com",
        recipient_name="Sara",
        delivery_address="Main street 10",
        total_amount="100.00",
        status=Order.Status.PENDING,
    )

    request = RequestFactory().post("/admin/orders/order/1/change/")
    request = attach_messages_middleware(request)
    request.user = get_user_model().objects.create_superuser(
        username="admin8",
        email="admin8@example.com",
        password="testpass123",
    )

    class DummyForm:
        cleaned_data = {}

    admin_instance.save_model(request, order, DummyForm(), change=True)

    order.refresh_from_db()
    assert order.status == Order.Status.PENDING
    assert len(mail.outbox) == 0