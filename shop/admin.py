from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from shop.models import Category, User, Shop, Product, ProductInfo, Parameter, ProductParameter, Contacts, Order, \
    OrderItem


class CategoryShopsInline(admin.TabularInline):
    model = Category.shops.through
    can_delete = False
    extra = 0


class IsUserAdmin(UserAdmin):
    list_display = ("id", "username", "email", "is_staff", "user_type")
    list_display_links = ('username', )
    fieldsets = (
        (None, {'fields': ('username', 'password', 'user_type')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )


class ShopAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user', 'state')
    list_display_links = ('name', )
    inlines = (CategoryShopsInline, )
    readonly_fields = ("name", 'user', 'state', "filename", 'url')


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)
    list_display_links = ('name',)
    inlines = (CategoryShopsInline, )
    readonly_fields = ("shops",)


class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category")
    list_display_links = ("name", )
    readonly_fields = ("name", "category")


class ProductInfoAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "shop", "price",)
    list_display_links = ("product", )
    readonly_fields = ("product", "shop", "quantity", "price", "price_rrc", )


class ParameterAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    list_display_links = ("name", )


class ProductParameterAdmin(admin.ModelAdmin):
    list_display = ("id", "product_info", "parameter")
    list_display_links = ("parameter", )
    readonly_fields = ("product_info", "parameter", "value")


class ContactsAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "city", "district", "street", "house", "building", "phone", )
    list_display_links = ("user",)
    readonly_fields = ("id", "user", "city", "district", "street", "house", "building", "phone", )


class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "state")
    list_display_links = ("user",)
    readonly_fields = ("id", "user", "created_date", "state", "contacts",)


class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "quantity",)
    list_display_links = ("order",)
    readonly_fields = ("id", "order", "product_info", "quantity",)


admin.site.register(User, IsUserAdmin)
admin.site.register(Shop, ShopAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductInfo, ProductInfoAdmin)
admin.site.register(Parameter, ParameterAdmin)
admin.site.register(ProductParameter, ProductParameterAdmin)
admin.site.register(Contacts, ContactsAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
