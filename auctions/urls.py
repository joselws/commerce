from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("item/<int:item>", views.item, name="item"),
    path("watch", views.watch, name="watch"),
    path("bid", views.bid, name="bid"),
    path("comment", views.comment, name="comment"),
    path("watchlist/<int:user_id>", views.watchlist, name="watchlist"),
    path("category", views.category, name="category"),
    path("category/<str:category_name>", views.category_page, name="category_page")
]
