from django.contrib import admin

from LittleLemonAPI.models import Cart, Category, MenuItem, Order, OrderItem

# Register your models here.

models = [Cart, Category, Order, OrderItem, MenuItem]

for model in models:
    admin.site.register(
        model
    )  # Register the models with the admin site.  # Register your
