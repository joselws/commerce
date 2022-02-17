from django.test import SimpleTestCase
from django.core.files import File
from django.urls import reverse
from auctions.utils import image_is_valid, name_is_valid, price_is_valid


class TestUtils(SimpleTestCase):

    def test_image_is_valid(self):
        no_image = ''
        valid_image = File(open('auctions/download.jpg', 'rb'))
        invalid_image_format = File(open('auctions/gas_prices.csv', 'rb'))
        invalid_image_size = File(open('auctions/lionheart.png', 'rb'))

        self.assertTrue(image_is_valid(no_image))
        self.assertTrue(image_is_valid(valid_image.name))

        self.assertFalse(image_is_valid(invalid_image_format))
        self.assertFalse(image_is_valid(invalid_image_size))

    def test_name_is_valid(self):
        self.assertTrue(name_is_valid('Jose Wilhelm'))
        self.assertTrue(name_is_valid('joselws'))
        self.assertTrue(name_is_valid('J'))

        self.assertFalse(name_is_valid(''))

    def test_price_is_valid(self):
        self.assertTrue(price_is_valid(20))
        self.assertTrue(price_is_valid(1))
        self.assertTrue(price_is_valid(5.5))
        self.assertTrue(price_is_valid(0.2))

        self.assertFalse(price_is_valid(0))
        self.assertFalse(price_is_valid(-1))
        self.assertFalse(price_is_valid(''))
        self.assertFalse(price_is_valid('Jose'))
