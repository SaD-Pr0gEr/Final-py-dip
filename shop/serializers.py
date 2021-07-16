import yaml
from django.conf import settings
from django.core import files
from django.db.models import Sum
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from rest_framework.response import Response

from shop.download import get_download_link, download_file, get_filename
from shop.models import User, Contacts, Category, Product, ProductInfo, Parameter, ProductParameter, Order, OrderItem, \
    Shop


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "user_type")


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name")
        read_only_fields = ("id",)

    def create(self, validated_data):
        name = validated_data.pop("name")
        uppercase_letter = name.capitalize()
        validated_data["name"] = uppercase_letter
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if validated_data["name"]:
            name = validated_data.pop("name")
            uppercase_letter = name.capitalize()
            validated_data["name"] = uppercase_letter
        return super().update(instance, validated_data)


class ShopSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    categories = CategorySerializer(read_only=True, many=True)

    class Meta:
        model = Shop
        fields = ("id", "name", "user", "state", "categories")
        read_only_fields = ("id", "user",)

    def create(self, validated_data):
        user = validated_data["user"]
        shop = Shop.objects.filter(user=user).all()
        if user.user_type != "Seller":
            raise serializers.ValidationError("Вы не продавец! Поменяйте свой user_type на продавца!")
        if len(shop) >= 1:
            raise serializers.ValidationError("У вас не может быть более 1го магазина!")
        return super().create(validated_data)

    def update(self, instance, validated_data):
        creator = instance.user
        if validated_data["user"] != creator:
            raise serializers.ValidationError("Вы не являетесь владельцем магазина!")
        return super().update(instance, validated_data)


class ContactsSerializer(serializers.ModelSerializer):
    # user = UserSerializer(read_only=True)

    class Meta:
        model = Contacts
        fields = ("city", "district", "street", "house", "building", "phone")
        read_only_fields = ("user",)


class ParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parameter
        fields = ("name",)

    def create(self, validated_data):
        name = validated_data.pop("name")
        uppercase_letter = name.capitalize()
        validated_data["name"] = uppercase_letter
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if validated_data["name"]:
            name = validated_data.pop("name")
            uppercase_letter = name.capitalize()
            validated_data["name"] = uppercase_letter
        return super().update(instance, validated_data)


class ProductParameterSerializer(serializers.ModelSerializer):
    parameter = ParameterSerializer()

    class Meta:
        model = ProductParameter
        fields = ("parameter", "value")


class ProductInfoSerializer(serializers.ModelSerializer):
    product_parameter = ProductParameterSerializer(many=True)
    shop = ShopSerializer(read_only=True)

    # def get_total_sum(self, obj):
    #     return obj.total_sum
    # total_sum = SerializerMethodField(read_only=True)

    class Meta:
        model = ProductInfo
        fields = ("shop", "quantity", "price", "price_rrc", "product_parameter")


class CustomProductInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductInfo
        fields = ("id", "product", "shop", "quantity", "price", "price_rrc")

    def create(self, validated_data):
        return Response("Нельзя создать информацию о продукте отдельно!", status=405)

    def update(self, instance, validated_data):
        return Response("Нельзя обновить информацию о продукте отдельно!", status=405)


class ProductSerializer(serializers.ModelSerializer):
    product_info = ProductInfoSerializer(many=True)
    category = CategorySerializer()

    class Meta:
        model = Product
        fields = ("id", "name", "product_info", "category")
        read_only_fields = ("id",)

    def create(self, validated_data):
        user = validated_data["user"]
        check_shop = Shop.objects.filter(user=user).first()
        if not check_shop:
            raise serializers.ValidationError("У вас нет магазина! Сначала создайте её!")
        get_product_info = validated_data.pop("product_info")
        pop_parameters = get_product_info[0].pop("product_parameter")
        parameters_list = []
        for parameter in pop_parameters:
            get_parameter = Parameter.objects.filter(name=parameter['parameter']["name"]).first()
            if not get_parameter:
                raise serializers.ValidationError(
                    "Такого параметра нет! Проверьте заглавные буквы! Они должны быть на вверхним регистре")
            params_dict = {"parameter": get_parameter, "value": parameter["value"]}
            parameters_list.append(params_dict)
        validated_data.pop("user")
        get_category = validated_data.pop("category")
        check_category = Category.objects.filter(name=get_category["name"]).first()
        if not check_category:
            raise serializers.ValidationError(
                "Такой категории нет! Проверьте заглавные буквы! Они должны быть на вверхним регистре")
        validated_data["category"] = check_category
        create_product = super().create(validated_data)
        data_for_create_product_info = {
            "product": create_product,
            "shop": check_shop,
            "quantity": get_product_info[0]["quantity"],
            "price": get_product_info[0]["price"],
            "price_rrc": get_product_info[0]["price_rrc"],
        }
        create_product_info = ProductInfo.objects.create(**data_for_create_product_info)
        for create_products_param in parameters_list:
            ProductParameter.objects.create(
                product_info=create_product_info,
                parameter=create_products_param["parameter"],
                value=create_products_param["value"]
            )
        return create_product


