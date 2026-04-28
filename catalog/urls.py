from django.urls import path

from catalog import views

app_name = "catalog"

urlpatterns = [
    path("gifts/<slug:slug>/", views.gift_detail, name="gift_detail"),
]
