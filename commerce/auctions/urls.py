from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('category/<str:category_name>/', views.category_listings, name='category_listings'),
    path('watchlist/', views.watchlist_view, name='watchlist'),
    path('listing/<int:listing_id>/place_bid/', views.place_bid, name='place_bid'),
    path('listing/<int:listing_id>/toggle_watchlist/', views.toggle_watchlist, name='toggle_watchlist'),
    path('listing/<int:listing_id>/close/', views.close_auction, name='close_auction'),
    path("listing/<int:listing_id>", views.listing_page, name="listing_page"),
    path("listing", views.create_listing, name="create_listing"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register")
]
