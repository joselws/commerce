from django.test import TestCase, Client
from django.db import IntegrityError
from auctions.models import Category, User, Item, Bid, Comment
from django.db.models import Max
from django.core.files import File
from django.urls import reverse


##### Index view #####

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
        for item in Item.objects.all():
            item.image.delete()

    def test_index_view(self):
        client = Client()
        response = client.get(reverse('index'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['items'].count(), 3)
        self.assertEqual(response.request.get('PATH_INFO'), '/')
        self.assertEqual(response.context['page_title'], 'Recent Items')
        self.assertEqual(response.context['empty'], 'There are no active items in the auction!')
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
            self.assertIn('empty', image_url)

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
        
    def tearDown(self):
        for item in Item.objects.all():
            item.image.delete()

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
    
    def setUp(self):
        other = Category.objects.create(category='Other')
        testuser = User.objects.create_user(username='testuser', password='testuser')
        testuser1 = User.objects.create_user(username='testuser1', password='testuser1')
        item = Item.objects.create(name='item', starting_price=5, user=testuser, category=other)

    def tearDown(self):
        for item in Item.objects.all():
            item.image.delete()

    
    def test_nonauth_watch_GET(self):
        client = Client()
        item = Item.objects.get(name='item')
        response = client.get(reverse('watch', args=(item.id,)), follow=True)
        redirect_url, redirect_status_code = response.redirect_chain[0]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(redirect_url, f'/item/{item.id}')
        self.assertEqual(redirect_status_code, 302)
        self.assertQuerysetEqual(item.watchlist.all(), [])
        self.assertTemplateUsed(response, 'auctions/item.html')
    
    def test_auth_watch_GET(self):
        client = Client()
        client.login(username="testuser1", password="testuser1")
        item = Item.objects.get(name='item')
        response = client.get(reverse('watch', args=(item.id,)), follow=True)
        redirect_url, redirect_status_code = response.redirect_chain[0]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(redirect_url, f'/item/{item.id}')
        self.assertEqual(redirect_status_code, 302)
        self.assertQuerysetEqual(item.watchlist.all(), [])
        self.assertTemplateUsed(response, 'auctions/item.html')

    def test_auth_watch_item_doesnt_exists_GET(self):
        client = Client()
        client.login(username="testuser1", password="testuser1")
        response = client.get(reverse('watch', args=(100,)), follow=True)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.request['PATH_INFO'], '/watch/100')

    def test_nonauth_watch_POST(self):
        client = Client()
        item = Item.objects.get(name='item')
        response = client.post(reverse('watch', args=(item.id,)), follow=True)
        item.refresh_from_db()
        redirect_url, redirect_status_code = response.redirect_chain[0]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(redirect_url, '/login')
        self.assertEqual(redirect_status_code, 302)
        self.assertQuerysetEqual(item.watchlist.all(), [])
        self.assertTemplateUsed(response, 'auctions/login.html')

    def test_authenticated_authorized_watch_POST(self):
        client = Client()
        testuser1 = User.objects.get(username='testuser1')
        client.login(username="testuser1", password="testuser1")
        item = Item.objects.get(name='item')
        response = client.post(reverse('watch', args=(item.id,)), follow=True)
        redirect_url, redirect_status_code = response.redirect_chain[0]
        item.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(redirect_url, f'/item/{item.id}')
        self.assertEqual(redirect_status_code, 302)
        self.assertQuerysetEqual(item.watchlist.all(), list(User.objects.filter(username='testuser1')))
        self.assertQuerysetEqual(testuser1.watchlist.all(), list(Item.objects.filter(name='item')))
        self.assertTemplateUsed(response, 'auctions/item.html')

    def test_auth_watch_item_doesnt_exists_POST(self):
        client = Client()
        client.login(username="testuser1", password="testuser1")
        response = client.post(reverse('watch', args=(100,)), follow=True)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.request['PATH_INFO'], '/watch/100')

    def test_authenticated_nonauthorized_watch_POST(self):
        client = Client()
        testuser = User.objects.get(username='testuser')
        client.login(username="testuser", password="testuser")
        item = Item.objects.get(name='item')
        response = client.post(reverse('watch', args=(item.id,)), follow=True)
        redirect_url, redirect_status_code = response.redirect_chain[0]
        item.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(redirect_url, f'/item/{item.id}')
        self.assertEqual(redirect_status_code, 302)
        self.assertQuerysetEqual(item.watchlist.all(), [])
        self.assertTemplateUsed(response, 'auctions/item.html')


