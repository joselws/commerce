from django.test import TestCase, SimpleTestCase, Client
from django.db import IntegrityError
from .models import Category, User, Item, Bid, Comment
from django.db.models import Max
from django.core.files import File
from django.urls import reverse, resolve
from .views import index, login_view, logout_view, register, create, item, watch, bid, comment, watchlist, category, category_page, edit
from .utils import image_is_valid, name_is_valid, price_is_valid


########## UTILS.PY TESTS ##########

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



########## URLS TESTS ##########

class TestUrls(SimpleTestCase):

    def test_index_url_resolves(self):
        url = reverse('index')
        self.assertEqual(resolve(url).func, index)

    def test_login_url_resolves(self):
        url = reverse('login')
        self.assertEqual(resolve(url).func, login_view)

    def test_logout_url_resolves(self):
        url = reverse('logout')
        self.assertEqual(resolve(url).func, logout_view)

    def test_register_url_resolves(self):
        url = reverse('register')
        self.assertEqual(resolve(url).func, register)

    def test_create_url_resolves(self):
        url = reverse('create')
        self.assertEqual(resolve(url).func, create)

    def test_edit_url_resolves(self):
        url = reverse('edit', args=(5,))
        self.assertEqual(resolve(url).func, edit)

    def test_item_url_resolves(self):
        url = reverse('item', args=(4,))
        self.assertEqual(resolve(url).func, item)

    def test_watch_url_resolves(self):
        url = reverse('watch', args=(6,))
        self.assertEqual(resolve(url).func, watch)

    def test_bid_url_resolves(self):
        url = reverse('bid', args=(9,))
        self.assertEqual(resolve(url).func, bid)

    def test_comment_url_resolves(self):
        url = reverse('comment', args=(10,))
        self.assertEqual(resolve(url).func, comment)

    def test_watchlist_url_resolves(self):
        url = reverse('watchlist', args=(2,))
        self.assertEqual(resolve(url).func, watchlist)

    def test_category_url_resolves(self):
        url = reverse('category')
        self.assertEqual(resolve(url).func, category)

    def test_category_page_url_resolves(self):
        url = reverse('category_page', args=('some_category',))
        self.assertEqual(resolve(url).func, category_page)

    

########## MODEL TESTS ##########

##### Item model Tests #####

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



########## VIEW TESTS ##########

##### index view test #####

class IndexTestCase(TestCase):

    def setUp(self):
        # Create user
        testuser = User.objects.create_user(username="testuser", password="asdf")

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
        self.assertTemplateUsed(response, 'auctions/items.html')


##### Login view test #####

