from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.forms.models import model_to_dict
from rest_framework import filters, status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.mixins import DestroyModelMixin, UpdateModelMixin
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import Group, User
from django.db import IntegrityError
from LittleLemonAPI.models import MenuItem, Cart, Order, OrderItem
from LittleLemonAPI.serializers import (
    MenuItemSerializer,
    UserSerializer,
    CartSerializer,
    OrderSerializer,
    MenuItemDetailSerializer,
)

from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from loguru import logger
import json
from datetime import datetime
from little_lemon.utils.cache import CachedResponseMixin
@api_view(["GET"])
@renderer_classes([BrowsableAPIRenderer, JSONRenderer])
def api_root(request):
    """Welcome To the Little Lemon API. Get started by making a request to one of the Primary Endpoints"""
    return Response(
        {
            "primary API Endpoint": [
                {
                    "Menu Items": reverse("items-list"),
                    "description": "Manage menu items: create, update, delete.",
                },
                {
                    "Orders": reverse("Order-Management"),
                    "description": "Manage orders from creation to deletion.",
                },
                {
                    "Cart": reverse("Cart-Management"),
                    "description": "Manage cart items, add, update, and delete items.",
                },
            ]
        }
    )


class MyEncoder(json.JSONEncoder):
    """Custom JSON encoder for serializing specific object types.

    This encoder extends the default JSONEncoder to handle serialization of
    custom objects such as TicketStatus, datetime, and Comment. It provides
    a way to convert these objects into a JSON-compatible format.
    """

    def default(self, obj):
        """
        Converts custom objects to a JSON-compatible format.

        This method checks the ticket_type of the object and returns a corresponding
        JSON representation. If the object ticket_type is not recognized, it falls
        back to the default serialization method.

        Args:
            obj: The object to be serialized.

        Returns:
            A JSON-compatible representation of the object.

        Raises:
            TypeError: If the object ticket_type is not serializable.
        """
        if isinstance(obj, datetime):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)