##### Bid view #####

class BidViewTestCase(TestCase):
    
    def setUp(self):
        testuser = User.objects.create_user(username='testuser', password='testuser')
        testuser2 = User.objects.create_user(username='testuser2', password='testuser2')
        other = Category.objects.create(category='Other')

        item_bids = Item.objects.create(name='test item bids', starting_price=20, category=other, user=testuser)
        item_no_bids = Item.objects.create(name='test item no bids', starting_price=20, category=other, user=testuser)

        Bid.objects.create(user=testuser2, item=item_bids, bid=30)
        Bid.objects.create(user=testuser2, item=item_bids, bid=40)
        Bid.objects.create(user=testuser2, item=item_bids, bid=50)

    def tearDown(self):
        for item in Item.objects.all():
            item.image.delete()

    def test_nonauth_item_exists_bid_GET(self):
        """ Redirects user to /item """
        client = Client()
        item_bids = Item.objects.get(name='test item bids')
        response = client.get(reverse('bid', args=(item_bids.id,)), follow=True)
        redirect_url, redirect_status_code = response.redirect_chain[0]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(redirect_url, f'/item/{item_bids.id}')
        self.assertEqual(redirect_status_code, 302)
        self.assertEqual(Bid.objects.filter(item=item_bids).count(), 3)
        self.assertTemplateUsed(response, 'auctions/item.html')

    def test_auth_item_exists_bid_GET(self):
        """ Redirects user to /item """
        client = Client()
        client.login(username="testuser2", password='testuser2')
        item_bids = Item.objects.get(name='test item bids')
        response = client.get(reverse('bid', args=(item_bids.id,)), follow=True)
        redirect_url, redirect_status_code = response.redirect_chain[0]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(redirect_url, f'/item/{item_bids.id}')
        self.assertEqual(redirect_status_code, 302)
        self.assertEqual(Bid.objects.filter(item=item_bids).count(), 3)
        self.assertTemplateUsed(response, 'auctions/item.html')

    def test_item_doesnt_exists_bid_GET(self):
        """ nonexistant items go 404 """
        client = Client()
        response = client.get(reverse('bid', args=(100,)), follow=True)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.request['PATH_INFO'], '/bid/100')

    def test_item_doesnt_exists_bid_POST(self):
        """ nonexistant items go 404 """
        client = Client()
        client.login(username='testuser2', password='testuser2')
        data = {'bid': 50}
        response = client.post(reverse('bid', args=(100,)), data, follow=True)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.request['PATH_INFO'], '/bid/100')

    def test_unauth_bid_POST(self):
        """ unauthenticated bids are rejected and redirected to /login """
        client = Client()
        item_bids = Item.objects.get(name="test item bids")
        data = {'bid': 60}
        response = client.post(reverse('bid', args=(item_bids.id,)), data, follow=True)
        redirect_url, redirect_status_code = response.redirect_chain[0]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(redirect_url, '/login')
        self.assertEqual(redirect_status_code, 302)
        self.assertEqual(Bid.objects.filter(item=item_bids).count(), 3)
        self.assertTemplateUsed(response, 'auctions/login.html')

    def test_unauth_bid_POST(self):
        """ user creator bids are rejected and redirected to /item """
        client = Client()
        client.login(username='testuser', password='testuser')
        item_bids = Item.objects.get(name="test item bids")
        data = {'bid': 60}
        response = client.post(reverse('bid', args=(item_bids.id,)), data, follow=True)
        redirect_url, redirect_status_code = response.redirect_chain[0]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(redirect_url, f'/item/{item_bids.id}')
        self.assertEqual(redirect_status_code, 302)
        self.assertEqual(Bid.objects.filter(item=item_bids).count(), 3)
        self.assertTemplateUsed(response, 'auctions/item.html')

    def test_authorized_valid_bid_POST(self):
        """ valid bids from other users are accepted and redirected to /item """
        client = Client()
        client.login(username='testuser2', password='testuser2')
        item_bids = Item.objects.get(name="test item bids")
        data = {'bid': 60}
        response = client.post(reverse('bid', args=(item_bids.id,)), data, follow=True)
        redirect_url, redirect_status_code = response.redirect_chain[0]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(redirect_url, f'/item/{item_bids.id}')
        self.assertEqual(redirect_status_code, 302)
        self.assertEqual(Bid.objects.filter(item=item_bids).count(), 4)
        self.assertTemplateUsed(response, 'auctions/item.html')

    def test_authorized_invalid_bid_POST(self):
        """ invalid bids (lesser than an existing bid) are rejected """
        client = Client()
        client.login(username='testuser2', password='testuser2')
        item_bids = Item.objects.get(name="test item bids")
        data = {'bid': 30}
        response = client.post(reverse('bid', args=(item_bids.id,)), data, follow=True)
        redirect_url, redirect_status_code = response.redirect_chain[0]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(redirect_url, f'/item/{item_bids.id}')
        self.assertEqual(redirect_status_code, 302)
        self.assertEqual(Bid.objects.filter(item=item_bids).count(), 3)
        self.assertTemplateUsed(response, 'auctions/item.html')

    def test_authorized_invalid_bid_empty_item_POST(self):
        """ invalid bids for empty items are rejected """
        client = Client()
        client.login(username='testuser2', password='testuser2')
        item_no_bids = Item.objects.get(name="test item no bids")
        data = {'bid': 15}
        response = client.post(reverse('bid', args=(item_no_bids.id,)), data, follow=True)
        redirect_url, redirect_status_code = response.redirect_chain[0]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(redirect_url, f'/item/{item_no_bids.id}')
        self.assertEqual(redirect_status_code, 302)
        self.assertEqual(Bid.objects.filter(item=item_no_bids).count(), 0)
        self.assertTemplateUsed(response, 'auctions/item.html')

    def test_authorized_valid_bid_empty_item_POST(self):
        """ valid bids on empty items are accepted """
        client = Client()
        client.login(username='testuser2', password='testuser2')
        item_no_bids = Item.objects.get(name="test item no bids")
        data = {'bid': 30}
        response = client.post(reverse('bid', args=(item_no_bids.id,)), data, follow=True)
        redirect_url, redirect_status_code = response.redirect_chain[0]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(redirect_url, f'/item/{item_no_bids.id}')
        self.assertEqual(redirect_status_code, 302)
        self.assertEqual(Bid.objects.filter(item=item_no_bids).count(), 1)
        self.assertTemplateUsed(response, 'auctions/item.html')

    
