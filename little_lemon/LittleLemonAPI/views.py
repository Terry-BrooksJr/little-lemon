from django.shortcuts import render, get_object_or_404
from rest_framework import filters
from rest_framework.generics import ListAPIView, RetrieveUpdateDestroyAPIView, ListCreateAPIView 
from LittleLemonAPI.models import MenuItem, Cart, Order, OrderItem
from LittleLemonAPI.serializers import MenuItemSerializer, UserSerializer, CartSerializer, OrderSerializer
from rest_framework.mixins import DestroyModelMixin, UpdateModelMixin
from django_filters.rest_framework import DjangoFilterBackend
from django.forms.models import model_to_dict
from  rest_framework.status import HTTP_403_FORBIDDEN, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_200_OK, HTTP_422_UNPROCESSABLE_ENTITY, HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST,HTTP_405_METHOD_NOT_ALLOWED
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError

from django.contrib.auth.models import Group, User
class MenuItemsListView(ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    permission_classes = [IsAuthenticatedOrReadOnly]
    filterset_fields = ['featured', 'category']
    search_fields = ["title"]


    def create(self, request, *args, **kwargs):
        if request.user.groups.filter(name="manager").exists():
            return super().create(request, *args, **kwargs)
        return Response(data="Action Restricted to Managers Only", status=HTTP_403_FORBIDDEN)

class MenuItemDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = MenuItemSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['title']


    def get_object(self):
        try:
            obj =   MenuItem.objects.get(item_id=self.kwargs['item_id'])
            self.check_object_permissions(self.request, obj)
            return obj
        except ObjectDoesNotExist:
            return None
    
    def update(self, request, *args, **kwargs):
        if request.user.groups.filter(name="manager").exists():
            return super().update(request, *args, **kwargs)
        return Response(data="Action Restricted to Managers Only", status=HTTP_403_FORBIDDEN)
    

    def destroy(self, request, *args, **kwargs):
        if request.user.groups.filter(name="manager").exists():
            return super().destroy(request, *args, **kwargs)
        return Response(data="Action Restricted to Managers Only", status=HTTP_403_FORBIDDEN)


    def partial_update(self, request, *args, **kwargs):
        if request.user.groups.filter(name="manager").exists():
            return super().partial_update(request, *args, **kwargs)
        return Response(data="Action Restricted to Managers Only", status=HTTP_403_FORBIDDEN)


class ManagerUserManagement(UpdateModelMixin, DestroyModelMixin, ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['username', 'first_name', 'last_name']
    permission_classes = [IsAuthenticated]
    filterset_fields = ['is_active', 'is_staff', 'is_superuser']

    def post(self, request):
        if request.user.groups.filter(name="manager").exists(): 
            try:
                if username := request.data['username']:
                    user = get_object_or_404(User, username=username)
                    managers = Group.objects.get(name="managers")
                    managers.user_set.add(user)
                    return Response(data=f"{user.username} has been added to the manager group and the accounts permissions have been updated to reflect the change.", status=HTTP_201_CREATED)
            except KeyError:
                return Response(data='Post body must have key "username"', status=HTTP_422_UNPROCESSABLE_ENTITY)
        return Response(data="Action Restricted to Managers Only", status=HTTP_403_FORBIDDEN)
    def delete(self, request, id):
        if request.user.groups.filter(name="manager").exists():
            try:
                user = get_object_or_404(User, id=id)
                managers = Group.objects.get(name="manager")
                managers.user_set.remove(user)
                return Response(f"{user.username} has been removed to the manager group and the accounts permissions have been updated to reflect the change.", status=HTTP_200_OK)
            except KeyError:
                return Response(data='URL must have a path parameter for the targeted employee id', status=HTTP_422_UNPROCESSABLE_ENTITY)
        return Response(data="Action Restricted to Managers Only", status=HTTP_403_FORBIDDEN)
        
    def get(self, request):
        if not request.user.groups.filter(name="manager").exists():
            return Response(data="Action Restricted to Managers Only", status=HTTP_403_FORBIDDEN)
        users = User.objects.all()
        manager_group_members = []
        for user in users:
            if user.groups.filter(name="manager").exists():
                user = UserSerializer(user).data
                manager_group_members.append(user)

        return Response(data=manager_group_members, status=HTTP_200_OK)
    
class DeliveryCrewUserManagement(UpdateModelMixin, DestroyModelMixin, ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    lookup_field = id
    search_fields = ['username', 'first_name', 'last_name']
    permission_classes = [IsAuthenticated]
    filterset_fields = ['is_active', 'is_staff', 'is_superuser']

    def post(self, request):
        if request.user.groups.filter(name="manager").exists(): 
            try:
                if username := request.data['username']:
                    user = get_object_or_404(User, username=username)
                    managers = Group.objects.get(name="delivery crew")
                    managers.user_set.add(user)
                    return Response(data=f"{user.username} has been added to the manager group and the accounts permissions have been updated to reflect the change.", status=HTTP_201_CREATED)
            except KeyError:
                return Response(data='Post body must have key "username"', status=HTTP_422_UNPROCESSABLE_ENTITY)
        return Response(data="Action Restricted to Managers Only", status=HTTP_403_FORBIDDEN)

    def delete(self, request, id):
        if request.user.groups.filter(name="manager").exists():
            try:               
                user = get_object_or_404(User, id=id)
                managers = Group.objects.get(name="delivery crew")
                managers.user_set.remove(user)
                return Response(f"{user.username} has been removed to the manager group and the accounts permissions have been updated to reflect the change.", status=
                                HTTP_200_OK)
            except KeyError:
                return Response(data='URL must have a path parameter for the targeted employee id', status=HTTP_422_UNPROCESSABLE_ENTITY)
        return Response(data="Action Restricted to Managers Only", status=HTTP_403_FORBIDDEN)
    
    def get(self, request):
        if request.user.groups.filter(name="manager").exists():    
            users = User.objects.all()
            manager_group_members = []
            for user in users:
                if user.groups.filter(name="delivery crew").exists():
                    user = UserSerializer(user).data
                    manager_group_members.append(user)

            return Response(data=manager_group_members, status=HTTP_200_OK)
        return Response(data="Action Restricted to Managers Only", status=HTTP_403_FORBIDDEN)
    


class CartManagement(RetrieveUpdateDestroyAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer   
    # lookup_field = 'cart_id'
    permission_classes = [IsAuthenticated]
    def calculate_price(self, quantity,  unit_price):
            return quantity * unit_price

    def get(self, request):
        user = User.objects.get(username=self.request.user.username)
        carts = Cart.objects.filter(user=user)
        all_cart_items = []
        for cart in carts:
            cart_item = {
                'item name': MenuItemSerializer(
                    MenuItem.objects.get(item_id=cart.menuitem.item_id)
                ).data['title'],
                'product id': cart.menuitem.item_id,
                'quantity': cart.quantity ,
                'price per item': float(MenuItemSerializer(
                    MenuItem.objects.get(item_id=cart.menuitem.item_id)
                ).data['price']),
            }
            cart_item['price'] = self.calculate_price(float(cart_item['quantity']), float(cart_item['price per item']))
            all_cart_items.append(cart_item)
        return Response(data=all_cart_items, status=HTTP_200_OK)
    
    def post(self, request):
        try:
            user = User.objects.get(username=self.request.user.username)
            if item_id := request.data['item_id']:
                if quantity := request.data['quantity']:
                        item = MenuItem.objects.get(item_id=item_id)
                        unit_price = item.price
                        cart = Cart.objects.create(
                            user=user,
                            menuitem=item,
                            quantity=quantity,
                            unit_price=unit_price,
                            price=float(unit_price)*float(quantity)
                            ).save()
                return Response(data=f"{quantity} {item.title}s been added to {user.username}'s cart", status=HTTP_201_CREATED)
        except KeyError:
                return Response(data='Post body must have keys "quantity", "item_id", ', status=HTTP_422_UNPROCESSABLE_ENTITY)
        except MenuItem.DoesNotExist:
            return Response(data='Item does not exist', status=HTTP_404_NOT_FOUND)
        except IntegrityError as e:
            return Response(data='Item already in cart', status=HTTP_400_BAD_REQUEST)
        

    def delete(self, request):
        user = User.objects.get(username=self.request.user.username)
        carts = Cart.objects.filter(user=user)
        for cart in carts:
            cart.delete()
        return Response(data=f"{user.username}'s cart has been cleared", status=HTTP_200_OK)
        




class OrderManagement(UpdateModelMixin, DestroyModelMixin, ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    lookup_field = 'order_id'
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status', 'date', 'delivery_crew', 'user']
    search_fields = ["order_is", "user"]
    
    def get(self, request):
        if request.user.groups.filter(name="manager").exists():
            return Response(data=Order.objects.all(),status=HTTP_200_OK) 
        elif request.user.groups.filter(name="delivery crew").exists():
            return  Response(data=Order.objects.filter(delivery_crew=request.user), status=HTTP_200_OK)
        else:
            return Response(data=Order.objects.filter(user=request.user),status=HTTP_200_OK)
        
    def post(self,request):
        if request.user.groups.filter(name="manager").exists():
            return Response(data="Method Not Allowed", status=HTTP_405_METHOD_NOT_ALLOWED)
        elif request.user.groups.filter(name="delivery crew").exists():
            return Response(data="Method Not Allowed", status=HTTP_405_METHOD_NOT_ALLOWED)
        else:
            try:
                if len(carts := Cart.objects.filter(user=self.request.user)) <= 0:
                    return Response(data="No Items In Cart", status=HTTP_400_BAD_REQUEST)
                total = sum(cart.price for cart in list(carts))
                new_order = Order.objects.create(
                    user=self.request.user,
                    total=total
                ).save()
                for cart in carts:
                    order_item = OrderItem.objects.create(
                        order=new_order.order_id,
                        menuitem=MenuItem.objects.get(item_id=cart.menuitem.item_id),
                        quantity=cart.quantity,
                        unit_price=cart.unit_price,
                        price=cart.price
                    ).save()
                    cart.delete()
                return Response(data=f" Successfully Created {new_order.order_id}",status=HTTP_201_CREATED)
            except Exception as e:
                return Response(data=f"Error:{str(e)}", status=HTTP_400_BAD_REQUEST)
        
    def patch(self, request, order_id):
        order = get_object_or_404(Order,order_id=order_id)
        if request.user.groups.filter(name="manager").exists():            
            if request.data['status']:
                order.status = request.data['status']
            if not request.data['delivery_crew']:
                return Response(data="POST body must contain either 'status' or 'delivery_crew' keys", status=HTTP_400_BAD_REQUEST)
            order.delivery_crew = User.objects.get(id=request.data['delivery_crew'].id)

            order.save()
            return Response(status=HTTP_204_NO_CONTENT)
        elif request.user.groups.filter(name="delivery crew").exists():                
            if request.data['status']:
                order.status = request.data['status']
                order.save()
                return Response(status=HTTP_204_NO_CONTENT)
            else:
                return Response(data="POST body must contain either 'status' key", status=HTTP_400_BAD_REQUEST)

        else:
            return super().patch()




