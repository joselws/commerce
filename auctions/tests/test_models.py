from django.test import TestCase
from auctions.models import Category, User, Item
from django.core.files import File



class ItemTestCase(TestCase):

    def setUp(self):

        # Create user
        testuser = User.objects.create_user(username="testuser", password="asdf")

        other = Category.objects.create(category="Other")

        valid_img_path = 'auctions/download.jpg'
        invalid_img_path = 'auctions/gas_prices.csv'

        # Items
        item_no_image = Item.objects.create(user=testuser, name="no_img", starting_price=22, category=other)
        item_no_name = Item.objects.create(user=testuser, name="", starting_price=10, category=other)

        item_valid_image = Item(user=testuser, name="valid_img", starting_price=50, category=other)
        item_valid_image.image.save('download.jpg', File(open(valid_img_path, 'rb')))

        item_invalid_image = Item(user=testuser, name="invalid_img", starting_price=23, category=other)
        item_invalid_image.image.save('gas_prices.csv', File(open(invalid_img_path, 'rb')))

    def tearDown(self):
        # Delete image files from project folder
        item_valid_image = Item.objects.get(name="valid_img")
        item_invalid_image = Item.objects.get(name="invalid_img")

        item_valid_image.image.delete()
        item_invalid_image.image.delete()


    def test_img_url(self):
        item_valid_image = Item.objects.get(name="valid_img")
        self.assertEqual(item_valid_image.image_url, '/media/download.jpg')

    def test_no_img_url(self):
        item_no_image = Item.objects.get(name="no_img")
        self.assertEqual(item_no_image.image_url, '')
