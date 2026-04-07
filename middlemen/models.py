from django.db import models
from django.contrib.auth.models import User

# Create your models here.
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

class Product(models.Model):
    # User is used as a foreign key here; the proper way to obtain objects from this table pertaining to a user is to take the user object itself (not the username) and use it as the foreign key to filter by the user object
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # ProductID is formed by combining the username of the user and appending an integer at the end beginning at zero
    productID = models.CharField(primary_key=True, max_length=50)
    
    # ProductName is the name of the product to display to the user
    productName = models.CharField(max_length=30)

    # CostPerUnits is the amount of money in dollars per units that the product costs
    costPerUnits = models.DecimalField(max_digits=10, decimal_places=2)

    # Units is bushels, pounds, etc.
    units = models.CharField(max_length=20)

    def createProduct(user: User, productID: str, productName: str, costPerUnits: float, units: str) -> int:
        """
        This function is intended to be called by the view to create a product in the Product table.

        Returns: 0 if there is no error; a positive integer as follows if there is an error:
            1 -- if the productName field did not match the requirements in the model
            2 -- if the costPerUnits field did not match the requirements in the model
            3 -- if the units field did not match the requirements in the model
        """
        if len(productName) > 30:
            return 1
        elif costPerUnits > 99999999.99:
            return 2
        elif len(units) > 20:
            return 3
        else:
            product = Product(user=user, productID=productID, productName=productName, costPerUnits=costPerUnits, units=units)
            product.save()
            return 0

    def editProduct(productID: str, productName: str, costPerUnits: float, units: str) -> int:
        """
        This function is intended to be called by the view to edit an existing product in the Product table.

        Returns: 0 if there is no error; a positive integer as follows if there is an error:
            1 -- if the productID field did not match an object in the product table
            2 -- if the productName field did not match the requirements in the model
            3 -- if the costPerUnits field did not match the requirements in the model
            4 -- if the units field did not match the requirements in the model
        """
        product = Product.objects.get(productID=productID)
        if product == None:
            return 1
        elif len(productName) > 30:
            return 2
        elif costPerUnits > 99999999.99:
            return 3
        elif len(units) > 20:
            return 4
        else:
            product.productName = productName
            product.costPerUnits = costPerUnits
            product.units = units
            product.save()
            return 0

    def deleteProduct(productID: str) -> None:
        """
        This function is intended to be called by the view to delete an existing product in the Product table.

        Returns: None

        No input validation is performed, because no error will arise if an object does not exist.
        """
        try:
            product = Product.objects.get(productID=productID)
            product.delete()
        except:
            return None

class Location(models.Model):
    # User is used as a foreign key here; the proper way to obtain objects from this table pertaining to a user is to take the user object itself (not the username) and use it as the foreign key to filter by the user object
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # LocationID is formed by combining the username of the user and appending an integer at the end beginning at zero
    locationID = models.CharField(primary_key=True, max_length=50)
    
    # City is the name of the City
    city = models.CharField(max_length=30)

    # State is the two letter abbreviation of the State
    state = models.CharField(max_length=2)
    
    # Address is the Address of the location
    address = models.CharField(max_length=50)

    # Zip Code is the five or nine digit version of the zip code
    zipCode = models.CharField(max_length=10)

    def createLocation(user: User, locationID: str, city: str, state: str, address: str, zipCode: str) -> int:
        """
        This function is intended to be called by the view to create a location in the Location table.

        Returns: 0 if there is no error; a positive integer if there is an error:
            1 -- if there is an issue with the locationID
            2 -- if there is an issue with the city
            3 -- if there is an issue with the state
            4 -- if there is an issue with the address
            5 -- if there is an issue with the zipCode
        """
        if len(locationID) > 30:
            return 1
        elif len(city) > 30:
            return 2
        elif len(state) != 2:
            return 3
        elif len(address) > 50:
            return 4
        elif len(zipCode) > 10:
            return 5
        else:
            location = Location(user=user, productID=productID, productName=productName, costPerUnits=costPerUnits, units=units)
            location.save()
            return 0

    def editLocation(locationID: str, city: str, state: str, address: str, zipCode: str) -> int:
        """
        This function is intended to be called by the view to edit a location in the Location table.

        Returns: 0 if there is no error; a positive integer if there is an error:
            1 -- if there is no location with locationID as its locationID
            2 -- if there is an issue with the city
            3 -- if there is an issue with the state
            4 -- if there is an issue with the address
            5 -- if there is an issue with the zipCode
        """
        location = Location.objects.get(productID=productID)
        if location == None:
            return 1
        elif len(city) > 30:
            return 2
        elif len(state) != 2:
            return 3
        elif len(address) > 50:
            return 4
        elif len(zipCode) > 10:
            return 5
        else:
            product.productName = productName
            product.costPerUnits = costPerUnits
            product.units = units
            product.save()
            return 0

    def deleteLocation(locationID: str) -> None:
        """
        This function is intended to be called by the view to delete a location in the Location table.

        Returns: None

        No input validation is made because no error will be produced if a non-existent location is attempted to be deleted.
        """
        try:
            location = Location.objects.get(productID=productID)
            location.delete()
        except:
            return None