class LoginTestCase(TestCase):
    
    def setUp(self):

        # Create user
        User.objects.create_user(username="testuser1", password="testuser1")
        

    def test_get_login_view(self):
        client = Client()
        response = client.get(reverse('login'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request['PATH_INFO'], '/login')
        self.assertTemplateUsed(response, 'auctions/login.html')
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
        self.assertTemplateUsed(response, 'auctions/items.html')

    def test_login_invalid_user(self):
        client = Client()
        credentials = {'username': 'testuser1', 'password': 'bad_password'}
        response = client.post(reverse('login'), credentials, follow=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['message'], 'Invalid username and/or password.')
        self.assertEqual(response.request.get('PATH_INFO'), '/login')
        self.assertTemplateUsed(response, 'auctions/login.html')


##### Logout test view #####

class LogoutTestCase(TestCase):

    def setUp(self):

        User.objects.create_user(username="testuser1", password="testuser1")

    
    def test_authenticated_logout(self):
        client = Client()
        client.login(username='testuser1', password='testuser1')
        response = client.get(reverse('logout'), follow=True)
        redirect_url, redirect_status_code = response.redirect_chain[0]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(redirect_url, '/')
        self.assertEqual(redirect_status_code, 302)
        self.assertTemplateUsed(response, 'auctions/items.html')
    
    def test_non_authenticated_logout(self):
        client = Client()
        response = client.get(reverse('logout'), follow=True)
        redirect_url, redirect_status_code = response.redirect_chain[0]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(redirect_url, '/login')
        self.assertEqual(redirect_status_code, 302)
        self.assertTemplateUsed(response, 'auctions/login.html')


##### Register view #####

class RegisterTestCase(TestCase):

    def setUp(self):

        User.objects.create_user(username="testuser1", password="testuser1")


    def test_register_get(self):
        client = Client()
        response = client.get(reverse('register'), follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request['PATH_INFO'], '/register')
        self.assertTemplateUsed(response, 'auctions/register.html')
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
        self.assertTemplateUsed(response, 'auctions/register.html')
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
        self.assertTemplateUsed(response, 'auctions/items.html')

    def test_register_invalid_credentials(self):
        client = Client()
        credentials = {'username': 'testuser2', 'password': 'testuser2', 'confirmation': 'bad_password'}
        response = client.post(reverse('register'), credentials, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['message'], 'Passwords must match.')
        self.assertEqual(response.request['PATH_INFO'], '/register')
        self.assertTemplateUsed(response, 'auctions/register.html')

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
            self.assertTemplateUsed(response, 'auctions/register.html')

    def test_register_authenticated_user(self):
        client = Client()
        client.login(username="testuser1", password="testuser1")
        credentials = {'username': 'testuser2', 'password': 'testuser2', 'confirmation': 'testuser2'}
        response = client.post(reverse('register'), credentials, follow=True)
        redirect_url, redirect_status_code = response.redirect_chain[0]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(redirect_url, '/')
        self.assertEqual(redirect_status_code, 302)
        self.assertTemplateUsed(response, 'auctions/items.html')


##### Create view #####

class CreateTestCase(TestCase):

    def setUp(self):
        testuser = User.objects.create_user(username='testuser', password='testuser')
        other = Category.objects.create(category="Other")
        house = Category.objects.create(category="House")

    def tearDown(self):
        for item in Item.objects.all():
            item.image.delete()

    
    def test_nonauthenticate_create_get_request(self):
        client = Client()
        response = client.get(reverse('create'), follow=True)
        redirect_url, redirect_status_code = response.redirect_chain[0]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(redirect_url, '/login')
        self.assertEqual(redirect_status_code, 302)
        self.assertTemplateUsed(response, 'auctions/login.html')
        try:
            message = response.context['message']
        except KeyError:
            message = ''
        finally:
            self.assertEqual(message, '')

    def test_authenticated_create_get_request(self):
        categories = Category.objects.all()
        client = Client()
        client.login(username='testuser', password='testuser')
        response = client.get(reverse('create'), follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request['PATH_INFO'], '/create')
        self.assertEqual(response.context['categories'].count(), 2)
        self.assertTemplateUsed(response, 'auctions/create.html')
        try:
            message = response.context['message']
        except KeyError:
            message = ''
        finally:
            self.assertEqual(message, '')

    def test_authenticated_create_valid_post_all_data_request(self):
        house = Category.objects.get(category="House")
        testuser = User.objects.get(username="testuser")

        client = Client()
        client.login(username='testuser', password='testuser')

        data = {'name': 'Test Item',
            'description': 'Test description',
            'price': 50,
            'category': house,
            'user': testuser,
            'image': File(open('auctions/download.jpg', 'rb'))
            }

        response = client.post(reverse('create'), data, follow=True)
        item = Item.objects.first()
        redirect_url, redirect_status_code = response.redirect_chain[0]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['item'].id, item.id)
        self.assertEqual(redirect_url, f'/item/{item.id}')
        self.assertEqual(redirect_status_code, 302)
        self.assertEqual(Item.objects.all().count(), 1)
        self.assertEqual(item.name, 'Test Item')
        self.assertTemplateUsed(response, 'auctions/item.html')

    def test_nonauthenticated_create_valid_post_all_data_request(self):
        house = Category.objects.get(category="House")
        testuser = User.objects.get(username="testuser")

        client = Client()

        data = {'name': 'Test Item',
            'description': 'Test description',
            'price': 50,
            'category': house,
            'user': testuser,
            'image': File(open('auctions/download.jpg', 'rb'))
            }

        response = client.post(reverse('create'), data, follow=True)
        redirect_url, redirect_status_code = response.redirect_chain[0]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(redirect_url, '/login')
        self.assertEqual(redirect_status_code, 302)
        self.assertEqual(Item.objects.all().count(), 0)
        self.assertTemplateUsed(response, 'auctions/login.html')
        try:
            message = response.context['message']
        except KeyError:
            message = ''
        finally:
            self.assertEqual(message, '')

    def test_authenticated_create_valid_post_no_img(self):
        house = Category.objects.get(category="House")
        testuser = User.objects.get(username="testuser")

        client = Client()
        client.login(username='testuser', password='testuser')

        data = {'name': 'Test Item',
            'description': 'Test description',
            'price': 50,
            'category': house,
            'user': testuser,
            }

        response = client.post(reverse('create'), data, follow=True)
        item = Item.objects.first()
        redirect_url, redirect_status_code = response.redirect_chain[0]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['item'].id, item.id)
        self.assertEqual(redirect_url, f'/item/{item.id}')
        self.assertEqual(redirect_status_code, 302)
        self.assertEqual(Item.objects.all().count(), 1)
        self.assertEqual(item.name, 'Test Item')
        self.assertTemplateUsed(response, 'auctions/item.html')
        try:
            image_url = item.image.url
        except ValueError:
            image_url = item.image_url  #property method
        finally:
            self.assertEqual(image_url, '')

    def test_authenticated_create_valid_post_no_category(self):
        testuser = User.objects.get(username="testuser")

        client = Client()
        client.login(username='testuser', password='testuser')

        data = {'name': 'Test Item',
            'description': 'Test description',
            'price': 50,
            'user': testuser,
            'image': File(open('auctions/download.jpg', 'rb'))
            }

        response = client.post(reverse('create'), data, follow=True)
        item = Item.objects.first()
        redirect_url, redirect_status_code = response.redirect_chain[0]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['item'].id, item.id)
        self.assertEqual(redirect_url, f'/item/{item.id}')
        self.assertEqual(redirect_status_code, 302)
        self.assertEqual(Item.objects.all().count(), 1)
        self.assertEqual(item.name, 'Test Item')
        self.assertEqual(item.category.category, 'Other')
        self.assertTemplateUsed(response, 'auctions/item.html')

    def test_authenticated_create_invalid_post_name(self):
        testuser = User.objects.get(username="testuser")
        categories = Category.objects.all()

        client = Client()
        client.login(username='testuser', password='testuser')

        data = {'name': '',
            'description': 'Test description',
            'price': 50,
            'user': testuser,
            'image': File(open('auctions/download.jpg', 'rb'))
            }

        response = client.post(reverse('create'), data, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['message'], 'Name length must be larger than 1!')
        self.assertEqual(response.request['PATH_INFO'], '/create')
        self.assertEqual(Item.objects.all().count(), 0)
        self.assertQuerysetEqual(response.context['categories'], list(categories), ordered=False)
        self.assertTemplateUsed(response, 'auctions/create.html')

    def test_authenticated_create_invalid_post_price_negative(self):
        testuser = User.objects.get(username="testuser")
        categories = Category.objects.all()

        client = Client()
        client.login(username='testuser', password='testuser')

        data = {'name': 'Test Item',
            'description': 'Test description',
            'price': -30,
            'user': testuser,
            'image': File(open('auctions/download.jpg', 'rb'))
            }

        response = client.post(reverse('create'), data, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['message'], 'Price must be a positive number!')
        self.assertEqual(response.request['PATH_INFO'], '/create')
        self.assertEqual(Item.objects.all().count(), 0)
        self.assertQuerysetEqual(response.context['categories'], list(categories), ordered=False)
        self.assertTemplateUsed(response, 'auctions/create.html')

    def test_authenticated_create_invalid_post_price_zero(self):
        testuser = User.objects.get(username="testuser")
        categories = Category.objects.all()

        client = Client()
        client.login(username='testuser', password='testuser')

        data = {'name': 'Test Item',
            'description': 'Test description',
            'price': 0,
            'user': testuser,
            'image': File(open('auctions/download.jpg', 'rb'))
            }

        response = client.post(reverse('create'), data, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['message'], 'Price must be a positive number!')
        self.assertEqual(response.request['PATH_INFO'], '/create')
        self.assertEqual(Item.objects.all().count(), 0)
        self.assertQuerysetEqual(response.context['categories'], list(categories), ordered=False)
        self.assertTemplateUsed(response, 'auctions/create.html')

    def test_authenticated_create_invalid_post_price_string(self):
        testuser = User.objects.get(username="testuser")
        categories = Category.objects.all()

        client = Client()
        client.login(username='testuser', password='testuser')

        data = {'name': 'Test Item',
            'description': 'Test description',
            'price': 'bad price',
            'user': testuser,
            'image': File(open('auctions/download.jpg', 'rb'))
            }

        response = client.post(reverse('create'), data, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['message'], 'Price must be a positive number!')
        self.assertEqual(response.request['PATH_INFO'], '/create')
        self.assertEqual(Item.objects.all().count(), 0)
        self.assertQuerysetEqual(response.context['categories'], list(categories), ordered=False)
        self.assertTemplateUsed(response, 'auctions/create.html')

    def test_authenticated_create_invalid_post_invalid_image(self):
        testuser = User.objects.get(username="testuser")
        categories = Category.objects.all()

        client = Client()
        client.login(username='testuser', password='testuser')

        data = {'name': 'Test Item',
            'description': 'Test description',
            'price': 0,
            'user': testuser,
            'image': File(open('auctions/gas_prices.csv', 'rb'))
            }

        response = client.post(reverse('create'), data, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['message'], 'Not a valid image format!')
        self.assertEqual(response.request['PATH_INFO'], '/create')
        self.assertEqual(Item.objects.all().count(), 0)
        self.assertQuerysetEqual(response.context['categories'], list(categories), ordered=False)
        self.assertTemplateUsed(response, 'auctions/create.html')