##### comment view #####

class CommentViewTestCase(TestCase):
    
    def setUp(self):
        testuser = User.objects.create_user(username='testuser', password='testuser')
        
        other = Category.objects.create(category='Other')

        item_comments = Item.objects.create(name='test item comments', starting_price=20, category=other, user=testuser)

        Comment.objects.create(user=testuser, item=item_comments, comment="comment 1")
        Comment.objects.create(user=testuser, item=item_comments, comment="comment 2")
        Comment.objects.create(user=testuser, item=item_comments, comment="comment 3")

    def tearDown(self):
        for item in Item.objects.all():
            item.image.delete()


    def test_item_doesnt_exists_bid_GET(self):
        """ nonexistant items go 404 """
        client = Client()
        response = client.get(reverse('comment', args=(100,)), follow=True)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.request['PATH_INFO'], '/comment/100')

    def test_item_doesnt_exists_bid_POST(self):
        """ nonexistant items go 404 """
        client = Client()
        client.login(username='testuser', password='testuser')
        data = {'comment': 'comment 4'}
        response = client.post(reverse('comment', args=(100,)), data, follow=True)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.request['PATH_INFO'], '/comment/100')

    def test_comment_GET(self):
        """ GET requests on this view are redirected to its respective item """
        client = Client()
        item_comments = Item.objects.get(name='test item comments')
        response = client.get(reverse('comment', args=(item_comments.id,)), follow=True)
        redirect_url, redirect_status_code = response.redirect_chain[0]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(redirect_url, f'/item/{item_comments.id}')
        self.assertEqual(redirect_status_code, 302)
        self.assertEqual(Comment.objects.filter(item=item_comments).count(), 3)
        self.assertTemplateUsed(response, 'auctions/item.html')

    def test_nonauthenticated_comment_POST(self):
        """ nonauthenticated users are redirected to login """
        client = Client()
        item_comments = Item.objects.get(name='test item comments')
        data = {'comment': 'comment 4'}
        response = client.post(reverse('comment', args=(item_comments.id,)), data, follow=True)
        redirect_url, redirect_status_code = response.redirect_chain[0]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(redirect_url, '/login')
        self.assertEqual(redirect_status_code, 302)
        self.assertEqual(Comment.objects.filter(item=item_comments).count(), 3)
        self.assertTemplateUsed(response, 'auctions/login.html')

    def test_authenticated_valid_comment_POST(self):
        """ authenticated users can post valid comments """
        client = Client()
        client.login(username='testuser', password='testuser')
        item_comments = Item.objects.get(name='test item comments')
        data = {'comment': 'comment 4'}
        response = client.post(reverse('comment', args=(item_comments.id,)), data, follow=True)
        redirect_url, redirect_status_code = response.redirect_chain[0]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(redirect_url, f'/item/{item_comments.id}')
        self.assertEqual(redirect_status_code, 302)
        self.assertEqual(Comment.objects.filter(item=item_comments).count(), 4)
        self.assertTemplateUsed(response, 'auctions/item.html')

    def test_authenticated_invalid_comment_POST(self):
        """ invalid comments are rejected """
        client = Client()
        client.login(username='testuser', password='testuser')
        item_comments = Item.objects.get(name='test item comments')
        data = {'comment': 'c'}
        response = client.post(reverse('comment', args=(item_comments.id,)), data, follow=True)
        redirect_url, redirect_status_code = response.redirect_chain[0]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(redirect_url, f'/item/{item_comments.id}')
        self.assertEqual(redirect_status_code, 302)
        self.assertEqual(Comment.objects.filter(item=item_comments).count(), 3)
        self.assertTemplateUsed(response, 'auctions/item.html')

    
