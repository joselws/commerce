from .models import Item, Bid, Comment
from django.db.models.signals import pre_save, post_save, post_delete, m2m_changed
from django.dispatch import receiver
from django.core.files import File
import os


@receiver(post_save, sender=Item)
def add_default_image(sender, instance, *args, **kwargs):
    """ Set the image property of Item to the default if no image was uploaded on creation """
    if not instance.image_url or not os.path.exists(instance.image.path):
        instance.image.save('empty.jpg', File(open('auctions/empty.jpg', 'rb')))


@receiver(post_delete, sender=Item)
def delete_image_post_delete(sender, instance, *args, **kwargs):
    """ Deletes item image from images/ folder when the item instance is deleted """
    try:
        instance.image.delete(save=False)
    except:
        pass


@receiver(pre_save, sender=Item)
def delete_image_update(sender, instance, *args, **kwargs):
    """ Deletes old image from images/ folder if a new image was uploaded on item edit, otherwise keep old image """
    try:
        old_object = instance.__class__.objects.get(id=instance.id)
        old_image = instance.__class__.objects.get(id=instance.id).image
        try:
            new_image = instance.image.path

        # User didn't upload new image
        except:
            instance.image = old_image
        
        if old_image.path != new_image and new_image is not None:
            if os.path.exists(old_image.path):
                os.remove(old_image.path)

    # Don't do anything if there was no old image
    except:
        pass


@receiver(post_save, sender=Bid)
def update_updated_at_item_on_bid(sender, instance, *args, **kwargs):
    """ Sets the updated_at attribute of item to the bid_date value of Bid """
    # print('signal fired')
    item = instance.item
    item.updated_at = instance.bid_date
    # print('setting updated_at from', item.updated_at, 'to', instance.bid_date)
    item.save()
    # print('updated_at set to', item.updated_at)


@receiver(post_save, sender=Comment)
def update_updated_at_item_on_comment(sender, instance, *args, **kwargs):
    """ Sets the updated_at attribute of item to the date value of Bid """
    #print('signal fired')
    item = instance.item
    item.updated_at = instance.date
    #print('setting updated_at from', item.updated_at, 'to', instance.date)
    item.save()
    #print('updated_at set to', item.updated_at)


@receiver(post_save, sender=Bid)
def increase_popularity_count_on_bid(sender, instance, *args, **kwargs):
    """ Call the increase_popularity item method everytime a bid is made """
    item = instance.item
    item.increase_popularity()


@receiver(post_save, sender=Comment)
def increase_popularity_count_on_comment(sender, instance, *args, **kwargs):
    """ Call the increase_popularity item method everytime a comment is made """
    item = instance.item
    item.increase_popularity()


@receiver(m2m_changed, sender=Item.watchlist.through)
def change_popularity_on_watchlist_add(sender, instance, action, *args, **kwargs):
    """ Call the increase_popularity or decrease_popularity item method 
    everytime the item is added in or removed from someone's watchlist """
    if action == 'post_add':
        instance.increase_popularity()

    elif action == 'post_remove':
        instance.decrease_popularity()