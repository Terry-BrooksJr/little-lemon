from django.contrib.auth.models import Group, User
from loguru import logger
from rest_framework.serializers import (
    HiddenField,
    ModelSerializer,
    PrimaryKeyRelatedField,
    ReadOnlyField,
    SerializerMethodField,
    CharField
)
from datetime import datetime
from LittleLemonAPI.models import Cart, Category, MenuItem, Order
import json
from django.forms.models import model_to_dict

class PriceRounder:

    def round_price(self, instance):
        logger.debug(f"Rounding price for {instance}")
        return round(instance.price, 2)
    
    def calculate_price(self, quantity, unit_price):
        return float(quantity) * float(unit_price)

class GroupSerializer(ModelSerializer):
    class Meta:
        model = Group
        fields = [ "name"]

    def to_representation(self, instance):
        return super().to_representation(instance)


class MenuItemDetailSerializer(PriceRounder, ModelSerializer):
    item_id = ReadOnlyField()
    category = PrimaryKeyRelatedField(queryset=Category.objects.all())

    class Meta:
        model = MenuItem
        fields = "__all__"

    def to_representation(self, instance):
        logger.info(f"Serializing menu item {instance}")
        representation = super().to_representation(instance)
        logger.debug(f"Serialized menu item {instance} to {representation}")
        representation["category"] = instance.category.title
        logger.debug(f"Modified menu item representation to {representation}")
        return {
            "product_sku": representation["item_id"],
            "category": representation["category"],
            "product_name": representation["title"],
            "price_per_item": representation["price"],
            "featured": representation["featured"],
            "on_sale": representation["is_on_sale"],
            "nutritional_facts": {
                "calories": representation["calories"],
                "sugar": f"{representation['sugar_gm']} gram(s)",
                "protein": f"{representation['protein_gm']} gram(s)",
                "carbohydrates": f"{representation['carbohydrates_mg']} milligram(s)",
                "saturated_fat": f"{representation['saturated_fat_gm']} gram(s)",
            },
            "allergens": {
                "contains_dairy": representation["contains_dairy"],
                "contains_gluten": representation["contains_gluten"],
                "contains_treenuts": representation["contains_treenuts"],
            },
        }

    def to_internal_value(self, data):
        ret = super().to_internal_value(data)
        logger.debug(ret)
        return ret


class MenuItemSerializer(PriceRounder, ModelSerializer):
    item_id = ReadOnlyField()
    category = PrimaryKeyRelatedField(queryset=Category.objects.all())

    class Meta:
        model = MenuItem
        fields = ["item_id", "title", "price", "category"]

    def to_representation(self, instance):
        logger.info(f"Serializing menu item {instance}")
        representation = super().to_representation(instance)
        logger.debug(f"Serialized menu item {instance} to {representation}")
        representation["category"] = instance.category.title
        logger.debug(f"Modified menu item representation to {representation}")
        return {
            "product_sku": int(representation["item_id"]),
            "category": representation["category"],
            "product_name": representation["title"],
            "price_per_item": float(representation["price"]),
        }

    def to_internal_value(self, data):
        ret = super().to_internal_value(data)
        logger.debug(ret)
        ret["product_sku"] = data["item_id"]
        ret["product_name"] = data["title"]
        ret["price_per_item"] = data["price"]
        return ret


class UserSerializer(ModelSerializer):
    id = ReadOnlyField()
    groups = GroupSerializer(many=True, read_only=True)

    class Meta:
        model = User
        exclude = ["is_staff", "is_active","is_superuser", "user_permissions"]

    def to_representation(self, instance):
        logger.info(f"Serializing user {instance}")
        instance_dict =model_to_dict(instance)
        employee_full_name = f"{instance_dict.get('last_name',"N/A")}, {instance_dict.get('first_name')}",
        groups = GroupSerializer(instance.groups, many=True).data
        group_list = [group['name'] for group in groups]
        hire_date = datetime.strftime(instance.date_joined, '%Y-%m-%d')
        email = instance_dict.get('email','NOT_PROVIDED')
        new_representation = {
            "employee_id": instance.id,
            "employee_name": str("".join(employee_full_name)),
            "hire_date": hire_date,
            "login_username": instance.username,
            "groups":group_list,
            "email": email
        }
        logger.debug(f"Serializing user {instance} to {new_representation}")
        return new_representation

        


class CartSerializer(PriceRounder, ModelSerializer):

    class Meta:
        model = Cart
        fields = ["menuitem", "quantity", "user_id", "price"]


class OrderSerializer(PriceRounder, ModelSerializer):

    class Meta:
        model = Order
        fields = "__all__"