##### watchlist view #####

class WatchlistTestCase(TestCase):

    def setUp(self):
        testuser = User.objects.create_user(username='testuser', password='testuser')
        testuser2 = User.objects.create_user(username='testuser2', password='testuser2')

        other = Category.objects.create(category='Other')

        item1 = Item.objects.create(name='item1', user=testuser, starting_price=5, category=other)
        item2 = Item.objects.create(name='item2', user=testuser, starting_price=5, category=other)
        item3 = Item.objects.create(name='item3', user=testuser, starting_price=5, category=other)

    def tearDown(self):
        for item in Item.objects.all():
            item.image.delete()

    
    def test_unauthenticated_GET(self):
        """ Unauthenticated users are redirected to /login """
        client = Client()
        response = client.get(reverse('watchlist'), follow=True)
        redirect_url, redirect_status_code = response.redirect_chain[0]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(redirect_url, '/login')
        self.assertEqual(redirect_status_code, 302)
        self.assertTemplateUsed(response, 'auctions/login.html')

    def test_unauthenticated_POST(self):
        """ unautheniticated users are also redirected to /login on post """
        client = Client()
        response = client.post(reverse('watchlist'), follow=True)
        redirect_url, redirect_status_code = response.redirect_chain[0]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(redirect_url, '/login')
        self.assertEqual(redirect_status_code, 302)
        self.assertTemplateUsed(response, 'auctions/login.html')

    def test_authenticated_watchlist_items(self):
        """ authenticated users with watchlist data have them rendered """
        client = Client()
        client.login(username='testuser2', password='testuser2')
        testuser2 = User.objects.get(username='testuser2')
        response = client.get(reverse('watchlist'), follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request['PATH_INFO'], '/watchlist')
        self.assertEqual(response.context['page_title'], 'Watchlist')
        self.assertEqual(response.context['empty'], 'There are no active items in your watchlist!')
        self.assertQuerysetEqual(response.context['items'], list(testuser2.watchlist.all().order_by('updated_at').reverse()))
        self.assertTemplateUsed(response, 'auctions/items.html')

    def test_authenticated_watchlist_empty(self):
        """ users with empty watchlist also renders the watchlist page """
        client = Client()
        client.login(username='testuser', password='testuser')
        testuser = User.objects.get(username='testuser')
        response = client.get(reverse('watchlist'), follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request['PATH_INFO'], '/watchlist')
        self.assertEqual(response.context['page_title'], 'Watchlist')
        self.assertEqual(response.context['empty'], 'There are no active items in your watchlist!')
        self.assertQuerysetEqual(response.context['items'], list(testuser.watchlist.all()))
        self.assertTemplateUsed(response, 'auctions/items.html')


##### Category view #####

