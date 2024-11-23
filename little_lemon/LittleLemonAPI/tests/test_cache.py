# tests.py
import hashlib

from django.contrib.auth.models import Group, User
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from LittleLemonAPI.models import Cart, Category, MenuItem, Order
from LittleLemonAPI.serializers import MenuItemSerializer


class CachingMechanismTestCase(TestCase):
    def setUp(self):
        # Clear the cache before each test
        cache.clear()

        # Create test users
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.manager = User.objects.create_user(
            username="manager", password="managerpass"
        )
        manager_group, created = Group.objects.get_or_create(name="manager")
        self.manager.groups.add(manager_group)
        self.test_category = Category.objects.create(
            title="TEST", slug="test", category_id=1
        )
        # Create test menu items
        self.menu_item1 = MenuItem.objects.create(
            title="Pizza", price=10.00, category=self.test_category, featured=False
        )
        self.menu_item2 = MenuItem.objects.create(
            title="Burger", price=8.00, category=self.test_category, featured=False
        )

        # Set up API clients
        self.client = APIClient()
        self.client.login(username="testuser", password="testpass")

        self.manager_client = APIClient()
        self.manager_client.login(username="manager", password="managerpass")

        # Endpoint URL
        self.menu_items_url = reverse("items-list")

    def seed_database(self):
        new_item1 = MenuItem.objects.create(
            title="Coffee", price=5.00, category=self.test_category, featured=False
        )
        new_item2 = MenuItem.objects.create(
            title="Ribs", price=12.00, category=self.test_category, featured=False
        )
        new_item3 = MenuItem.objects.create(
            title="Chicken", price=11.00, category=self.test_category, featured=False
        )
        return (new_item1, new_item2, new_item3)

    def get_cache_key(self, user, query_params=""):
        user_id = user.id if user.is_authenticated else "anon"
        query_params_hash = hashlib.md5(query_params.encode("utf-8")).hexdigest()
        model_names = "MenuItem"  # Since cache_models = [MenuItem] in the view
        return (
            f"MenuItemsListView_{model_names}_{user_id}_{query_params_hash}_cache_key"
        )

    def test_data_is_cached(self):
        # Make a GET request to the menu items list view
        response = self.client.get(self.menu_items_url)
        self.assertEqual(response.status_code, 200)

        # Generate the expected cache key
        cache_key = self.get_cache_key(self.user)

        # Check that data is cached
        cached_data = cache.get(cache_key)
        self.assertIsNotNone(cached_data)
        # Ensure that the cached data matches the response data
        self.assertEqual(cached_data, response.data)

    def test_cached_data_is_served(self):
        # Make the first request to cache the data
        self.client.get(self.menu_items_url)

        # Clear the MenuItem objects to ensure data is served from cache
        MenuItem.objects.all().delete()

        # Make a second request
        response = self.client.get(self.menu_items_url)

        # The response should still have the data from the cache
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["title"], "Pizza")
        self.assertEqual(response.data[1]["title"], "Burger")

    def test_cache_invalidation_on_create(self):
        # Cache the data
        self.client.get(self.menu_items_url)

        # Add a new menu item
        self.menu_item3, self.menu_item4, self.menu_item5 = self.seed_database()
        # Generate the cache key
        cache_key = self.get_cache_key(self.user)

        # Ensure the cache has been invalidated
        cached_data = cache.get(cache_key)
        self.assertIsNone(cached_data)

        # Make a new request
        response = self.client.get(self.menu_items_url)

        # The new item should be in the response
        self.assertEqual(len(response.data), 3)
        self.assertEqual(response.data[2]["title"], "Salad")

    def test_cache_invalidation_on_update(self):
        # Cache the data
        self.client.get(self.menu_items_url)

        # Update a menu item
        self.menu_item1.title = "Updated Pizza"
        self.menu_item1.save()

        # Generate the cache key
        cache_key = self.get_cache_key(self.user)

        # Ensure the cache has been invalidated
        cached_data = cache.get(cache_key)
        self.assertIsNone(cached_data)

        # Make a new request
        response = self.client.get(self.menu_items_url)

        # The updated item should be in the response
        self.assertEqual(response.data[0]["title"], "Updated Pizza")

    def test_cache_invalidation_on_delete(self):
        # Cache the data
        self.client.get(self.menu_items_url)

        # Delete a menu item
        self.menu_item1.delete()

        # Generate the cache key
        cache_key = self.get_cache_key(self.user)

        # Ensure the cache has been invalidated
        cached_data = cache.get(cache_key)
        self.assertIsNone(cached_data)

        # Make a new request
        response = self.client.get(self.menu_items_url)

        # The deleted item should not be in the response
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Burger")

    def test_fresh_data_after_invalidation(self):
        # Cache the data
        self.client.get(self.menu_items_url)

        # Update a menu item
        self.menu_item1.title = "Fresh Pizza"
        self.menu_item1.save()

        # Make a new request
        response = self.client.get(self.menu_items_url)

        # The response should have fresh data
        self.assertEqual(response.data[0]["title"], "Fresh Pizza")

    def test_cache_key_includes_user_specific_data(self):
        # Make a request as an anonymous user
        anonymous_client = APIClient()
        response_anon = anonymous_client.get(self.menu_items_url)
        self.assertEqual(response_anon.status_code, 200)

        # Generate cache key for anonymous user
        cache_key_anon = self.get_cache_key(User(is_authenticated=False))

        # Check that anonymous user's data is cached separately
        cached_data_anon = cache.get(cache_key_anon)
        self.assertIsNotNone(cached_data_anon)

        # Ensure that the cache keys for authenticated and anonymous users are different
        cache_key_user = self.get_cache_key(self.user)
        self.assertNotEqual(cache_key_anon, cache_key_user)

    def test_cache_with_query_parameters(self):
        # Make a request with a filter
        response_filtered = self.client.get(self.menu_items_url, {"search": "Pizza"})
        self.assertEqual(response_filtered.status_code, 200)
        self.assertEqual(len(response_filtered.data), 1)
        self.assertEqual(response_filtered.data[0]["title"], "Pizza")

        # Generate the cache key with query parameters
        query_params = "search=Pizza"
        cache_key = self.get_cache_key(self.user, query_params)

        # Check that filtered data is cached
        cached_data = cache.get(cache_key)
        self.assertIsNotNone(cached_data)
        self.assertEqual(len(cached_data), 1)
        self.assertEqual(cached_data[0]["title"], "Pizza")

        # Ensure that the cache key is different from the one without query parameters
        default_cache_key = self.get_cache_key(self.user)
        self.assertNotEqual(cache_key, default_cache_key)

    def test_cache_invalidation_does_not_affect_other_users(self):
        # Cache data for both users
        self.client.get(self.menu_items_url)
        self.manager_client.get(self.menu_items_url)

        # Update a menu item
        self.menu_item1.title = "Manager Updated Pizza"
        self.menu_item1.save()

        # Check that both caches are invalidated
        cache_key_user = self.get_cache_key(self.user)
        cache_key_manager = self.get_cache_key(self.manager)

        self.assertIsNone(cache.get(cache_key_user))
        self.assertIsNone(cache.get(cache_key_manager))

        # Make requests again
        response_user = self.client.get(self.menu_items_url)
        response_manager = self.manager_client.get(self.menu_items_url)

        # Both responses should have the updated data
        self.assertEqual(response_user.data[0]["title"], "Manager Updated Pizza")
        self.assertEqual(response_manager.data[0]["title"], "Manager Updated Pizza")

    def test_cache_invalidation_across_multiple_views(self):
        # Assuming there's another view that also caches MenuItem data
        other_view_url = reverse("other-items-list")

        # Cache data from both views
        self.client.get(self.menu_items_url)
        self.client.get(other_view_url)

        # Update a menu item
        self.menu_item1.title = "Updated Across Views"
        self.menu_item1.save()

        # Generate cache keys for both views
        cache_key_main_view = self.get_cache_key(self.user)
        cache_key_other_view = f"OtherItemsListView_MenuItem_{self.user.id}_{hashlib.md5(''.encode('utf-8')).hexdigest()}_cache_key"

        # Ensure both caches are invalidated
        self.assertIsNone(cache.get(cache_key_main_view))
        self.assertIsNone(cache.get(cache_key_other_view))

        # Make requests again
        response_main = self.client.get(self.menu_items_url)
        response_other = self.client.get(other_view_url)

        # Both responses should have the updated data
        self.assertEqual(response_main.data[0]["title"], "Updated Across Views")
        self.assertEqual(response_other.data[0]["title"], "Updated Across Views")

    def test_performance_with_caching(self):
        import time

        # First request (should be slower)
        start_time = time.time()
        self.client.get(self.menu_items_url)
        first_request_time = time.time() - start_time

        # Second request (should be faster due to caching)
        start_time = time.time()
        self.client.get(self.menu_items_url)
        second_request_time = time.time() - start_time

        # The second request should be faster
        self.assertTrue(second_request_time < first_request_time)