##### item view #####

class ItemViewTestCase(TestCase):
    
    def setUp(self):
        testuser = User.objects.create_user(username='testuser', password='testuser')
        testuser2 = User.objects.create_user(username='testuser2', password='testuser2')
        other = Category.objects.create(category='Other')

        item_bids_comments = Item.objects.create(name='test item bids', starting_price=20, category=other, user=testuser)
        item_no_bids_comments = Item.objects.create(name='test item no bids', starting_price=20, category=other, user=testuser)

        Bid.objects.create(user=testuser2, item=item_bids_comments, bid=30)
        Bid.objects.create(user=testuser2, item=item_bids_comments, bid=40)
        Bid.objects.create(user=testuser2, item=item_bids_comments, bid=50)

        Comment.objects.create(user=testuser2, item=item_bids_comments, comment="Nice!")
        Comment.objects.create(user=testuser2, item=item_bids_comments, comment="Great!")
        Comment.objects.create(user=testuser2, item=item_bids_comments, comment="Awesome!")
        

    def test_item_exists_with_data_GET(self):
        client = Client()

        item_bids_comments = Item.objects.get(name='test item bids')
        bids = Bid.objects.filter(item=item_bids_comments).order_by('bid_date').reverse()
        comments = Comment.objects.filter(item=item_bids_comments).order_by('date').reverse()
        max_bid = bids.first()
        next_bid = max_bid.bid + 1
        
        response = client.get(reverse('item', args=(item_bids_comments.id,)), follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(item_bids_comments.active)
        self.assertEqual(response.context['item'], item_bids_comments)
        self.assertQuerysetEqual(response.context['bids'], list(bids))
        self.assertQuerysetEqual(response.context['comments'], list(comments))
        self.assertEqual(response.context['max_bid'], max_bid)
        self.assertEqual(response.context['next_bid'], next_bid)
        self.assertEqual(response.request['PATH_INFO'], f'/item/{item_bids_comments.id}')
        self.assertTemplateUsed(response, 'auctions/item.html')

    def test_item_exists_with_no_data_GET(self):
        client = Client()

        item_no_bids_comments = Item.objects.get(name='test item no bids')
        bids = Bid.objects.filter(item=item_no_bids_comments).order_by('bid_date').reverse()
        comments = Comment.objects.filter(item=item_no_bids_comments).order_by('date').reverse()
        max_bid = bids.first()
        next_bid = item_no_bids_comments.starting_price + 1
        
        response = client.get(reverse('item', args=(item_no_bids_comments.id,)), follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(item_no_bids_comments.active)
        self.assertEqual(response.request['PATH_INFO'], f'/item/{item_no_bids_comments.id}')
        self.assertEqual(response.context['item'], item_no_bids_comments)
        self.assertQuerysetEqual(response.context['comments'], list(comments))
        self.assertQuerysetEqual(response.context['bids'], list(bids))
        self.assertEqual(response.context['max_bid'], max_bid)
        self.assertEqual(response.context['next_bid'], next_bid)
        self.assertTemplateUsed(response, 'auctions/item.html')

    def test_item_doesnt_exists_GET(self):
        client = Client()
        response = client.get(reverse('item', args=(100,)), follow=True)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.request['PATH_INFO'], '/item/100')
        try:
            item = response.context['item']
            bids = response.context['bids']
            comments = response.context['comments']
            max_bid = response.context['max_bid']
            next_bid = response.context['next_bid']
        except KeyError:
            item = None
            bids = None
            comments = None
            max_bid = None
            next_bid = None
        finally:
            self.assertIsNone(item)
            self.assertIsNone(bids)
            self.assertIsNone(comments)
            self.assertIsNone(max_bid)
            self.assertIsNone(next_bid)

    def test_authenticated_item_exists_with_data_GET(self):
        client = Client()
        client.login(username='testuser', password='testuser')

        item_bids_comments = Item.objects.get(name='test item bids')
        bids = Bid.objects.filter(item=item_bids_comments).order_by('bid_date').reverse()
        comments = Comment.objects.filter(item=item_bids_comments).order_by('date').reverse()
        max_bid = bids.first()
        next_bid = max_bid.bid + 1
        
        response = client.get(reverse('item', args=(item_bids_comments.id,)), follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(item_bids_comments.active)
        self.assertEqual(response.context['item'], item_bids_comments)
        self.assertQuerysetEqual(response.context['bids'], list(bids))
        self.assertQuerysetEqual(response.context['comments'], list(comments))
        self.assertEqual(response.context['max_bid'], max_bid)
        self.assertEqual(response.context['next_bid'], next_bid)
        self.assertEqual(response.request['PATH_INFO'], f'/item/{item_bids_comments.id}')
        self.assertTemplateUsed(response, 'auctions/item.html')

    def test_authorized_item_POST(self):
        client = Client()
        client.login(username='testuser', password='testuser')

        item_bids_comments = Item.objects.get(name='test item bids')
        bids = Bid.objects.filter(item=item_bids_comments).order_by('bid_date').reverse()
        comments = Comment.objects.filter(item=item_bids_comments).order_by('date').reverse()
        max_bid = bids.first()
        next_bid = max_bid.bid + 1
        
        response = client.post(reverse('item', args=(item_bids_comments.id,)), follow=True)
        item_bids_comments.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['item'].active)
        self.assertEqual(response.context['item'], item_bids_comments)
        self.assertQuerysetEqual(response.context['bids'], list(bids))
        self.assertQuerysetEqual(response.context['comments'], list(comments))
        self.assertEqual(response.context['max_bid'], max_bid)
        self.assertEqual(response.context['next_bid'], next_bid)
        self.assertEqual(response.request['PATH_INFO'], f'/item/{item_bids_comments.id}')
        self.assertTemplateUsed(response, 'auctions/item.html')

    def test_unauthorized_item_POST(self):
        client = Client()
        client.login(username='testuser2', password='testuser2')

        item_bids_comments = Item.objects.get(name='test item bids')
        bids = Bid.objects.filter(item=item_bids_comments).order_by('bid_date').reverse()
        comments = Comment.objects.filter(item=item_bids_comments).order_by('date').reverse()
        max_bid = bids.first()
        next_bid = max_bid.bid + 1
        
        response = client.post(reverse('item', args=(item_bids_comments.id,)), follow=True)
        item_bids_comments.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(item_bids_comments.active)
        self.assertEqual(response.context['item'], item_bids_comments)
        self.assertQuerysetEqual(response.context['bids'], list(bids))
        self.assertQuerysetEqual(response.context['comments'], list(comments))
        self.assertEqual(response.context['max_bid'], max_bid)
        self.assertEqual(response.context['next_bid'], next_bid)
        self.assertEqual(response.request['PATH_INFO'], f'/item/{item_bids_comments.id}')
        self.assertTemplateUsed(response, 'auctions/item.html')

    def test_unauthenticated_item_POST(self):
        client = Client()
        item_bids_comments = Item.objects.get(name='test item bids')
        response = client.post(reverse('item', args=(item_bids_comments.id,)), follow=True)
        redirect_url, redirect_status_code = response.redirect_chain[0]
        
        item_bids_comments.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(redirect_url, '/login')
        self.assertEqual(redirect_status_code, 302)
        self.assertTrue(item_bids_comments.active)
        self.assertTemplateUsed(response, 'auctions/login.html')


##### Watch view #####

class WatchViewTestCase(TestCase):
    pass