class CategoryViewTestCase(TestCase):

    def setUp(self):
        testuser = User.objects.create_user(username='testuser', password='testuser')

        Category.objects.create(category='Other')
        Category.objects.create(category='House')
        Category.objects.create(category='Electronics')
        Category.objects.create(category='Books')
        Category.objects.create(category='Games')

    def test_categories_GET(self):
        """ Render template normally on GET """
        client = Client()
        categories = Category.objects.all()
        response = client.get(reverse('category'), follow=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request['PATH_INFO'], '/category')
        self.assertQuerysetEqual(response.context['categories'], list(categories), ordered=False)
        self.assertTemplateUsed(response, 'auctions/categories.html')

    def test_categories_POST(self):
        """ Render template normally on POST as well """
        client = Client()
        categories = Category.objects.all()
        response = client.post(reverse('category'), follow=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request['PATH_INFO'], '/category')
        self.assertQuerysetEqual(response.context['categories'], list(categories), ordered=False)
        self.assertTemplateUsed(response, 'auctions/categories.html')

    def test_authenticated_categories_GET(self):
        """ Render template normally if the user is logged in """
        client = Client()
        client.login(username='testuser', password='testuser')
        categories = Category.objects.all()
        response = client.get(reverse('category'), follow=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request['PATH_INFO'], '/category')
        self.assertQuerysetEqual(response.context['categories'], list(categories), ordered=False)
        self.assertTemplateUsed(response, 'auctions/categories.html')


##### category page view #####

class CategoryPageViewTestCase(TestCase):

    def setUp(self):
        testuser = User.objects.create_user(username='testuser', password='testuser')

        other = Category.objects.create(category="Other")
        house = Category.objects.create(category="House")
        books = Category.objects.create(category="Books")

        item_other_1 = Item.objects.create(name='item other 1', starting_price=30, category=other, user=testuser)
        item_other_2 = Item.objects.create(name='item other 2', starting_price=30, category=other, user=testuser)
        item_other_3 = Item.objects.create(name='item other 3', starting_price=30, category=other, user=testuser)
        
        item_house = Item.objects.create(name='item house', starting_price=30, category=house, user=testuser)

    def tearDown(self):
        for item in Item.objects.all():
            item.image.delete()

    
    def test_render_other_category_items_GET(self):
        """ GET requests render the items normally """
        category_name = 'Other'
        other = Category.objects.get(category=category_name)
        items = Item.objects.filter(category=other).order_by('updated_at').reverse()
        client = Client()
        response = client.get(reverse('category_page', args=(category_name,)), follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request['PATH_INFO'], f'/category/{category_name}')
        self.assertQuerysetEqual(response.context['items'], list(items))
        self.assertEqual(response.context['items'].count(), 3)
        self.assertEqual(response.context['page_title'], category_name)
        self.assertEqual(response.context['empty'], 'There are no active items for this category!')
        self.assertTemplateUsed(response, 'auctions/items.html')

    def test_render_other_category_items_POST(self):
        """ POST requests render the items normally """
        category_name = 'Other'
        other = Category.objects.get(category=category_name)
        items = Item.objects.filter(category=other).order_by('updated_at').reverse()
        client = Client()
        response = client.post(reverse('category_page', args=(category_name,)), follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request['PATH_INFO'], f'/category/{category_name}')
        self.assertQuerysetEqual(response.context['items'], list(items))
        self.assertEqual(response.context['items'].count(), 3)
        self.assertEqual(response.context['page_title'], category_name)
        self.assertEqual(response.context['empty'], 'There are no active items for this category!')
        self.assertTemplateUsed(response, 'auctions/items.html')

    def test_render_auth_user_category_items_GET(self):
        """ Auth users are rendered the items normally """
        category_name = 'Other'
        other = Category.objects.get(category=category_name)
        items = Item.objects.filter(category=other).order_by('updated_at').reverse()
        client = Client()
        client.login(username='testuser', password='testuser')
        response = client.get(reverse('category_page', args=(category_name,)), follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request['PATH_INFO'], f'/category/{category_name}')
        self.assertQuerysetEqual(response.context['items'], list(items))
        self.assertEqual(response.context['items'].count(), 3)
        self.assertEqual(response.context['page_title'], category_name)
        self.assertEqual(response.context['empty'], 'There are no active items for this category!')
        self.assertTemplateUsed(response, 'auctions/items.html')

    def test_category_name_doesnt_exist(self):
        """ Category names that doesn't exist go 404 """
        category_name = 'Pets'
        client = Client()
        response = client.get(reverse('category_page', args=(category_name,)), follow=True)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.request['PATH_INFO'], f'/category/{category_name}')

    def test_category_house_single_item(self):
        """ Page works normally on single items """
        category_name = 'House'
        house = Category.objects.get(category=category_name)
        items = Item.objects.filter(category=house).order_by('updated_at').reverse()
        client = Client()
        response = client.get(reverse('category_page', args=(category_name,)), follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request['PATH_INFO'], f'/category/{category_name}')
        self.assertQuerysetEqual(response.context['items'], list(items))
        self.assertEqual(response.context['items'].count(), 1)
        self.assertEqual(response.context['page_title'], category_name)
        self.assertEqual(response.context['empty'], 'There are no active items for this category!')
        self.assertTemplateUsed(response, 'auctions/items.html')

    def test_category_books_no_item(self):
        """ Page also works normally on empty category items """
        category_name = 'Books'
        books = Category.objects.get(category=category_name)
        items = Item.objects.filter(category=books).order_by('updated_at').reverse()
        client = Client()
        response = client.get(reverse('category_page', args=(category_name,)), follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request['PATH_INFO'], f'/category/{category_name}')
        self.assertQuerysetEqual(response.context['items'], list(items))
        self.assertEqual(response.context['items'].count(), 0)
        self.assertEqual(response.context['page_title'], category_name)
        self.assertEqual(response.context['empty'], 'There are no active items for this category!')
        self.assertTemplateUsed(response, 'auctions/items.html')

    
