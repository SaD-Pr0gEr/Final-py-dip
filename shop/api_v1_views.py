from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from shop.filters import ShopsFilterSet, CategoryFilterSet, ProductFilterSet, ParameterFilterSet
from shop.models import Shop, Category, Product, Parameter, Order, ProductInfo
from shop.serializers import ShopSerializer, CategorySerializer, ProductSerializer, YamlSerializer, ParameterSerializer, \
    ContactsSerializer, OrderSerializer, CustomProductInfoSerializer
from rest_framework import permissions


class ShopsViewSet(viewsets.ModelViewSet):
    serializer_class = ShopSerializer
    filterset_class = ShopsFilterSet

    def get_permissions(self):
        if self.action in ["retrieve", "list", "create", "update", "delete"]:
            return [permissions.IsAuthenticated()]
        return []

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return Shop.objects.prefetch_related("categories", "user").all()

    def destroy(self, request, *args, **kwargs):
        check_shop = Shop.objects.get(pk=kwargs["pk"])
        if not request.user.is_superuser and not check_shop.user == request.user:
            raise ValidationError("Вы не являетесь владельцом магазина или суперпользователем!")
        return super(ShopsViewSet, self).destroy(request, *args, **kwargs)


class CategoriesViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filterset_class = CategoryFilterSet

    def get_permissions(self):
        if self.action in ["retrieve", "list"]:
            return [permissions.IsAuthenticated()]
        if self.action in ["create", "update", "delete"]:
            return [permissions.IsAdminUser()]
        return []


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.prefetch_related(
        "category",
        "product_info",
        "product_info__shop",
        "product_info__shop__user",
        "product_info__product_parameter",
        "product_info__product_parameter__parameter"
    ).all()
    serializer_class = ProductSerializer
    filterset_class = ProductFilterSet

    def get_permissions(self):
        if self.action in ["list", "retrieve", "create", "update", "delete"]:
            return [permissions.IsAuthenticated()]
        return []

    def perform_create(self, serializer):
        user = self.request.user
        if "url" in self.request.data:
            url = self.request.data['url']
            serializer.save(user=user, url=url)
        serializer.save(user=user)

    def perform_update(self, serializer):
        user = self.request.user
        serializer.save(user=user)


class CreateWithYamlViewSet(viewsets.ModelViewSet):
    serializer_class = YamlSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve", "create", "update", "delete"]:
            return [permissions.IsAuthenticated()]
        return []

    def get_queryset(self):
        user = self.request.user
        get = user.users_shop.all()
        return get

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)

    def destroy(self, request, *args, **kwargs):
        return Response("Нельзя удалить ссылку на файл или сам файл!", status=405)


class ParametersViewSet(viewsets.ModelViewSet):
    queryset = Parameter.objects.all()
    serializer_class = ParameterSerializer
    filterset_class = ParameterFilterSet

    def get_permissions(self):
        if self.action in ["create", "update", "delete"]:
            return [permissions.IsAdminUser()]
        if self.action in ["list", "retrieve"]:
            return [permissions.IsAuthenticated()]
        return []


class ContactsViewSet(viewsets.ModelViewSet):
    serializer_class = ContactsSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve", "create", "update", "delete"]:
            return [permissions.IsAuthenticated()]
        return []

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)

    def perform_update(self, serializer):
        user = self.request.user
        serializer.save(user=user)

    def get_queryset(self):
        user = self.request.user
        return user.contacts.all()


class ProductInfoViewSet(viewsets.ModelViewSet):
    queryset = ProductInfo.objects.all()
    serializer_class = CustomProductInfoSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.IsAuthenticated()]
        return []

    def destroy(self, request, *args, **kwargs):
        return Response("Нельзя удалить информацию о продукте отдельно от самого продукта!", status=405)


class OrdersViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'create', 'update', 'delete']:
            return [permissions.IsAuthenticated()]
        return []

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Order.objects.prefetch_related("positions", "contacts").all()
        return user.order.all()





# return Order.objects.prefetch_related(
#     "contacts",
#     "user",
#     "positions",
#     "positions__product_info",
#     "positions__product_info__shop",
#     "positions__product_info__shop__categories",
#     "positions__product_info__shop__user",
#     "positions__product_info__product_parameter",
#     "positions__product_info__product_parameter__parameter"
# ).all()
