from django.urls import re_path, path,include
from LittleLemonAPI.views import MenuItemsListView, MenuItemDetailView, ManagerUserManagement, DeliveryCrewUserManagement, CartManagement, OrderManagement

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

def api_root(request, format=format):
    return Response([
        {'Menu Items': reverse('items-list', request=request, format=format)},
        {'Orders': reverse('Order-Management', request=request, format=format)},
        {'Cart': reverse('Cart-Management', request=request, format=format)}
    ])
urlpatterns = [
    re_path(r'^users/', include('djoser.urls')),
    re_path(r'^users/', include('djoser.urls.authtoken')),

    path('menu-items/', MenuItemsListView.as_view(), name="items-list"),
    path('menu-items/<int:item_id>', MenuItemDetailView.as_view(), name="items-detail"),
    path('groups/managers/user', ManagerUserManagement.as_view(), name="Management-Users"),
    path('groups/delivery-crew/user', DeliveryCrewUserManagement.as_view(), name="Delivery-Crew"),
    path('groups/managers/user/<int:id>', ManagerUserManagement.as_view(), name="Management-Users"),
    path('groups/delivery-crew/user', DeliveryCrewUserManagement.as_view(), name="Delivery-Crew"),
    path('cart/menu-items', CartManagement.as_view(), name="Cart-Management"),
    path('orders', OrderManagement.as_view(), name="Order-Management"),
    path('orders/<int:order_id>', OrderManagement.as_view(), name="Order-Detail-Management")
]
