from django.test import TestCase
from django.db.utils import IntegrityError
from .models import Category, User, Listing, Bid, Comment

# Create your tests here.


########## MODEL TESTS ##########

##### Category model Tests #####

class CategoryModelTests(TestCase):
    """Tests for the Category model"""
   
    def test_category_not_unique(self):
        """Django raises an integrity error whenever two categories are equal"""
        #Create two equal objects
        Category.objects.create(category="Test")
        message = ""
        try:
            Category.objects.create(category="Test")
            message += "No error found"

        except IntegrityError:
            message += "Integrity error found"
        #The message evaluates if the exception occurred
        self.assertEqual(message, "Integrity error found")


    def test_category_unique(self):
        """Two unique categories exist without problem"""
        #Create two unique objects
        Category.objects.create(category="Test1")
        message = ""
        try:
            Category.objects.create(category="Test2")
            message += "No error found"

        except IntegrityError:
            message += "Integrity error found"
        #The message evaluates if the exception did occur
        self.assertEqual(message, "No error found")
    	#Check if objects are created correctly
        self.assertEqual(Category.objects.all().count(), 2)

        
##### End Category Model Tests #####

### User model won't be test since it comes from Django, a reliable source

##### Listing Model Tests #####

