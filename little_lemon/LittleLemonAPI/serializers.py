from rest_framework.serializers import ModelSerializer, SerializerMethodField,PrimaryKeyRelatedField, ReadOnlyField, HiddenField
from LittleLemonAPI.models import MenuItem, Cart, Order,Category
from django.contrib.auth.models import User, Group
from loguru import logger

class PriceRounder:
    
    def round_price(self, instance):
        logger.debug(f"Rounding price for {instance}")
        return round(instance.price, 2)

class GroupSerializer(ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name', 'permissions']

class MenuItemSerializer(PriceRounder, ModelSerializer):
    item_id = ReadOnlyField()
    category = PrimaryKeyRelatedField(queryset=Category.objects.all())
    class Meta:
        model = MenuItem
        fields = ['item_id', 'title', 'price', 'featured', 'category']

    def to_representation(self, instance):
        logger.info(f"Serializing menu item {instance}")
        representation = super().to_representation(instance)
        logger.debug(f"Serialized menu item {instance} to {representation}")
        representation['category'] = instance.category.title
        logger.debug(f"Modified menu item representation to {representation}")
        return representation

    def to_internal_value(self, data):
        ret = super().to_internal_value(data)
        logger.debug(ret)
        return ret

class UserSerializer(ModelSerializer):
    id = ReadOnlyField()
    groups = GroupSerializer(many=True, read_only=True)
    class Meta:
        model = User
        fields = "__all__"

    def to_representation(self, instance):
        logger.info(f"Serializing user {instance}")
        representation = super().to_representation(instance)
        logger.debug(f"Serialized user {instance} to {representation}")
        unnecessary_fields = ['first_name', 'last_name', 'username', 'id', 'password']
        for field in unnecessary_fields:
            del representation[field]
            logger.debug(f"Deleted unnecessary field {field} from user representation")
        representation['employee_name'] = f'{instance.last_name}, {instance.first_name}',
        representation["employee_id"]= instance.id,
        representation['login_username']= instance.username,
        logger.debug(f"Modified user representation to {representation}")
        return representation

class CartSerializer(PriceRounder, ModelSerializer):
    cart_id = ReadOnlyField()
    price = SerializerMethodField(method_name="round_price")
    class Meta:
        model = Cart
        fields = ['menuitem', 'quantity', 'user_id', 'price']

class OrderSerializer(PriceRounder, ModelSerializer):
    order_id = ReadOnlyField()
    price = SerializerMethodField(method_name="round_price")
    class Meta:
        model = Order
        fields = "__all__"

    def to_representation(self, instance):
        logger.info(f"Serializing order {instance}")
        representation = super().to_representation(instance)
        logger.debug(f"Serialized order {instance} to {representation}")
        return representation