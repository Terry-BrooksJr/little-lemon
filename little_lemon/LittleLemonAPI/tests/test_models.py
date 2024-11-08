from rest_framework.test import APIClient, APITransactionTestCase
from django.test import TestCase

# Create your tests here.
from LittleLemonAPI.models import MenuItem, Category
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User, Group
from django.urls import reverse
import json
from loguru import logger


class TestGetTransactions(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Create test users
        self.test_manager = User.objects.create(
            username="manager1", password="manage1pass"
        )
        self.test_delivery_crew = User.objects.create(
            username="deliverycrew1", password="manage1pass"
        )
        self.test_customer = User.objects.create(
            username="customer1", password="manage1pass"
        )
        # Create Test Category and 2 Test Products
        self.test_category = Category.objects.create(
            category_id=1, title="Test", slug="Test"
        )
        self.test_product1 = MenuItem.objects.create(
            item_id=101,
            title="test_item101",
            price=5.55,
            featured=False,
            is_on_sale=True,
            category=self.test_category,
        )
        self.test_product2 = MenuItem.objects.create(
            item_id=102,
            title="test_item102",
            price=10.10,
            featured=True,
            is_on_sale=False,
            category=self.test_category,
        )
        # Create Needed Group and Add Members
        self.managers_group = Group.objects.create(name="manager")
        self.delivery_group = Group.objects.create(name="delivery crew")
        self.managers_group.user_set.add(self.test_manager)
        self.delivery_group.user_set.add(self.test_delivery_crew)

        # cREATE required Tokens
        self.manager_token = Token.objects.create(user=self.test_manager)
        self.customer_token = Token.objects.create(user=self.test_customer)
        self.delivery_crew_token = Token.objects.create(user=self.test_delivery_crew)

    def test_api_landing(self):
        response = self.client.get(reverse("API-Root", query_kwargs={"format": "json"}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "primary API Endpoints")
        self.assertIn(
            "Menu Items",
            json.loads(response["text"]).keys()["primary API Endpoints"][0],
        )

    def test_get_menu_items_list(self):
        self.client.headers["Authorization"] = f"Token {self.manager_token}"
        url = f"https://m366g28j-8000.use.devtunnels.ms{reverse('items-list')}?format=json"
        logger.debug(url)
        response = self.client.get(url=url)
        logger.debug(str(response))
        logger.debug(dir(response.body))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json.loads(response.text)), 2)

    def test_get_single_item(self):
        response = self.client.get(
            path=reverse("items-detail", kwargs={"item_id": 101}),
            query_params={"format": "json"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.text).get("product_sku"), self.test_product1.item_id
        )

    def test_get_list_of_managers(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.manager_token.key}")
        response = self.client.get(
            reverse("Management-Users", query_kwargs={"format": "json"})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json.loads(response.text)), 2)
