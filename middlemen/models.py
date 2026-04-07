from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    # Defines user roles in the system
    ROLE_CHOICES = [
        ('producer', 'Producer'),
        ('buyer', 'Buyer'),
    ]

    # One-to-one link with Django's built-in User model
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    # Role of the user (producer or buyer)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='buyer')

    # Optional business-related details
    business_name = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=50, blank=True)
    zip_code = models.CharField(max_length=10, blank=True)

    # Optional profile information
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    # Timestamp when profile is created
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"

    # Helper method to check if user is a producer
    def is_producer(self):
        return self.role == 'producer'

    # Helper method to check if user is a buyer
    def is_buyer(self):
        return self.role == 'buyer'


class Product(models.Model):
    # Product categories for filtering and organization
    CATEGORY_CHOICES = [
        ('Vegetables', 'Vegetables'),
        ('Fruits', 'Fruits'),
        ('Dairy & Eggs', 'Dairy & Eggs'),
        ('Meat & Poultry', 'Meat & Poultry'),
    ]

    # Product belongs to a producer profile
    producer = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='products')

    # Basic product information
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)

    # Pricing and unit (e.g., per lb, per unit)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    unit = models.CharField(max_length=30, default='lb')

    # Availability status of product
    available = models.BooleanField(default=True)

    # Optional product image
    image = models.ImageField(upload_to='products/', blank=True, null=True)

    # Timestamps for tracking product lifecycle
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} by {self.producer.business_name or self.producer.user.username}"

class Customer(models.Model):
    # Username field (should be the same as the username field in the Django User table)
    username = models.CharField(primary_key=True, max_length=30)

    def createCustomer(username: str) -> int:
        """
        This function is intended to be called by the view to create a new Customer object in the Customer table.
        
        Returns: 0 if succeeded; 1 if failed

        """
        try:
            customer = Customer.objects.get(username=username)
            return 1
        except:
            newCustomer = Customer(username=username)
            newCustomer.save()
            return 0
    
    def deleteCustomer(username: str) -> int:
        """
        This function is intended to be called by the view to delete a Customer object in the Customer table.
        """
        try:
            customer = Customer.objects.get(username=username)
            customer.delete()
        except:
            return None

class Producer(models.Model):
    # Username field (should be the same as the username field in the Django User table)
    username = models.CharField(primary_key=True, max_length=30)

    def createProducer(username: str) -> int:
        """
        This function is intended to be called by the view to create a new Producer object in the Producer table.

        Returns: 0 if succeeded; 1 if failed
        
        """
        try:
            producer = Producer.objects.get(username=username)
            return 1
        except:
            newProducer = Producer(username=username)
            newProducer.save()
            return 0

    def deleteProducer(username: str) -> int:
        """
        This function is intended to be called by the view to delete a Producer object in the Producer table. 
        
        Input validation is not performed because if the item is not present, no error will be thrown.
        """
        try:
            producer = Producer.objects.get(username=username)
            producer.delete()
        except:
            return None

class RestaurantRequest(models.Model):
    # Categories for requested items
    CATEGORY_CHOICES = [
        ('Vegetables', 'Vegetables'),
        ('Fruits', 'Fruits'),
        ('Dairy & Eggs', 'Dairy & Eggs'),
        ('Meat & Poultry', 'Meat & Poultry'),
    ]

    # Request created by a buyer profile
    buyer = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='requests')

    # Request details
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)

    # Budget range (optional)
    budget_min = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    budget_max = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    # Whether the request is still active
    active = models.BooleanField(default=True)

    # Timestamp when request was created
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} by {self.buyer.business_name or self.buyer.user.username}"


class Message(models.Model):
    # User who sends the message
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')

    # User who receives the message
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')

    # Message content
    body = models.TextField()

    # Read/unread status
    read = models.BooleanField(default=False)

    # Timestamp of message creation
    created_at = models.DateTimeField(auto_now_add=True)

    # Default ordering of messages (oldest first)
    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"From {self.sender} to {self.recipient} at {self.created_at:%Y-%m-%d %H:%M}"


class SavedProducer(models.Model):
    # Buyer who saved a producer
    buyer = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='saved_producers')

    # Producer profile being saved
    producer = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='saved_by')

    # Timestamp when saved
    created_at = models.DateTimeField(auto_now_add=True)

    # Prevent duplicate saves of same producer by same buyer
    class Meta:
        unique_together = ('buyer', 'producer')

    def __str__(self):
        return f"{self.buyer} saved {self.producer}"