##### Edit view #####

class EditViewTestCase(TestCase):
    
    def setUp(self):
        other = Category.objects.create(category='Other')
        testuser = User.objects.create_user(username='testuser', password='testuser')
        testuser2 = User.objects.create_user(username='testuser2', password='testuser2')

        item = Item.objects.create(name='item', starting_price=20, user=testuser, category=other)

    def tearDown(self):
        for item in Item.objects.all():
            item.image.delete()

    
    def test_edit_item_doesnt_exist(self):
        """ go 404 if the item doesn't exist """
        client = Client()
        response = client.get(reverse('edit', args=(100,)))

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.request['PATH_INFO'], '/edit/100')

    def test_nonauthenticated_users_redirected(self):
        """ nonauthenticated users are redirected to /login """
        client = Client()
        item = Item.objects.get(name="item")
        response = client.get(reverse('edit', args=(item.id,)), follow=True)
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

    def test_non_authorized_users_redirected(self):
        """ only the user creator can edit the item, others are redirected to the item page """
        client = Client()
        client.login(username='testuser2', password='testuser2')
        item = Item.objects.get(name="item")
        response = client.get(reverse('edit', args=(item.id,)), follow=True)
        redirect_url, redirect_status_code = response.redirect_chain[0]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(redirect_url, f'/item/{item.id}')
        self.assertEqual(redirect_status_code, 302)
        self.assertTemplateUsed(response, 'auctions/item.html')
        try:
            message = response.context['message']
        except KeyError:
            message = ''
        finally:
            self.assertEqual(message, '')

    def test_authorized_user_GET(self):
        """ user creator can see this page normally """
        client = Client()
        client.login(username='testuser', password='testuser')
        item = Item.objects.get(name="item")
        response = client.get(reverse('edit', args=(item.id,)), follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request['PATH_INFO'], f'/edit/{item.id}')
        self.assertEqual(response.context['item'], item)
        self.assertEqual(response.context['message'], 'Edit your item.')
        self.assertQuerysetEqual(response.context['categories'], list(Category.objects.all()))
        self.assertTemplateUsed(response, 'auctions/edit.html')

    def test_valid_authorized_edit_POST(self):
        """ The item was updated successfully """
        client = Client()
        client.login(username='testuser', password='testuser')
        item = Item.objects.get(name="item")
        data = {'name': 'item edited', 'description': ''}
        response = client.post(reverse('edit', args=(item.id,)), data, follow=True)
        redirect_url, redirect_status_code = response.redirect_chain[0]
        item.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(redirect_url, f'/item/{item.id}')
        self.assertEqual(redirect_status_code, 302)
        self.assertEqual(response.context['item'], item)
        self.assertEqual(response.context['item'].name, 'item edited')
        self.assertTemplateUsed(response, 'auctions/item.html')

    def test_invalid_authorized_edit_name(self):
        """ Invalid name edits are rejected """
        client = Client()
        client.login(username='testuser', password='testuser')
        item = Item.objects.get(name="item")
        data = {'name': '', 'description': ''}
        response = client.post(reverse('edit', args=(item.id,)), data, follow=True)
        item.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request['PATH_INFO'], f'/edit/{item.id}')
        self.assertEqual(response.context['item'], item)
        self.assertEqual(response.context['item'].name, 'item')
        self.assertEqual(response.context['message'], 'Name length must be larger than 1!')
        self.assertQuerysetEqual(response.context['categories'], list(Category.objects.all()))
        self.assertTemplateUsed(response, 'auctions/edit.html')

    def test_invalid_authorized_edit_image_format(self):
        """ dont accept files that arent jpg or png """
        client = Client()
        client.login(username='testuser', password='testuser')
        item = Item.objects.get(name="item")
        image = File(open('auctions/gas_prices.csv', 'rb'))
        data = {'image': image, 'description': '', 'name': item.name}
        response = client.post(reverse('edit', args=(item.id,)), data, follow=True)
        item.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request['PATH_INFO'], f'/edit/{item.id}')
        self.assertEqual(response.context['item'], item)
        self.assertIn('empty', response.context['item'].image_url)
        self.assertEqual(response.context['message'], 'Not a valid image format!')
        self.assertQuerysetEqual(response.context['categories'], list(Category.objects.all()))
        self.assertTemplateUsed(response, 'auctions/edit.html')

    
