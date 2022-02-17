from django.test import SimpleTestCase
from django.urls import reverse, resolve
from auctions.views import index, login_view, logout_view, register, create, item, watch, bid, comment, watchlist, category, category_page, edit


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
        url = reverse('watchlist')
        self.assertEqual(resolve(url).func, watchlist)

    def test_category_url_resolves(self):
        url = reverse('category')
        self.assertEqual(resolve(url).func, category)

    def test_category_page_url_resolves(self):
        url = reverse('category_page', args=('some_category',))
        self.assertEqual(resolve(url).func, category_page)
