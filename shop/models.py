from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


USER_TYPE_CHOICES = (
    ("Seller", "Магазин"),
    ("Buyer", "Покупатель"),
)


STATE_CHOICES = (
    ('new', 'Новый'),
    ('confirmed', 'Подтвержден'),
    ('assembled', 'Собран'),
    ('sent', 'Отправлен'),
    ('delivered', 'Доставлен'),
    ('canceled', 'Отменен'),
)


class User(AbstractUser):
    """Модель пользователя"""

    username = models.CharField(
        _('username'),
        max_length=150,
        unique=False,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    user_type = models.TextField(
        verbose_name="Тип пользователя",
        choices=USER_TYPE_CHOICES,
        blank=False,
        null=False
    )
    email = models.EmailField(_('email address'), blank=False, null=False, unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ["username", "user_type"]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Список пользователей"

    def __str__(self):
        return f"{self.username}"


class Shop(models.Model):
    """Модель магазина"""

    name = models.CharField(verbose_name="Название", max_length=80)
    url = models.URLField(verbose_name="Ссылка", blank=True, null=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Пользователь",
        related_name="users_shop",
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    state = models.BooleanField("Статус приёма заказов", default=True)
    filename = models.FileField(
        "Файл продуктов",
        upload_to="product_files/",
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = "Магазин"
        verbose_name_plural = "Список магазинов"

    def __str__(self):
        return f"{self.name}"


class Category(models.Model):
    """Модель категорий"""

    name = models.CharField(verbose_name="Название", max_length=50)
    shops = models.ManyToManyField(
        Shop,
        verbose_name="Магазин",
        related_name="categories",
        blank=True
    )

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return f"{self.name}"


class Product(models.Model):
    """Модель продукта"""

    name = models.CharField(verbose_name="Название", max_length=80)
    category = models.ForeignKey(
        Category,
        verbose_name="Категория",
        related_name="product",
        blank=True,
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Список продуктов"

    def __str__(self):
        return f"{self.name}"


class ProductInfo(models.Model):
    """Модель информации о продукте"""

    product = models.ForeignKey(
        Product,
        verbose_name="Продукт",
        related_name="product_info",
        on_delete=models.CASCADE
    )
    shop = models.ForeignKey(
        Shop,
        verbose_name="Магазин",
        related_name="about_product",
        on_delete=models.CASCADE,
        blank=True
    )
    quantity = models.IntegerField(verbose_name="Количество в наличии")
    price = models.IntegerField(verbose_name="Цена")
    price_rrc = models.IntegerField(verbose_name="Рекомендованная цена")

    class Meta:
        verbose_name = "Информация о продукте"
        verbose_name_plural = "Список информаций о продуктах"

    # @property
    # def total_sum(self):
    #     self.aggregate(total=Sum("price_rrc"))

    def __str__(self):
        return f"{self.product}"


class Parameter(models.Model):
    """Модель параметров"""

    name = models.CharField(verbose_name="Название параметра", max_length=150)

    class Meta:
        verbose_name = "Параметры"
        verbose_name_plural = "Список параметров"

    def __str__(self):
        return f"{self.name}"


class ProductParameter(models.Model):
    """Модель параметров продукта"""

    product_info = models.ForeignKey(
        ProductInfo,
        verbose_name="Информация о продукте",
        related_name="product_parameter",
        on_delete=models.CASCADE
    )
    parameter = models.ForeignKey(
        Parameter,
        verbose_name="Название параметра",
        related_name="parameter_name",
        on_delete=models.CASCADE,
        blank=True
    )
    value = models.CharField(verbose_name="Значение", max_length=100)

    class Meta:
        verbose_name = "Параметр продукта"
        verbose_name_plural = "Список параметров продукта"


class Contacts(models.Model):
    """Модель контактов пользователя"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Пользователь",
        related_name="contacts",
        on_delete=models.CASCADE
    )
    city = models.CharField(verbose_name="Город", max_length=60)
    district = models.CharField(verbose_name="Район", max_length=60)
    street = models.CharField("Улица", max_length=60)
    house = models.CharField("Дом", max_length=60)
    building = models.CharField("Квартира", max_length=60)
    phone = models.CharField("Номер телефона", max_length=20)

    class Meta:
        verbose_name = "Контакты пользователя"
        verbose_name_plural = "Список контактов пользователей"

    def __str__(self):
        return f'{self.user} - {self.city}'


class Order(models.Model):
    """Модель заказов"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Пользователь",
        related_name="order",
        on_delete=models.CASCADE
    )
    created_date = models.DateField("Дата создания", auto_now_add=True)
    state = models.CharField("Статус заказа", choices=STATE_CHOICES, max_length=20)
    contacts = models.ForeignKey(
        Contacts,
        verbose_name="Контакты",
        related_name="order",
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Заказы"
        verbose_name_plural = "Список заказов"

    def __str__(self):
        return f"{self.user}"

    # @property
    # def sum(self):
    #     return 10


class OrderItem(models.Model):
    """Модель позиции заказа"""

    order = models.ForeignKey(
        Order,
        verbose_name="Заказ",
        related_name="positions",
        on_delete=models.CASCADE
    )
    product_info = models.ForeignKey(
        ProductInfo,
        verbose_name="Информация о продукте",
        related_name="order_item",
        on_delete=models.CASCADE
    )
    quantity = models.IntegerField("Количество товара")

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Список позиций заказов"

    def __str__(self):
        return f"{self.quantity}"