class DeleteViewTestCase(TestCase):

    def setUp(self):
        other = Category.objects.create(category='Other')
        testuser = User.objects.create_user(username='testuser', password='testuser')
        testuser2 = User.objects.create_user(username='testuser2', password='testuser2')
        

        item1 = Item.objects.create(name='item1', user=testuser, category=other, starting_price=5)
        item2 = Item.objects.create(name='item2', user=testuser, category=other, starting_price=5)

    def tearDown(self):
        for item in Item.objects.all():
            item.image.delete()

    
    def test_delete_item_doesnt_exist(self):
        """ go 404 if the item doesn't exist """
        client = Client()
        response = client.get(reverse('delete', args=(100,)), follow=True)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.request['PATH_INFO'], '/delete/100')

    def test_delete_item_GET(self):
        """ Users are redirected to /item on GET """
        client = Client()
        item1 = Item.objects.get(name='item1')
        response = client.get(reverse('delete', args=(item1.id,)), follow=True)
        redirect_url, redirect_status_code = response.redirect_chain[0]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(redirect_url, f'/item/{item1.id}')
        self.assertEqual(redirect_status_code, 302)
        self.assertEqual(Item.objects.all().count(), 2)
        self.assertTemplateUsed(response, 'auctions/item.html')

    def test_delete_item_unauthorized_POST(self):
        """ Authenticated users that are not the creator are redirected to /item """
        client = Client()
        client.login(username='testuser2', password='testuser2')
        item1 = Item.objects.get(name='item1')
        response = client.post(reverse('delete', args=(item1.id,)), follow=True)
        redirect_url, redirect_status_code = response.redirect_chain[0]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(redirect_url, f'/item/{item1.id}')
        self.assertEqual(redirect_status_code, 302)
        self.assertEqual(Item.objects.all().count(), 2)
        self.assertTemplateUsed(response, 'auctions/item.html')

    def test_delete_item_unauthenticated_POST(self):
        """ Non authenticated users are redirected to /login on POST """
        client = Client()
        item1 = Item.objects.get(name='item1')
        response = client.post(reverse('delete', args=(item1.id,)), follow=True)
        redirect_url, redirect_status_code = response.redirect_chain[0]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(redirect_url, '/login')
        self.assertEqual(redirect_status_code, 302)
        self.assertEqual(Item.objects.all().count(), 2)
        self.assertTemplateUsed(response, 'auctions/login.html')

    def test_delete_item_authorized_POST(self):
        """ Authenticated users that are not the creator are redirected to /item """
        client = Client()
        client.login(username='testuser', password='testuser')
        item1 = Item.objects.get(name='item1')
        response = client.post(reverse('delete', args=(item1.id,)), follow=True)
        redirect_url, redirect_status_code = response.redirect_chain[0]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(redirect_url, '/')
        self.assertEqual(redirect_status_code, 302)
        self.assertEqual(Item.objects.all().count(), 1)
        self.assertTemplateUsed(response, 'auctions/items.html')


##### Most popular view #####

