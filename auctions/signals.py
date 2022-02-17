from .models import Item, Bid, Comment
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
import os


@receiver(post_delete, sender=Item)
def delete_image_post_delete(sender, instance, *args, **kwargs):
    """ Deletes item image from images/ folder when the item instance is deleted """
    try:
        instance.image.delete(save=False)
    except:
        pass


@receiver(pre_save, sender=Item)
def delete_image_update(sender, instance, *args, **kwargs):
    """ Deletes old image from images/ folder if a new image was uploaded on item edit """
    try:
        old_image = instance.__class__.objects.get(id=instance.id).image.path
        try:
            new_image = instance.image.path

        # User didn't upload new image
        except:
            pass
        
        if old_image != new_image and new_image is not None:
            if os.path.exists(old_image):
                os.remove(old_image)

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