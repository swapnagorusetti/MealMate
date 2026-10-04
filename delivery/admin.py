from django.contrib import admin
from .models import Customer, Restaurant, Item, Cart


# ==========================================
# CUSTOMER ADMIN
# ==========================================

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'username',
        'email',
        'mobile',
    )

    search_fields = (
        'username',
        'email',
        'mobile',
    )


# ==========================================
# RESTAURANT ADMIN
# ==========================================

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'name',
    )

    search_fields = (
        'name',
    )

    ordering = (
        'id',
    )


# ==========================================
# ITEM ADMIN
# ==========================================

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'name',
        'price',
        'restaurant',
    )

    search_fields = (
        'name',
    )


# ==========================================
# CART ADMIN
# ==========================================

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'customer',
    )