class PopularsTestCase(TestCase):

    def setUp(self):
        other = Category.objects.create(category='Other')
        testuser = User.objects.create_user(username='testuser', password='testuser')
        item1 = Item.objects.create(name='item1', starting_price=23, user=testuser, category=other)
        item2 = Item.objects.create(name='item2', starting_price=23, user=testuser, category=other)

        # Item 1 is more popular than item2
        item1.increase_popularity()
        item1.increase_popularity()

        item2.increase_popularity()

    def tearDown(self):
        for item in Item.objects.all():
            item.image.delete()

    
    def test_most_popular_GET(self):
        """ Most popular items are rendered first """
        page_title = 'Most popular'
        empty = 'There are no active items in the auction!'
        client = Client()
        response = client.get(reverse('populars'), follow=True)
        items = Item.objects.all().order_by('popularity').reverse()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request['PATH_INFO'], '/populars')
        self.assertEqual(response.context['page_title'], page_title)
        self.assertEqual(response.context['empty'], empty)
        self.assertQuerysetEqual(response.context['items'], list(items))
        self.assertTemplateUsed(response, 'auctions/items.html')

    def test_most_popular_POST(self):
        """ POST requests don't affect the logic """
        page_title = 'Most popular'
        empty = 'There are no active items in the auction!'
        client = Client()
        response = client.post(reverse('populars'), follow=True)
        items = Item.objects.all().order_by('popularity').reverse()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request['PATH_INFO'], '/populars')
        self.assertEqual(response.context['page_title'], page_title)
        self.assertEqual(response.context['empty'], empty)
        self.assertQuerysetEqual(response.context['items'], list(items))
        self.assertTemplateUsed(response, 'auctions/items.html')


##### My items view #####

class MyItemsTestCase(TestCase):

    def setUp(self):
        other = Category.objects.create(category='Other')
        testuser = User.objects.create_user(username='testuser', password='testuser')
        testuser2 = User.objects.create_user(username='testuser2', password='testuser2')
        item1 = Item.objects.create(name='item1', starting_price=23, user=testuser, category=other)
        item2 = Item.objects.create(name='item2', starting_price=23, user=testuser, category=other)

    def tearDown(self):
        for item in Item.objects.all():
            item.image.delete()

    
    def test_auth_my_items_GET(self):
        """ GET requests on auth users have their items rendered correctly """
        testuser = User.objects.get(username='testuser')
        items = Item.objects.filter(user=testuser)
        page_title = 'My items'
        empty = 'You have no items!'
        client = Client()
        client.login(username='testuser', password='testuser')
        response = client.get(reverse('my_items'), follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request['PATH_INFO'], '/my_items')
        self.assertEqual(response.context['page_title'], page_title)
        self.assertEqual(response.context['empty'], empty)
        self.assertEqual(response.context['items'].count(), 2)
        self.assertQuerysetEqual(response.context['items'], list(items), ordered=False)
        self.assertTemplateUsed(response, 'auctions/items.html')

    def test_auth_my_items_POST(self):
        """ POST requests don't affect the logic of the view """
        testuser = User.objects.get(username='testuser')
        items = Item.objects.filter(user=testuser)
        page_title = 'My items'
        empty = 'You have no items!'
        client = Client()
        client.login(username='testuser', password='testuser')
        response = client.post(reverse('my_items'), follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request['PATH_INFO'], '/my_items')
        self.assertEqual(response.context['page_title'], page_title)
        self.assertEqual(response.context['empty'], empty)
        self.assertEqual(response.context['items'].count(), 2)
        self.assertQuerysetEqual(response.context['items'], list(items), ordered=False)
        self.assertTemplateUsed(response, 'auctions/items.html')

    def test_unauthenticated_my_items_GET(self):
        """ Non authenticated users are redirected to /login """
        client = Client()
        response = client.get(reverse('my_items'), follow=True)
        redirect_url, redirect_status_code = response.redirect_chain[0]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(redirect_url, '/login')
        self.assertEqual(redirect_status_code, 302)
        self.assertTemplateUsed(response, 'auctions/login.html')
        try:
            page_title = response.context['page_title']
            empty = response.context['empty']
            items = response.context['items']
        except:
            page_title = ''
            empty = ''
            items = []
        finally:
            self.assertEqual(page_title, '')
            self.assertEqual(empty, '')
            self.assertEqual(len(items), 0)

    def test_auth_my_items_empty_GET(self):
        """ Users with empty items have their page rendered correctly """
        testuser2 = User.objects.get(username='testuser2')
        items = Item.objects.filter(user=testuser2)
        page_title = 'My items'
        empty = 'You have no items!'
        client = Client()
        client.login(username='testuser2', password='testuser2')
        response = client.get(reverse('my_items'), follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request['PATH_INFO'], '/my_items')
        self.assertEqual(response.context['page_title'], page_title)
        self.assertEqual(response.context['empty'], empty)
        self.assertEqual(response.context['items'].count(), 0)
        self.assertQuerysetEqual(response.context['items'], list(items), ordered=False)
        self.assertTemplateUsed(response, 'auctions/items.html')