class MenuItemsListView(CachedResponseMixin, ListCreateAPIView):
    """
    Menu Items List and Creation API View.

    This view provides a comprehensive interface for listing and creating menu items in the system.
    - **Listing**: All users can view the list of menu items, which includes filtering and searching functionalities.
    - **Creation**: Only users in the "manager" group are permitted to create new menu items. When a manager creates an item, the menu item details (such as title, description, and category) are validated and stored.

    ### Filters and Search
    - **Filter by**: `featured`, `category`
    - **Search by**: `title`

    ### Permissions
    - Authenticated users can view the menu items (read-only).
    - Only users in the "manager" group can create new menu items.

    Raises:
    - **403 Forbidden**: If a non-manager attempts to create a menu item.
    - **400 Bad Request**: If an item creation fails due to invalid data.
    """
    queryset = MenuItem.objects.all()
    primary_model = MenuItem
    cache_models = [ Group, User ]
    serializer_class = MenuItemSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    permission_classes = [IsAuthenticatedOrReadOnly]
    filterset_fields = [
        "featured",
        "category",
        "is_on_sale",
        "contains_dairy",
        "contains_treenuts",
        "contains_gluten",
    ]
    search_fields = ["title"]
    def create(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="manager").exists():
            logger.warning(f"Unauthorized  POST Request Blocked At {reverse('items-detail')}")
            return Response(
                {"error": "Action restricted to managers only."},
                status=status.HTTP_403_FORBIDDEN,
            )
        try:
            return super().create(request, *args, **kwargs)
        except (IntegrityError, TypeError, KeyError) as e:
            print(dir(e))
            logger.error(str(e))
            return Response(
                {"error": "Unable to add menu item", "reason": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class MenuItemDetailView(CachedResponseMixin, RetrieveUpdateDestroyAPIView):
    """
    Menu Item Detail, Update, and Delete API View.

    This view provides detailed access to a single menu item, allowing retrieval, updates, and deletion.
    - **Retrieve**: All authenticated users can view the details of a specific menu item.
    - **Update and Delete**: Only users in the "manager" group can modify or delete menu items.

    ### Permissions
    - Authenticated users can retrieve menu item details (read-only).
    - Only managers can update or delete a menu item.

    Raises:
    - **403 Forbidden**: If a non-manager attempts to update or delete a menu item.
    - **404 Not Found**: If the menu item does not exist.
    """

    serializer_class = MenuItemDetailSerializer
    queryset = MenuItem.objects.all()
    primary_model = MenuItem
    cache_models = [ Group, User ]
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = "item_id"

    def perform_update_or_destroy(self, request, method):
        if request.user.groups.filter(name="manager").exists():
            return method(request)
        logger.warning(f"Unauthorized {method.__name__} Request Blocked At {reverse('items-detail')}")
        return Response(
            {"error": "Action restricted to managers only."},
            status=status.HTTP_403_FORBIDDEN,
        )

    def update(self, request, *args, **kwargs):
        return self.perform_update_or_destroy(
            request, lambda req: super().update(req, *args, **kwargs)
        )

    def destroy(self, request, *args, **kwargs):
        return self.perform_update_or_destroy(
            request, lambda req: super().destroy(req, *args, **kwargs)
        )

    def partial_update(self, request, *args, **kwargs):
        return self.perform_update_or_destroy(
            request, lambda req: super().partial_update(req, *args, **kwargs)
        )


class ManagerUserManagement(CachedResponseMixin, UpdateModelMixin, DestroyModelMixin, ListCreateAPIView):
    """
    Manager User Management API View.

    This view manages user roles, specifically adding or removing users from the "manager" group.
    - **Add User to Manager Group**: Only current managers can add other users to the "manager" group, granting them special privileges.
    - **Remove User from Manager Group**: Managers can also remove users from the "manager" group.
    - **List of Managers**: Provides a list of all users who belong to the "manager" group.

    ### Permissions
    - Only users in the "manager" group can access these operations.

    Raises:
    - **403 Forbidden**: If a non-manager attempts to access this view.
    - **404 Not Found**: If the specified user does not exist.
    - **400 Bad Request**: If required data, such as `username`, is missing.
    """

    queryset = User.objects.all()
    primary_model = User
    cache_models = [ Group ]
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ["username", "first_name", "last_name"]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not request.user.groups.filter(name="manager").exists():
            logger.warning(f"Unauthorized  {request.method} Request Blocked At {request.path}")
            return Response(
                {"error": "Action restricted to managers only."},
                status=status.HTTP_403_FORBIDDEN,
            )
        try:
            username = request.data["username"]
            user = get_object_or_404(User, username=username)
            Group.objects.get(name="manager").user_set.add(user)
            return Response(
                {"response": f"{user.username} added to manager group."},
                status=status.HTTP_201_CREATED,
            )
        except KeyError as e:
            logger.error(str(e))
            return Response(
                {"error": 'POST body must include "username".'},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def delete(self, request, id):
        if not request.user.groups.filter(name="manager").exists():
            logger.warning(f"Unauthorized  {request.method} Request Blocked At {request.path}")
            return Response(
                {"error": "Action restricted to managers only."},
                status=status.HTTP_403_FORBIDDEN,
            )
        user = get_object_or_404(User, id=id)
        Group.objects.get(name="manager").user_set.remove(user)
        return Response(
            {"response": f"{user.username} removed from manager group."},
            status=status.HTTP_200_OK,
        )

    def get(self, request):
        if not request.user.groups.filter(name="manager").exists():
            logger.warning(f"Unauthorized  {request.method} Request Blocked At {request.path}")
            return Response(
                {"error": "Action restricted to managers only."},
                status=status.HTTP_403_FORBIDDEN,
            )
        crew_users = User.objects.filter(groups__name="manager")
        delivery_crew_users = UserSerializer(crew_users, many=True)
        final_list = list(delivery_crew_users.data)
        return Response(final_list, status=status.HTTP_200_OK)


class DeliveryCrewUserManagement(CachedResponseMixin,
    UpdateModelMixin, DestroyModelMixin, ListCreateAPIView
):
    """
    Delivery Crew User Management API View.

    This view manages user roles for the "delivery crew" group, specifically allowing managers to add or remove users from this group.
    - **Add User to Delivery Crew Group**: Managers can assign users to the "delivery crew" group, enabling them to take delivery responsibilities.
    - **Remove User from Delivery Crew Group**: Managers can remove users from the "delivery crew" group.
    - **List Delivery Crew**: Provides a list of all users in the "delivery crew" group.

    ### Permissions
    - Only users in the "manager" group can access these operations.

    Raises:
    - **403 Forbidden**: If a non-manager attempts to access this view.
    - **404 Not Found**: If the specified user does not exist.
    - **400 Bad Request**: If required data, such as `username`, is missing.
    """

    queryset = User.objects.all()
    primary_model = User
    cache_models = [ Group ]
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ["username", "first_name", "last_name"]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not request.user.groups.filter(name="manager").exists():
            return Response(
                {"error": "Action restricted to managers only."},
                status=status.HTTP_403_FORBIDDEN,
            )
        try:
            username = request.data["username"]
            user = get_object_or_404(User, username=username)
            delivery_crew_group = Group.objects.get(name="delivery crew")
            delivery_crew_group.user_set.add(user)
            return Response(
                {"response": f"{user.username} added to delivery crew."},
                status=status.HTTP_201_CREATED,
            )
        except KeyError:
            return Response(
                {"error": 'POST body must include "username".'},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def delete(self, request, id):
        if not request.user.groups.filter(name="manager").exists():
            return Response(
                {"error": "Action restricted to managers only."},
                status=status.HTTP_403_FORBIDDEN,
            )
        user = get_object_or_404(User, id=id)
        delivery_crew_group = Group.objects.get(name="delivery crew")
        delivery_crew_group.user_set.remove(user)
        return Response(
            {"response": f"{user.username} removed from delivery crew."},
            status=status.HTTP_200_OK,
        )

    def get(self, request):
        if not request.user.groups.filter(name="manager").exists():
            logger.warning(f"Unauthorized  GET Request Blocked At {reverse('items-detail')}")
            return Response(
                {"error": "Action restricted to managers only."},
                status=status.HTTP_403_FORBIDDEN,
            )
        all_users = User.objects.all()
        crew_users = [
            query_user
            for query_user in all_users
            if query_user.groups.filter(name="manager").exists()
        ]
        delivery_crew_users = UserSerializer(crew_users, many=True)
        final_list = list(delivery_crew_users.data)
        return Response(final_list, status=status.HTTP_200_OK)


class CartManagement(CachedResponseMixin, RetrieveUpdateDestroyAPIView):
    """
    User Cart Management API View.

    This view manages the shopping cart for authenticated users.
    - **Retrieve Cart**: Displays the contents of the user’s cart, including item names, quantities, and total prices.
    - **Add to Cart**: Allows users to add items to their cart by specifying item ID and quantity.
    - **Clear Cart**: Clears all items in the user’s cart.

    ### Permissions
    - Only authenticated users can access cart operations.

    Raises:
    - **400 Bad Request**: If required fields are missing in the request body (e.g., `quantity`, `item_id`).
    - **404 Not Found**: If the specified item does not exist.
    - **403 Forbidden**: If a user tries to perform unauthorized cart actions.
    """

    queryset = Cart.objects.all()
    primary_model = Cart
    cache_models = [ Group ]
    cache_models = [MenuItem, Group, User ]
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def calculate_price(self, quantity, unit_price):
        return round(float(quantity) * float(unit_price),2)

    def get(self, request):
        user = request.user
        cart_items = Cart.objects.filter(user=user)
        cart_total = 0
        all_cart_items = []
        item_count = 0
        if len(cart_items) >= 1:
            for cart in cart_items:
                item = {
                    "product_name": cart.menuitem.title,
                    "product_sku": cart.menuitem.item_id,
                    "quantity": cart.quantity,
                    "price per item": round(float(cart.menuitem.price),2),
                    "price": self.calculate_price(cart.quantity, cart.menuitem.price),
                }
                all_cart_items.append(item)
                cart_total += item.get("price")
                item_count += 1
            return Response(
                {
                    "cart": {
                        "summary": {
                            "customer": f"{user.last_name }, {user.first_name}",
                            "number_of_items": item_count,
                            "total_cost_USD": f"${round(cart_total,2)}",
                        },
                        "contents": all_cart_items,
                    }
                }, status=status.HTTP_200_OK,
            )
        else: 
            return Response(
                {
                    "cart": {
                        "summary": {
                            "customer": f"{user.last_name }, {user.first_name}",
                            "number_of_items": item_count,
                            "total_cost_USD": f"${round(cart_total,2)}",
                        },
                        "contents": ['No Items Currently In Cart']
                    }
                },status=status.HTTP_200_OK,
            )
            
        

    def post(self, request):
        try:
            return self._build_cart(request)
        except KeyError as ke:
            logger.error(str(ke))
            return Response(
                {"error": 'Request body must include "quantity" and "item_id".'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except MenuItem.DoesNotExist as ODNE:
            logger.error(str(ODNE))
            return Response(
                {"error": "Item does not exist."}, status=status.HTTP_404_NOT_FOUND
            )
        except IntegrityError as ie:
            logger.error(str(ie))
            return Response(
                {"error": "Item Already In Cart"}, status=status.HTTP_400_BAD_REQUEST
            )

    # TODO Rename this here and in `post`
    def _build_cart(self, request):
        user = request.user
        item_id = request.data["item_id"]
        quantity = request.data["quantity"]
        item = MenuItem.objects.get(item_id=item_id)
        Cart.objects.create(
            user=user,
            menuitem=item,
            quantity=quantity,
            unit_price=item.price,
            price=round(item.price * quantity, 2),
        )
        return Response(
            {"response": f"{quantity} {item.title}(s) added to {user.username}'s cart"},
            status=status.HTTP_201_CREATED,
        )

    def delete(self, request):
        user = request.user
        Cart.objects.filter(user=user).delete()
        return Response(
            {"response": f"{user.username}'s cart cleared."}, status=status.HTTP_200_OK
        )


class OrderManagement(CachedResponseMixin, UpdateModelMixin, DestroyModelMixin, ListCreateAPIView):
    """
        Order Management API View.

        This view provides the functionality for creating, viewing, updating, and deleting orders.
        - **Retrieve Orders**: Allows users to retrieve orders based on their role. Managers see all orders, delivery crew sees their assigned orders, and customers see only their own orders.
        - **Create Order**: Customers can create an order based on the contents of their cart. Cart items are moved to the order, and the cart is cleared.
        - **Update Order**: Managers can assign delivery personnel and update the status of an order.
        - **Delete Order**: Only managers can delete an order.

        ### Filters and Search
        - **Filter by**: `status`, `date`, `delivery_crew`, `user`
        - **Search by**: `order_id`, `user`

        ### Permissions
        - Only authenticated users can access order operations.
        - Managers can view all orders and perform all actions.
        - Delivery crew can view and update assigned orders.
        - Customers can view and create their orders only.
    
        Raises:
        - **403 Forbidden**: If a user tries to perform an unauthorized action.
        - **404 Not Found**: If the specified order does not exist.
        - **400 Bad Request**: If required fields are missing in the request.
        - **405 Method Not Allowed**: If managers or delivery crew attempt to create orders.
    """

    queryset = Order.objects.all()
    cache_models = [MenuItem, Group, User, Cart, OrderItem ]
    primary_model = Order
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["status", "date", "delivery_crew", "user"]
    search_fields = ["order_id", "user"]

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="manager").exists():
            return Order.objects.all()
        if user.groups.filter(name="delivery crew").exists():
            return Order.objects.filter(delivery_crew=user)
        return Order.objects.filter(user=user)

    def post(self, request):
        if request.user.groups.filter(name="manager").exists():
            logger.warning(f"Unauthorized  {request.method} Request Blocked At {request.path}")
            return Response(
                {"error": "Managers cannot create orders."},
                status=status.HTTP_405_METHOD_NOT_ALLOWED,
            )
        carts = Cart.objects.filter(user=request.user)
        if not carts.exists():
            logger.warning(f"Invalid {request.method} Request Blocked At {request.path}")
            return Response(
                {"error": "No items in cart."}, status=status.HTTP_400_BAD_REQUEST
            )
        total = sum(cart.price for cart in carts)
        new_order = Order.objects.create(user=request.user, total=total)
        for cart in carts:
            OrderItem.objects.create(
                order=new_order,
                menuitem=cart.menuitem,
                quantity=cart.quantity,
                unit_price=cart.unit_price,
                price=cart.price,
            )
            cart.delete()
            
        return Response(
            {"response": f"Order {new_order.order_id} created."},
            status=status.HTTP_201_CREATED,
        )
