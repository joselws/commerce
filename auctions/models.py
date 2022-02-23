from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """Has default 'username' 'password' and 'email' attributes"""

    def __str__(self):
        return self.username


class Category(models.Model):
	"""Models any category available for a particular item"""
	#All different categories can't be repeated i.e. unique
	category = models.CharField(max_length=20, unique=True)
	
	def __str__(self):
		return self.category


class Item(models.Model):
	"""Models an item in the auction"""
	name = models.CharField(max_length=100)
	
	# TextField simulates a textarea field, can be empty
	description = models.TextField(blank=True)

	# initial price set on an item
	starting_price = models.DecimalField(max_digits=10, decimal_places=2)
	
	# Don't delete the item if the category it belongs to does
	category = models.ForeignKey(Category, blank=True, on_delete=models.RESTRICT)
	
	# if an user gets deleted, delete all items associated with him
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	
	# date the item is created
	created_at = models.DateTimeField(auto_now_add=True)

	# date the item was last updated
	updated_at = models.DateTimeField(auto_now=True)
	
	# users can optionally add an image for their item, and they're sent to 'static/auctions/images' folder
	image = models.ImageField(blank=True, max_length=200)

	# Field that stores the name of users that have any item as their watchlist
	watchlist = models.ManyToManyField(User, related_name="watchlist", blank=True)

	# Is the item active? True by default
	active = models.BooleanField(default=True)

	# increases everytime a comment or bid is made on the item, and when
	# it's added on someone's watchlist. Decreases when taken off of a watchlist
	popularity = models.PositiveSmallIntegerField(default=0)
	
	def __str__(self):
		return f"Item {self.id}: {self.name} for ${self.starting_price}. Posted by {self.user.username}"

	@property
	def image_url(self):
		""" Handles no input image """
		try:
			img = self.image.url
		except:
			img = ''
		return img

	def increase_popularity(self):
		""" Increases popularity count by one """
		self.popularity += 1
		self.save()

	def decrease_popularity(self):
		""" Decreases popularity count by one """
		self.popularity -= 1
		self.save()


class Bid(models.Model):
	"""The bid for every item in the auction"""
	bid = models.DecimalField(max_digits=10, decimal_places=2)
	
	#automatically added on creation
	bid_date = models.DateTimeField(auto_now=True)
	
	#the specific item on which the bid is made
	item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="bids")
	
	#person doing the bid
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	
	def __str__(self):
		return f"Bid {self.bid} on {self.item.name} by {self.user.username}"


class Comment(models.Model):
	"""Any comments inside a item"""
	#User doing the comment
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	
	#the comment made by the user
	comment = models.TextField()
	
	#date is created and set automatically when the comment is made
	date = models.DateTimeField(auto_now=True)
	
	#the specific item the comment pertains to
	item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="comments")
	
	def __str__(self):
		return f"Comment by {self.user.username} on {self.item.name} at {self.date}"

