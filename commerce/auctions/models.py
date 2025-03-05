from django.contrib.auth.models import AbstractUser, User
from django.db import models

class User(AbstractUser):
    pass

class AuctionListing(models.Model):
    title = models.CharField(max_length=90, verbose_name="Auction title")
    description = models.TextField(verbose_name="Auction description")
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Starting price")
    current_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="now price", null=True, blank=True)
    image_url = models.URLField(max_length=200, verbose_name="picture url", blank=True, null=True)
    category = models.CharField(max_length=50, verbose_name="category", blank=True, null=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings", verbose_name="auction creator")
    is_active = models.BooleanField(default=True, verbose_name="is auction active")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="creation time")

    def __str__(self):
        return self.title

class Bid(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="price")
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids", verbose_name="bidder")
    auction = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="bids", verbose_name="auction")
    bid_time = models.DateTimeField(auto_now_add=True, verbose_name="offer date")

    def __str__(self):
        return f"{self.amount} $ - {self.bidder.username}"

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments", verbose_name="author")
    auction = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="comments", verbose_name="auction")
    content = models.TextField(verbose_name="comment")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="comment date")

    def __str__(self):
        return f"Comment from: {self.user.username} - {self.created_at}"

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    auction = models.ForeignKey(AuctionListing, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'auction')

    def __str__(self):
        return f"{self.user.username} watches {self.auction.title}"