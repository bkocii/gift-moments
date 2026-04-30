import pytest
from django.contrib.admin.sites import site

from catalog.models import (
    GiftBox,
    GiftBoxImage,
    GiftItem,
    GiftOptionGroup,
    Occasion,
)


@pytest.mark.django_db
def test_catalog_models_registered_in_admin():
    assert Occasion in site._registry
    assert GiftItem in site._registry
    assert GiftBox in site._registry
    assert GiftOptionGroup in site._registry
