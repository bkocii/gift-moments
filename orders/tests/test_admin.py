import pytest
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.test import RequestFactory

from orders.admin import (
    OrderAdmin,
    mark_as_cancelled,
    mark_as_confirmed,
    mark_as_delivered,
    mark_as_preparing,
)
from orders.models import Order


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
    request.user = get_user_model().objects.create_superuser(
        username="admin4",
        email="admin4@example.com",
        password="testpass123",
    )

    queryset = Order.objects.filter(id=order.id)
    mark_as_cancelled(modeladmin, request, queryset)

    order.refresh_from_db()
    assert order.status == Order.Status.CANCELLED
