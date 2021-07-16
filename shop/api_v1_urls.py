from rest_framework.routers import DefaultRouter

from shop.api_v1_views import ShopsViewSet, CategoriesViewSet, ProductViewSet, CreateWithYamlViewSet, ParametersViewSet, \
    ContactsViewSet, OrdersViewSet, ProductInfoViewSet

router = DefaultRouter()
router.register("shops", ShopsViewSet, basename="all_shops")
router.register("categories", CategoriesViewSet, basename="all_categories")
router.register("products", ProductViewSet, basename="all_products")
router.register("create-yml", CreateWithYamlViewSet, basename="create_yml")
router.register("parameters", ParametersViewSet, basename="all_parameters")
router.register("contacts", ContactsViewSet, basename="contacts")
router.register("orders", OrdersViewSet, basename="orders")
router.register("product-info", ProductInfoViewSet, basename="product_info")


urlpatterns = [] + router.urls
