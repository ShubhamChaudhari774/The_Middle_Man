from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

from .models import Profile, Product, Message, RestaurantRequest


class MiddlemanUnitTests(TestCase):
    def setUp(self):
        self.client = Client()

        self.buyer_user = User.objects.create_user(
            username="buyer1",
            password="testpass123",
            first_name="Test",
            last_name="Buyer"
        )
        self.buyer_profile = Profile.objects.create(
            user=self.buyer_user,
            role="buyer",
            business_name="Buyer Biz",
            state="NE"
        )

        self.producer_user = User.objects.create_user(
            username="producer1",
            password="testpass123",
            first_name="Prod",
            last_name="User"
        )
        self.producer_profile = Profile.objects.create(
            user=self.producer_user,
            role="producer",
            business_name="Green Farm",
            state="NE"
        )

    # 1
    def test_home_page_status_code(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

    # 2
    def test_about_page_status_code(self):
        response = self.client.get(reverse("about"))
        self.assertEqual(response.status_code, 200)

    # 3
    def test_browse_page_status_code(self):
        response = self.client.get(reverse("browse"))
        self.assertEqual(response.status_code, 200)

    # 4
    def test_browse_shows_available_product(self):
        Product.objects.create(
            producer=self.producer_profile,
            name="Tomatoes",
            category="Vegetables",
            price=5.00,
            available=True
        )

        response = self.client.get(reverse("browse"))
        self.assertContains(response, "Tomatoes")

    # 5
    def test_browse_hides_unavailable_product(self):
        Product.objects.create(
            producer=self.producer_profile,
            name="Hidden Product",
            category="Vegetables",
            price=7.00,
            available=False
        )

        response = self.client.get(reverse("browse"))
        self.assertNotContains(response, "Hidden Product")

    def test_producer_browse_shows_buyer_requests(self):
        RestaurantRequest.objects.create(
            buyer=self.buyer_profile,
            title="Need local carrots",
            category="Vegetables",
            description="Looking for organic carrots for our restaurant.",
            budget_min=20.00,
            budget_max=50.00,
            active=True
        )

        self.client.login(username="producer1", password="testpass123")
        response = self.client.get(reverse("browse"))
        self.assertContains(response, "Need local carrots")
        self.assertContains(response, "Looking for organic carrots")

    # 6
    def test_view_message_marks_message_as_read(self):
        self.client.login(username="buyer1", password="testpass123")

        msg = Message.objects.create(
            MessageTo="buyer1",
            MessageFrom="producer1",
            MessageBody="Fresh produce available",
            IsNewMessage=True
        )

        response = self.client.get(reverse("viewMessage", args=[msg.id]))
        self.assertEqual(response.status_code, 200)

        msg.refresh_from_db()
        self.assertFalse(msg.IsNewMessage)

    # 7
    def test_only_recipient_can_delete_message(self):
        msg = Message.objects.create(
            MessageTo="buyer1",
            MessageFrom="producer1",
            MessageBody="Delete protection test",
            IsNewMessage=True
        )

        self.client.login(username="producer1", password="testpass123")
        self.client.get(reverse("deleteMessage", args=[msg.id]))
        self.assertTrue(Message.objects.filter(id=msg.id).exists())

        self.client.logout()
        self.client.login(username="buyer1", password="testpass123")
        self.client.get(reverse("deleteMessage", args=[msg.id]))
        self.assertFalse(Message.objects.filter(id=msg.id).exists())
