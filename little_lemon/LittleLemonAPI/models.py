from django.db import models
from django.contrib.auth import get_user_model
from django_prometheus.models import ExportModelOperationsMixin



# Create your models here.
class Category(ExportModelOperationsMixin('menu-categories'),models.Model):
    category_id = models.AutoField(primary_key=True )
    title = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255, unique=True)

    def __str__(self):
        return f"{self.title}: {self.category_id}"

    class Meta:
        db_table = "menu_categories "
        ordering = ["title"]
        verbose_name = "category"
        verbose_name_plural = "catagories"


class MenuItem(ExportModelOperationsMixin('menu_items'),models.Model):
    item_id = models.AutoField(primary_key=True )
    title = models.CharField(max_length=255, db_index=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, db_index=True)
    featured = models.BooleanField(db_index=True, default=False)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.title} ({self.category.title})"

    class Meta:
        db_table = "menu_items"
        ordering = ["category", "title"]
        verbose_name = "menu item"
        verbose_name_plural = "menu items"

class Cart(ExportModelOperationsMixin('carts'),models.Model):
    cart_id = models.AutoField(primary_key=True )
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    menuitem = models.ForeignKey(MenuItem, on_delete=models.PROTECT)
    quantity = models.SmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, null=True)
 
    class Meta:
        unique_together = ("menuitem", "user")
        db_table = "user_carts"
        ordering = ["user"]
        verbose_name = "cart"
        verbose_name_plural = "carts"



    def __str__(self):
        return f"{self.user} - {self.price}"

class Order(ExportModelOperationsMixin('orders'),models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="customer")
    delivery_crew = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        related_name="delivery_crew",
        null=True,
    )
    status = models.BooleanField(db_index=True, default=0)
    total = models.DecimalField(max_digits=6, decimal_places=2)
    date = models.DateField(db_index=True, auto_now=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, null=True)

    def __str__(self):
        return f"{self.user} - {self.date} - {self.total} ({self.status})"

    class Meta:
        db_table = "orders"
        ordering = ["user", "date", "status"]
        verbose_name = "order"
        verbose_name_plural = "orders"


class OrderItem(ExportModelOperationsMixin('order-items'),models.Model):
    order_item_id = models.AutoField(primary_key=True )
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    price = models.DecimalField(max_digits=6, decimal_places=2, null=True)

    def __str__(self):
        return f"{self.order} ({self.menuitem})"

    class Meta:
        unique_together = ("order", "menuitem")
        db_table = "order_items"
        ordering = ["order"]
        verbose_name = "order item"
        verbose_name_plural = "order items"

    def __str__(self):
        return f"{self.order} ({self.menuitem})"