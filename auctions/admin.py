from django.contrib import admin
from .models import Item, Comment, Bid, Category

# Register your models here.
admin.site.register(Item)
admin.site.register(Comment)
admin.site.register(Bid)
admin.site.register(Category)