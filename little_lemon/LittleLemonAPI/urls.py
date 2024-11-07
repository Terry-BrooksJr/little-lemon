from django.urls import include, path, re_path

from LittleLemonAPI.views import (
    CartManagement,
    DeliveryCrewUserManagement,
    ManagerUserManagement,
    MenuItemDetailView,
    MenuItemsListView,
    OrderManagement,
)

urlpatterns = [
    re_path(r"^users/", include("djoser.urls")),
    re_path(r"^users/", include("djoser.urls.authtoken")),
    path("menu-items/", MenuItemsListView.as_view(), name="items-list"),
    path("menu-items/<int:item_id>", MenuItemDetailView.as_view(), name="items-detail"),
    path(
        "groups/managers/user", ManagerUserManagement.as_view(), name="Management-Users"
    ),
    path(
        "groups/delivery-crew/user",
        DeliveryCrewUserManagement.as_view(),
        name="Delivery-Crew",
    ),
    path(
        "groups/managers/user/<int:id>",
        ManagerUserManagement.as_view(),
        name="Management-Users",
    ),
    path(
        "groups/delivery-crew/user/<int:id>",
        DeliveryCrewUserManagement.as_view(),
        name="Delivery-Crew",
    ),
    path("cart/menu-items", CartManagement.as_view(), name="Cart-Management"),
    path("orders", OrderManagement.as_view(), name="Order-Management"),
    path(
        "orders/<int:order_id>",
        OrderManagement.as_view(),
        name="Order-Detail-Management",
    ),


]