class OrderItemSerializer(serializers.ModelSerializer):
    # def get_total_order_sum(self, obj):
    #     return obj.sum
    #
    # total_order_sum = SerializerMethodField(read_only=True)

    class Meta:
        model = OrderItem
        fields = ("id", "product_info", "quantity",)
        read_only_fields = ("id", )


class OrderSerializer(serializers.ModelSerializer):

    # def get_total_order_sum(self, obj):
    #     return obj.sum

    contacts = ContactsSerializer()
    positions = OrderItemSerializer(many=True)
    # total_order_sum = SerializerMethodField(read_only=True)

    class Meta:
        model = Order
        fields = ("id", "positions", "created_date", "state", "contacts", )
        read_only_fields = ("id", "positions", "contacts")

    def create(self, validated_data):
        pop_positions = validated_data.pop("positions")
        positions_list = []
        for check_positions in pop_positions:
            quantity_in_stock = check_positions['product_info']
            if quantity_in_stock.quantity < check_positions['quantity']:
                raise serializers.ValidationError("Количество заказанных товаров больше чем количество товаров в наличии!")
            ready_to_create = OrderItem(product_info=check_positions['product_info'], quantity=check_positions['quantity'])
            quantity_in_stock.quantity -= check_positions['quantity']
            quantity_in_stock.save()
            positions_list.append(ready_to_create)
        pop_contacts = validated_data.pop("contacts")
        create_contacts = Contacts.objects.create(user=validated_data['user'], **pop_contacts)
        validated_data['contacts'] = create_contacts
        create_order = super().create(validated_data)
        for append_order in positions_list:
            append_order.order = create_order
        OrderItem.objects.bulk_create(positions_list)
        return create_order


class YamlSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ("url",)

    def create(self, validated_data):
        user = validated_data["user"]
        check_shop = Shop.objects.filter(user=user).first()
        url = validated_data["url"]
        get_link = get_download_link(url)
        if not get_link:
            raise serializers.ValidationError("По вашему Url нет никакого документа!")
        download = download_file(get_link)
        if not download:
            raise serializers.ValidationError("Не удалось записать на файл")
        filename = get_filename(get_link)
        check_shop.url = url
        check_shop.filename.save(f"{filename}", files.File(download))
        with open(f"{settings.BASE_DIR}{settings.MEDIA_URL}{check_shop.filename}", encoding="utf-8") as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
        data_for_create_product = []
        for get_data in data:
            ready_data = {
                "product": get_data["name"],
                "category": get_data["category"]["name"],
                "info": get_data["product_info"],
                "parameter": get_data["product_parameter"]
            }
            data_for_create_product.append(ready_data)
        for create_product in data_for_create_product:
            check_category = Category.objects.filter(name=create_product["category"]).first()
            if not check_category:
                raise serializers.ValidationError(f"Такой категории нет! Проверьте её на заглавные буквы!")
            create_product["category"] = check_category
            create = Product.objects.create(
                name=create_product["product"],
                category=create_product["category"]
            )
            create_info = ProductInfo.objects.create(
                product=create,
                shop=check_shop,
                quantity=create_product["info"]["quantity"],
                price=create_product["info"]["price"],
                price_rrc=create_product["info"]["price"]
            )
            for parameter in create_product['parameter']:
                check_param = Parameter.objects.filter(name=parameter["parameter"]["name"]).first()
                if not check_param:
                    raise serializers.ValidationError(f"Такого параметра нет! Проверьте её на заглавные буквы! Они "
                                                      f"должны быть на вверхним регистре! И проверьте есть ли вообще такой "
                                                      f"параметр!")
                ProductParameter.objects.create(
                    product_info=create_info,
                    parameter=check_param,
                    value=parameter["value"]
                )
        return super().data

    def update(self, instance, validated_data):
        return Response("Нельзя обновить ссылку или название файла! Можно только создать!", status=405)
