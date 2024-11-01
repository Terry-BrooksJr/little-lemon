from django.urls import re_path, path,include
from LittleLemonAPI.views import MenuItemsListView, MenuItemDetailView, ManagerUserManagement, DeliveryCrewUserManagement, CartManagement
urlpatterns = [
    re_path(r'^users/', include('djoser.urls')),
    path('menu-items/', MenuItemsListView.as_view(), name="items-list"),
    path('menu-items/<int:item_id>', MenuItemDetailView.as_view(), name="items-detail"),
    path('groups/managers/user', ManagerUserManagement.as_view(), name="Management-Users"),
    path('groups/delivery-crew/user', DeliveryCrewUserManagement.as_view(), name="Delivery-Crew"),
    path('groups/managers/user/<int:id>', ManagerUserManagement.as_view(), name="Management-Users"),
    path('groups/delivery-crew/user`', DeliveryCrewUserManagement.as_view(), name="Delivery-Crew"),
    path('cart/menu-items', CartManagement.as_view(), name="Cart-Management")
]
