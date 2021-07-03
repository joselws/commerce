from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """Has default 'username' 'password' and 'email' attributes"""

    def __str__(self):
        return f"{self.username}"


class Category(models.Model):
	"""Models any category available for a particular item"""
	#All different categories can't be repeated i.e. unique
	category = models.CharField(max_length=20, unique=True)
	
	def __str__(self):
		return f"{self.category}"


class Listing(models.Model):
	"""Models an item in the auction"""
	name = models.CharField(max_length=64)
	
	#TextField simulates a textarea field, can be empty
	description = models.TextField(blank=True)

	#initial price set on an item
	price = models.DecimalField(max_digits=10, decimal_places=2)
	
	#Don't delete the listing if the category it belongs to does
	category = models.ForeignKey(Category, blank=True, on_delete=models.RESTRICT, default="Other")
	
	#if an user gets deleted, delete all Listings associated with him
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	
	#date the listing is created
	date = models.DateField(auto_now=True)
	
	#users can optionally add an image for their item, and they're sent to 'media/item_pics' folder
	image_url = models.URLField(blank=True, max_length=200)

	#Field that stores the name of users that have any listing as their watchlist
	watchlist = models.ManyToManyField(User, related_name="watchlist", blank=True)

	#Is the listing active? True by default
	active = models.BooleanField(default=True)
	
	def __str__(self):
		return f"Item {self.id}: {self.name} for ${self.price}. Posted by {self.user.username}"


class Bid(models.Model):
	"""The bid for every Listing in the auction"""
	bid = models.DecimalField(max_digits=10, decimal_places=2)
	
	#automatically added on creation
	bid_date = models.DateField(auto_now=True)
	
	#the specific item on which the bid is made
	item = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
	
	#person doing the bid
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	
	def __str__(self):
		return f"Bid {self.bid} on {self.item.name} by {self.user.username}"


class Comment(models.Model):
	"""Any comments inside a listing"""
	#User doing the comment
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	
	#the comment made by the user
	comment = models.TextField()
	
	#date is created and set automatically when the comment is made
	date = models.DateField(auto_now=True)
	
	#the specific item the comment pertains to
	item = models.ForeignKey(Listing, on_delete=models.CASCADE)
	
	def __str__(self):
		return f"Comment by {self.user.username} on {self.item.name} at {self.date}"

