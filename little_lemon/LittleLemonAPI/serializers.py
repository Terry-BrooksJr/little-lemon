from rest_framework.serializers import ModelSerializer, SerializerMethodField
from LittleLemonAPI.models import MenuItem, Cart, Order
from django.contrib.auth.models import User, Group

class MenuItemSerializer(ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['item_id', 'title', 'price', 'featured', 'category']

    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['category'] = instance.category.title
        return representation

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id','first_name', 'last_name', 'username']

    def to_representation(self, instance):
        return {
            'employee_name': f'{instance.last_name}, {instance.first_name}',
            "employee_id": instance.id,
            'login_username': instance.username,
        }



class GroupSerializer(ModelSerializer):
    class Meta:
        model = Group
        fields = ['permissions']


class CartSerializer(ModelSerializer):
    price = SerializerMethodField(method_name="calculate_price")
    class Meta:
        model = Cart
        fields = ['menuitem', 'quantity', 'user_id', 'price']


class OrderSerializer(ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"
    # def to_representation(self, instance):
    #     representation = super().to_representation(instance)
    #     all_cart_items = []
    #     for cart in instance:
    #         cart_item = {
    #             'item_id': MenuItemSerializer(
    #                 MenuItem.objects.get(item_id=cart.item_id)
    #             ).data['title'],
    #             'quantity':  MenuItemSerializer(
    #                 MenuItem.objects.get(item_id=cart.item_id)
    #             ).data['title'] ,
    #             'price per item': cart.unit_price,
    #         }   
    #         cart_item['price'] = self.calculate_price(cart_item['quantity'],        cart_item['price'])
    #         all_cart_items.append(cart_item)
    #     return all_cart_items