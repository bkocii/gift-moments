import pytest
from django.contrib.admin.sites import site

from catalog.models import (
    BuildCategory,
    BuildYourOwnPackage,
    GiftBox,
    GiftItem,
    GiftOptionGroup,
    MessageCategory,
    Occasion,
)


@pytest.mark.django_db
def test_catalog_models_registered_in_admin():
    assert Occasion in site._registry
    assert GiftItem in site._registry
    assert GiftBox in site._registry
    assert GiftOptionGroup in site._registry
    assert BuildYourOwnPackage in site._registry
    assert BuildCategory in site._registry
    assert MessageCategory in site._registry
