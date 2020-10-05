from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("item/<str:id>", views.item, name="item"),
    path("filter/<str:filter>", views.filter, name="filter"),
    path("closed/<str:id>", views.closed, name="closed"),
    path("create", views.create, name="create"),
    path("error/<str:id>", views.error, name="error"),
    path("winning/<str:id>", views.winning, name="winning"),
    path("watchlist/<str:id>", views.watchlist, name="watchlist")
]
