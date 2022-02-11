from django.test import TestCase, Client
from django.db import IntegrityError
from .models import Category, User, Item, Bid, Comment
from django.db.models import Max
from django.core.files import File
from django.urls import reverse


########## MODEL TESTS ##########

##### Item model Tests #####

class ItemTestCase(TestCase):

    @classmethod
    def setUpClass(cls):

        # Create user
        testuser = User.objects.create_user(username="testuser", password="asdf")
        testuser.save()

        other = Category.objects.create(category="Other")

        valid_img_path = 'auctions/download.jpg'
        invalid_img_path = 'auctions/gas_prices.csv'

        # Items
        item_no_image = Item.objects.create(user=testuser, name="no_img", starting_price=22, category=other)

        item_valid_image = Item(user=testuser, name="valid_img", starting_price=50, category=other)
        item_valid_image.image.save('download.jpg', File(open(valid_img_path, 'rb')))

        item_invalid_image = Item(user=testuser, name="invalid_img", starting_price=23, category=other)
        item_invalid_image.image.save('gas_prices.csv', File(open(invalid_img_path, 'rb')))

    @classmethod
    def tearDownClass(cls):
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

    def test_valid_image(self):
        item_valid_image = Item.objects.get(name="valid_img")
        item_no_image = Item.objects.get(name="no_img")

        self.assertTrue(item_valid_image.valid_img())
        self.assertTrue(item_no_image.valid_img())

    def test_invalid_image(self):
        item_invalid_image = Item.objects.get(name="invalid_img")
        self.assertFalse(item_invalid_image.valid_img())



########## VIEW TESTS ##########

##### index view test #####

class IndexTestCase(TestCase):

    def setUp(self):
        # Create user
        testuser = User.objects.create_user(username="testuser", password="asdf")
        testuser.save()

        other = Category.objects.create(category="Other")

        valid_img_path = 'auctions/download.jpg'
        invalid_img_path = 'auctions/gas_prices.csv'

        # Items
        item_no_image = Item.objects.create(user=testuser, name="no_img", starting_price=22, category=other)

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

    def test_index_view(self):
        client = Client()
        response = client.get(reverse('index'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['items'].count(), 3)
        self.assertEqual(response.request.get('PATH_INFO'), '/')


##### Login view test #####

class LoginTestCase(TestCase):
    
    def setUp(self):

        # Create user
        testuser1 = User.objects.create_user(username="testuser1", password="testuser1")
        testuser1.save()
        

    def test_get_login_view(self):
        client = Client()
        response = client.get(reverse('login'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request['PATH_INFO'], '/login')
        try:
            message = response.context['message']
        except KeyError:
            message = ''
        finally:
            self.assertEqual(message, '')


    def test_login_valid_user(self):
        client = Client()
        credentials = {'username': 'testuser1', 'password': 'testuser1'}
        response = client.post(reverse('login'), credentials, follow=True)
        
        redirect_url, redirect_status_code = response.redirect_chain[0]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(redirect_url, '/')
        self.assertEqual(redirect_status_code, 302)

    def test_login_invalid_user(self):
        client = Client()
        credentials = {'username': 'testuser1', 'password': 'bad_password'}
        response = client.post(reverse('login'), credentials, follow=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['message'], 'Invalid username and/or password.')
        self.assertEqual(response.request.get('PATH_INFO'), '/login')


##### Logout test view #####

class LogoutTestCase(TestCase):

    def setUp(self):

        testuser1 = User.objects.create_user(username="testuser1", password="testuser1")
        testuser1.save()

    
    def test_authenticated_logout(self):
        client = Client()
        client.login(username='testuser1', password='testuser1')
        response = client.get(reverse('logout'), follow=True)
        redirect_url, redirect_status_code = response.redirect_chain[0]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(redirect_url, '/')
        self.assertEqual(redirect_status_code, 302)
    
    def test_non_authenticated_logout(self):
        client = Client()
        response = client.get(reverse('logout'), follow=True)
        redirect_url, redirect_status_code = response.redirect_chain[0]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(redirect_url, '/login')
        self.assertEqual(redirect_status_code, 302)


class RegisterTestCase(TestCase):

    def setUp(self):

        testuser1 = User.objects.create_user(username="testuser1", password="testuser1")
        testuser1.save()


    def test_register_get(self):
        client = Client()
        response = client.get(reverse('register'), follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request['PATH_INFO'], '/register')
        try:
            message = response.context['message']
        except:
            message = ''
        finally:
            self.assertEqual(message, '')


    def test_authenticated_register_get(self):
        client = Client()
        client.login(username='testuser1', password='testuser1')
        response = client.get(reverse('register'), follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request['PATH_INFO'], '/register')
        try:
            message = response.context['message']
        except:
            message = ''
        finally:
            self.assertEqual(message, '')


    def test_nonauthenticated_valid_register_post(self):
        client = Client()
        credentials = {'username': 'testuser2', 'password': 'testuser2', 'confirmation': 'testuser2'}
        response = client.post(reverse('register'), credentials, follow=True)
        redirect_url, redirect_status_code = response.redirect_chain[0]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(redirect_url, '/')
        self.assertEqual(redirect_status_code, 302)

    def test_register_invalid_credentials(self):
        client = Client()
        credentials = {'username': 'testuser2', 'password': 'testuser2', 'confirmation': 'bad_password'}
        response = client.post(reverse('register'), credentials, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['message'], 'Passwords must match.')
        self.assertEqual(response.request['PATH_INFO'], '/register')

    def test_register_existent_user(self):
        client = Client()
        credentials = {'username': 'testuser1', 'password': 'testuser1', 'confirmation': 'testuser1'}
        
        try:
            response = client.post(reverse('register'), credentials, follow=True)
        except IntegrityError:
            pass
        finally:
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context['message'], 'Username already taken.')
            self.assertEqual(response.request['PATH_INFO'], '/register')

    def test_register_authenticated_user(self):
        client = Client()
        client.login(username="testuser1", password="testuser1")
        credentials = {'username': 'testuser2', 'password': 'testuser2', 'confirmation': 'testuser2'}
        response = client.post(reverse('register'), credentials, follow=True)
        redirect_url, redirect_status_code = response.redirect_chain[0]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(redirect_url, '/')
        self.assertEqual(redirect_status_code, 302)


