from django_filters import rest_framework as filters

from shop.models import Shop, Contacts, Category, ProductParameter, ProductInfo, Product, Order, Parameter


class ShopsFilterSet(filters.FilterSet):

    class Meta:
        model = Shop
        fields = ("id", "name", 'state')


class ContactsFilterSet(filters.FilterSet):

    class Meta:
        model = Contacts
        fields = ("id", "city", 'district', 'street')


class CategoryFilterSet(filters.FilterSet):
    name = filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Category
        fields = ("id", "name")


class ProductParameterFilterSet(filters.FilterSet):

    class Meta:
        model = ProductParameter
        fields = ("parameter", "value")


class ProductInfoFilterSet(filters.FilterSet):

    class Meta:
        model = ProductInfo
        fields = ("price", "price_rrc")


class ProductFilterSet(filters.FilterSet):

    class Meta:
        model = Product
        fields = ("id", "name", )


class OrderFilterSet(filters.FilterSet):

    class Meta:
        model = Order
        fields = ('id', 'created_date', "state")


class ParameterFilterSet(filters.FilterSet):

    class Meta:
        model = Parameter
        fields = ("name", )
