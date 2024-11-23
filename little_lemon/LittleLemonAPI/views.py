import json
from datetime import datetime

from django.contrib.auth.models import Group, User
from django.db import IntegrityError
from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import (OpenApiExample, OpenApiParameter,
                                   OpenApiResponse, extend_schema,
                                   extend_schema_view, inline_serializer)
from loguru import logger
from rest_framework import filters, status
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.generics import (GenericAPIView, ListCreateAPIView,
                                     RetrieveAPIView,
                                     RetrieveUpdateDestroyAPIView)
from rest_framework.mixins import DestroyModelMixin, UpdateModelMixin
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer
from rest_framework.response import Response

from little_lemon.utils.cache import CachedResponseMixin
from LittleLemonAPI.models import Cart, MenuItem, Order, OrderItem
from LittleLemonAPI.serializers import (CartSerializer,
                                        MenuItemDetailSerializer,
                                        MenuItemSerializer, OrderSerializer,
                                        UserSerializer)


class APIRootView(RetrieveAPIView):
    queryset = None
    primary_model = None
    cache_models = [None]
    serializer_class = inline_serializer(name="API Root", fields={})
    filter_backends = None
    permission_classes = [AllowAny]

    def get(self, request):
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


@extend_schema_view(
    list=extend_schema(
        tags=["Inventory Management"],
        parameters=[
            OpenApiParameter(
                name="featured",
                description="Filter menu items by whether they are featured (true/false).",
                required=False,
                type=bool,
            ),
            OpenApiParameter(
                name="category",
                description="Filter menu items by category ID.",
                required=False,
                type=int,
            ),
            OpenApiParameter(
                name="title",
                description="Search menu items by title.",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="is_on_sale",
                description="Filter menu items by whether they are on sale (true/false).",
                required=False,
                type=bool,
            ),
            OpenApiParameter(
                name="contains_dairy",
                description="Filter menu items by whether they contain dairy (true/false).",
                required=False,
                type=bool,
            ),
            OpenApiParameter(
                name="contains_treenuts",
                description="Filter menu items by whether they contain tree nuts (true/false).",
                required=False,
                type=bool,
            ),
            OpenApiParameter(
                name="contains_gluten",
                description="Filter menu items by whether they contain gluten (true/false).",
                required=False,
                type=bool,
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=MenuItemSerializer(many=True),
                description="A list of menu items matching the query parameters.",
                examples=[
                    OpenApiExample(
                        name="Successful Response",
                        value=[
                            {
                                "id": 1,
                                "title": "Spaghetti Bolognese",
                                "category": "Main Course",
                                "featured": True,
                                "is_on_sale": False,
                                "contains_dairy": False,
                                "contains_treenuts": False,
                                "contains_gluten": True,
                            },
                            {
                                "id": 2,
                                "title": "Vegan Burger",
                                "category": "Snacks",
                                "featured": False,
                                "is_on_sale": True,
                                "contains_dairy": False,
                                "contains_treenuts": False,
                                "contains_gluten": False,
                            },
                        ],
                        description="Example response for a successful menu item list query.",
                    )
                ],
            ),
        },
    ),
)
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
    cache_models = [Group, User]
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

    @extend_schema(
        tags=["Inventory Management"],
        parameters=[
            OpenApiParameter(
                name="featured",
                description="Filter menu items by whether they are featured (true/false).",
                required=False,
                type=bool,
            ),
            OpenApiParameter(
                name="category",
                description="Filter menu items by category ID.",
                required=False,
                type=int,
            ),
            OpenApiParameter(
                name="title",
                description="Search menu items by title.",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="is_on_sale",
                description="Filter menu items by whether they are on sale (true/false).",
                required=False,
                type=bool,
            ),
            OpenApiParameter(
                name="contains_dairy",
                description="Filter menu items by whether they contain dairy (true/false).",
                required=False,
                type=bool,
            ),
            OpenApiParameter(
                name="contains_treenuts",
                description="Filter menu items by whether they contain tree nuts (true/false).",
                required=False,
                type=bool,
            ),
            OpenApiParameter(
                name="contains_gluten",
                description="Filter menu items by whether they contain gluten (true/false).",
                required=False,
                type=bool,
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=MenuItemSerializer(many=True),
                description="A list of menu items matching the query parameters.",
                examples=[
                    OpenApiExample(
                        name="Successful Response",
                        value=[
                            {
                                "id": 1,
                                "title": "Spaghetti Bolognese",
                                "category": "Main Course",
                                "featured": True,
                                "is_on_sale": False,
                                "contains_dairy": False,
                                "contains_treenuts": False,
                                "contains_gluten": True,
                            },
                            {
                                "id": 2,
                                "title": "Vegan Burger",
                                "category": "Snacks",
                                "featured": False,
                                "is_on_sale": True,
                                "contains_dairy": False,
                                "contains_treenuts": False,
                                "contains_gluten": False,
                            },
                        ],
                        description="Example response for a successful menu item list query.",
                    )
                ],
            ),
            201: OpenApiResponse(
                response=MenuItemSerializer,
                description="Menu item successfully created.",
                examples=[
                    OpenApiExample(
                        name="Successful Creation",
                        value={
                            "id": 3,
                            "title": "Caesar Salad",
                            "category": "Salads",
                            "featured": True,
                            "is_on_sale": False,
                            "contains_dairy": True,
                            "contains_treenuts": False,
                            "contains_gluten": True,
                        },
                        description="Example response for successfully creating a menu item.",
                    )
                ],
            ),
            403: OpenApiResponse(
                response={"error": "Action restricted to managers only."},
                description="Unauthorized access - user is not a manager.",
            ),
            400: OpenApiResponse(
                response={
                    "error": "Unable to add menu item",
                    "reason": "Detailed error reason.",
                },
                description="Failed to create the menu item due to invalid data.",
            ),
        },
    )
    def create(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="manager").exists():
            logger.warning(
                f"Unauthorized  POST Request Blocked At {reverse('items-detail')}"
            )
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
    cache_models = [Group, User]
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = "item_id"

    def perform_update_or_destroy(self, request, method):
        if request.user.groups.filter(name="manager").exists():
            return method(request)
        logger.warning(
            f"Unauthorized {method.__name__} Request Blocked At {reverse('items-detail')}"
        )
        return Response(
            {"error": "Action restricted to managers only."},
            status=status.HTTP_403_FORBIDDEN,
        )

    @extend_schema(
        tags=["Inventory Management"],
        responses={
            200: OpenApiResponse(
                response=MenuItemDetailSerializer,
                description="Successfully retrieved the menu item details.",
                examples=[
                    OpenApiExample(
                        name="Successful Retrieve",
                        value={
                            "id": 1,
                            "title": "Spaghetti Bolognese",
                            "category": "Main Course",
                            "featured": True,
                            "is_on_sale": False,
                            "contains_dairy": False,
                            "contains_treenuts": False,
                            "contains_gluten": True,
                        },
                        description="Example response for retrieving a menu item.",
                    )
                ],
            ),
            403: OpenApiResponse(
                response={"error": "Action restricted to managers only."},
                description="Unauthorized access - user is not a manager.",
            ),
            404: OpenApiResponse(
                response={"error": "Menu item not found."},
                description="The requested menu item does not exist.",
            ),
        },
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        tags=["Inventory Management"],
        request=MenuItemDetailSerializer,
        responses={
            200: OpenApiResponse(
                response=MenuItemDetailSerializer,
                description="Menu item successfully updated.",
                examples=[
                    OpenApiExample(
                        name="Successful Update",
                        value={
                            "id": 1,
                            "title": "Updated Spaghetti Bolognese",
                            "category": "Main Course",
                            "featured": True,
                            "is_on_sale": True,
                            "contains_dairy": False,
                            "contains_treenuts": False,
                            "contains_gluten": True,
                        },
                        description="Example response for updating a menu item.",
                    )
                ],
            ),
            403: OpenApiResponse(
                response={"error": "Action restricted to managers only."},
                description="Unauthorized access - user is not a manager.",
            ),
            404: OpenApiResponse(
                response={"error": "Menu item not found."},
                description="The requested menu item does not exist.",
            ),
        },
    )
    def update(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="manager").exists():
            logger.warning(f"Unauthorized POST Request Blocked At {request.path}")
            return Response(
                {"error": "Action restricted to managers only."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().update(request, *args, **kwargs)

    @extend_schema(
        tags=["Inventory Management"],
        responses={
            204: OpenApiResponse(description="Menu item successfully deleted."),
            403: OpenApiResponse(
                response={"error": "Action restricted to managers only."},
                description="Unauthorized access - user is not a manager.",
            ),
            404: OpenApiResponse(
                response={"error": "Menu item not found."},
                description="The requested menu item does not exist.",
            ),
        },
    )
    def destroy(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="manager").exists():
            logger.warning(f"Unauthorized POST Request Blocked At {request.path}")
            return Response(
                {"error": "Action restricted to managers only."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().destroy(request, *args, **kwargs)

    @extend_schema(
        tags=["Inventory Management"],
        request=MenuItemDetailSerializer,
        responses={
            200: OpenApiResponse(
                response=MenuItemDetailSerializer,
                description="Menu item partially updated.",
                examples=[
                    OpenApiExample(
                        name="Partial Update",
                        value={"id": 1, "title": "Partially Updated Spaghetti"},
                        description="Example response for partially updating a menu item.",
                    )
                ],
            ),
            403: OpenApiResponse(
                response={"error": "Action restricted to managers only."},
                description="Unauthorized access - user is not a manager.",
            ),
            404: OpenApiResponse(
                response={"error": "Menu item not found."},
                description="The requested menu item does not exist.",
            ),
        },
    )
    def partial_update(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="manager").exists():
            logger.warning(f"Unauthorized POST Request Blocked At {request.path}")
            return Response(
                {"error": "Action restricted to managers only."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().partial_update(request, *args, **kwargs)


class ManagerUserManagement(
    CachedResponseMixin, UpdateModelMixin, DestroyModelMixin, ListCreateAPIView
):

    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ["username", "first_name", "last_name"]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["User Management"],
        request={"type": "object", "properties": {"username": {"type": "string"}}},
        responses={
            201: OpenApiResponse(
                response={"response": "Username added to manager group."},
                examples=[
                    OpenApiExample(
                        name="Add User to Manager Group",
                        value={"response": "john_doe added to manager group."},
                        description="A user was successfully added to the manager group.",
                    )
                ],
            ),
            400: OpenApiResponse(
                response={"error": 'POST body must include "username".'},
                description="Request missing required username field.",
            ),
            403: OpenApiResponse(
                response={"error": "Action restricted to managers only."},
                description="Non-managers cannot perform this action.",
            ),
        },
    )
    def post(self, request):
        if not request.user.groups.filter(name="manager").exists():
            logger.warning(f"Unauthorized POST Request Blocked At {request.path}")
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
        except KeyError:
            return Response(
                {"error": 'POST body must include "username".'},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @extend_schema(
        tags=["User Management"],
        responses={
            200: OpenApiResponse(
                response={"response": "Username removed from manager group."},
                examples=[
                    OpenApiExample(
                        name="Remove User from Manager Group",
                        value={"response": "john_doe removed from manager group."},
                        description="A user was successfully removed from the manager group.",
                    )
                ],
            ),
            403: OpenApiResponse(
                response={"error": "Action restricted to managers only."},
                description="Non-managers cannot perform this action.",
            ),
            404: OpenApiResponse(
                response={"error": "User not found."},
                description="The specified user does not exist.",
            ),
        },
    )
    def delete(self, request, id):
        if not request.user.groups.filter(name="manager").exists():
            logger.warning(f"Unauthorized DELETE Request Blocked At {request.path}")
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

    @extend_schema(
        tags=["User Management"],
        responses={
            200: OpenApiResponse(
                response=UserSerializer(many=True),
                examples=[
                    OpenApiExample(
                        name="List Managers",
                        value=[
                            {
                                "id": 1,
                                "username": "manager1",
                                "first_name": "John",
                                "last_name": "Doe",
                            },
                            {
                                "id": 2,
                                "username": "manager2",
                                "first_name": "Jane",
                                "last_name": "Smith",
                            },
                        ],
                        description="List of all users in the manager group.",
                    )
                ],
            ),
            403: OpenApiResponse(
                response={"error": "Action restricted to managers only."},
                description="Non-managers cannot perform this action.",
            ),
        },
    )
    def get(self, request):
        if not request.user.groups.filter(name="manager").exists():
            logger.warning(f"Unauthorized GET Request Blocked At {request.path}")
            return Response(
                {"error": "Action restricted to managers only."},
                status=status.HTTP_403_FORBIDDEN,
            )
        managers = User.objects.filter(groups__name="manager")
        serialized_managers = UserSerializer(managers, many=True)
        return Response(serialized_managers.data, status=status.HTTP_200_OK)


class DeliveryCrewUserManagement(
    CachedResponseMixin, UpdateModelMixin, DestroyModelMixin, ListCreateAPIView
):

    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ["username", "first_name", "last_name"]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["User Management"],
        request={"type": "object", "properties": {"username": {"type": "string"}}},
        responses={
            201: OpenApiResponse(
                response={"response": "Username added to delivery crew group."},
                examples=[
                    OpenApiExample(
                        name="Add User to Delivery Crew Group",
                        value={"response": "john_doe added to delivery crew group."},
                        description="A user was successfully added to the delivery crew group.",
                    )
                ],
            ),
            400: OpenApiResponse(
                response={"error": 'POST body must include "username".'},
                description="Request missing required username field.",
            ),
            403: OpenApiResponse(
                response={"error": "Action restricted to managers only."},
                description="Non-managers cannot perform this action.",
            ),
        },
    )
    def post(self, request):
        if not request.user.groups.filter(name="manager").exists():
            logger.warning(f"Unauthorized POST Request Blocked At {request.path}")
            return Response(
                {"error": "Action restricted to managers only."},
                status=status.HTTP_403_FORBIDDEN,
            )
        try:
            username = request.data["username"]
            user = get_object_or_404(User, username=username)
            Group.objects.get(name="delivery crew").user_set.add(user)
            return Response(
                {"response": f"{user.username} added to delivery crew group."},
                status=status.HTTP_201_CREATED,
            )
        except KeyError:
            return Response(
                {"error": 'POST body must include "username".'},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @extend_schema(
        tags=["User Management"],
        responses={
            200: OpenApiResponse(
                response={"response": "Username removed from delivery crew group."},
                examples=[
                    OpenApiExample(
                        name="Remove User from Manager Group",
                        value={
                            "response": "john_doe removed from delivery crew group."
                        },
                        description="A user was successfully removed from the delivery crew group.",
                    )
                ],
            ),
            403: OpenApiResponse(
                response={"error": "Action restricted to managers only."},
                description="Non-managers cannot perform this action.",
            ),
            404: OpenApiResponse(
                response={"error": "User not found."},
                description="The specified user does not exist.",
            ),
        },
    )
    def delete(self, request, id):
        if not request.user.groups.filter(name="manager").exists():
            logger.warning(f"Unauthorized DELETE Request Blocked At {request.path}")
            return Response(
                {"error": "Action restricted to managers only."},
                status=status.HTTP_403_FORBIDDEN,
            )
        user = get_object_or_404(User, id=id)
        Group.objects.get(name="delivery crew").user_set.remove(user)
        return Response(
            {"response": f"{user.username} removed from delivery crew group."},
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=["User Management"],
        responses={
            200: OpenApiResponse(
                response=UserSerializer(many=True),
                examples=[
                    OpenApiExample(
                        name="List Delivery Crew",
                        value=[
                            {
                                "id": 1,
                                "username": "manager1",
                                "first_name": "John",
                                "last_name": "Doe",
                            },
                            {
                                "id": 2,
                                "username": "manager2",
                                "first_name": "Jane",
                                "last_name": "Smith",
                            },
                        ],
                        description="List of all users in the manager group.",
                    )
                ],
            ),
            403: OpenApiResponse(
                response={"error": "Action restricted to managers only."},
                description="Non-managers cannot perform this action.",
            ),
        },
    )
    def get(self, request):
        if not request.user.groups.filter(name="manager").exists():
            logger.warning(f"Unauthorized GET Request Blocked At {request.path}")
            return Response(
                {"error": "Action restricted to managers only."},
                status=status.HTTP_403_FORBIDDEN,
            )
        managers = User.objects.filter(groups__name="delivery crew")
        serialized_managers = UserSerializer(managers, many=True)
        return Response(serialized_managers.data, status=status.HTTP_200_OK)


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
    cache_models = [Group]
    cache_models = [MenuItem, Group, User]
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def calculate_price(self, quantity, unit_price):
        return round(float(quantity) * float(unit_price), 2)

    @extend_schema(
        tags=["Order Management"],
        responses={
            200: OpenApiResponse(
                response={"type": "object"},
                description="Successfully retrieved the cart contents.",
                examples=[
                    OpenApiExample(
                        name="Empty Cart",
                        value={
                            "cart": {
                                "summary": {
                                    "customer": "Doe, John",
                                    "number_of_items": 0,
                                    "total_cost_USD": "$0.00",
                                },
                                "contents": ["No Items Currently In Cart"],
                            }
                        },
                    ),
                    OpenApiExample(
                        name="Non-Empty Cart",
                        value={
                            "cart": {
                                "summary": {
                                    "customer": "Doe, John",
                                    "number_of_items": 3,
                                    "total_cost_USD": "$45.00",
                                },
                                "contents": [
                                    {
                                        "product_name": "Spaghetti",
                                        "product_sku": 1,
                                        "quantity": 2,
                                        "price per item": 10.0,
                                        "price": 20.0,
                                    },
                                    {
                                        "product_name": "Salad",
                                        "product_sku": 2,
                                        "quantity": 1,
                                        "price per item": 25.0,
                                        "price": 25.0,
                                    },
                                ],
                            }
                        },
                    ),
                ],
            )
        },
    )
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
                    "price per item": round(float(cart.menuitem.price), 2),
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
                },
                status=status.HTTP_200_OK,
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
                        "contents": ["No Items Currently In Cart"],
                    }
                },
                status=status.HTTP_200_OK,
            )

    @extend_schema(
        tags=["Order Management"],
        request={
            "type": "object",
            "properties": {
                "item_id": {"type": "integer"},
                "quantity": {"type": "integer"},
            },
        },
        responses={
            201: OpenApiResponse(
                description="Item successfully added to the cart.",
                examples=[
                    OpenApiExample(
                        name="Item Added",
                        value={"response": "2 Spaghetti(s) added to johndoe's cart"},
                    )
                ],
            ),
            400: OpenApiResponse(
                response={
                    "error": 'Request body must include "quantity" and "item_id".'
                },
                description="Invalid request data.",
            ),
            404: OpenApiResponse(
                response={"error": "Item does not exist."},
                description="Item ID does not match any existing menu item.",
            ),
        },
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

    @extend_schema(
        tags=["Order Management"],
        responses={
            200: OpenApiResponse(
                description="Successfully cleared the cart.",
                examples=[
                    OpenApiExample(
                        name="Cart Cleared",
                        value={"response": "johndoe's cart cleared."},
                    )
                ],
            )
        },
    )
    def delete(self, request):
        user = request.user
        Cart.objects.filter(user=user).delete()
        return Response(
            {"response": f"{user.username}'s cart cleared."}, status=status.HTTP_200_OK
        )


class OrderManagement(
    CachedResponseMixin, UpdateModelMixin, DestroyModelMixin, ListCreateAPIView
):
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
    cache_models = [MenuItem, Group, User, Cart, OrderItem]
    primary_model = Order
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["status", "date", "delivery_crew", "user"]
    search_fields = ["order_id", "user"]

    @extend_schema(
        tags=["Order Management"],
        responses={
            200: OpenApiResponse(
                response=OrderSerializer(many=True),
                description="Successfully retrieved the orders.",
                examples=[
                    OpenApiExample(
                        name="Manager View",
                        value=[
                            {
                                "order_id": 1,
                                "user": "johndoe",
                                "status": "Pending",
                                "total": 45.0,
                            },
                            {
                                "order_id": 2,
                                "user": "janedoe",
                                "status": "Completed",
                                "total": 75.0,
                            },
                        ],
                    ),
                    OpenApiExample(
                        name="Customer View",
                        value=[
                            {"order_id": 3, "status": "Pending", "total": 45.0},
                        ],
                    ),
                ],
            ),
            403: OpenApiResponse(
                response={"error": "Unauthorized access."},
                description="User does not have permission to view these orders.",
            ),
        },
    )
    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="manager").exists():
            return Order.objects.all()
        if user.groups.filter(name="delivery crew").exists():
            return Order.objects.filter(delivery_crew=user)
        return Order.objects.filter(user=user)

    @extend_schema(
        tags=["Order Management"],
        request={"type": "object"},
        responses={
            201: OpenApiResponse(
                description="Order created successfully.",
                examples=[
                    OpenApiExample(
                        name="Order Created",
                        value={"response": "Order 1234 created."},
                    )
                ],
            ),
            400: OpenApiResponse(
                response={"error": "No items in cart."},
                description="The cart is empty.",
            ),
            405: OpenApiResponse(
                response={"error": "Managers cannot create orders."},
                description="Action restricted to customers only.",
            ),
        },
    )
    def post(self, request):
        if request.user.groups.filter(name="manager").exists():
            logger.warning(
                f"Unauthorized  {request.method} Request Blocked At {request.path}"
            )
            return Response(
                {"error": "Managers cannot create orders."},
                status=status.HTTP_405_METHOD_NOT_ALLOWED,
            )
        carts = Cart.objects.filter(user=request.user)
        if not carts.exists():
            logger.warning(
                f"Invalid {request.method} Request Blocked At {request.path}"
            )
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
