from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from .forms import AuctionForm, CommentForm, Bid
from django.contrib.auth.decorators import login_required
from .models import AuctionListing, User, Comment, Bid, Watchlist


def index(request):
    categories = AuctionListing.objects.values('category').distinct()
    listings = AuctionListing.objects.filter(is_active=True)

    for listing in listings:
        highest_bid = listing.bids.order_by('-amount').first()

        listing.current_price = highest_bid.amount if highest_bid else listing.starting_bid

    return render(request, "auctions/index.html", {
        "listings": listings,
        "categories": categories
    })


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required
def create_listing(request):
    if request.method == "POST":
        form = AuctionForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.creator = request.user  
            listing.save()
            return redirect('index')  
    else:
        form = AuctionForm()
    
    return render(request, "auctions/create_listing.html", {
        "form": form
    })

@login_required
def listing_page(request, listing_id):
    listing = get_object_or_404(AuctionListing, pk=listing_id)
    
    is_in_watchlist = Watchlist.objects.filter(user=request.user, auction=listing).exists()

    highest_bid = Bid.objects.filter(auction=listing).order_by('-amount').first()

    highest_bid_user = highest_bid.bidder if highest_bid else None

    comments = Comment.objects.filter(auction=listing)
    
    is_closed = not listing.is_active

    has_won = False
    if is_closed: 
        if highest_bid and highest_bid.bidder == request.user:
            has_won = True

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.auction = listing
            comment.save()
            return redirect('listing_page', listing_id=listing.id)
    else:
        form = CommentForm()

    return render(request, "auctions/listing_page.html", {
        "listing": listing,
        "comments": comments,
        "form": form,
        "highest_bid": highest_bid,
        "is_in_watchlist": is_in_watchlist,
        'highest_bid_user': highest_bid_user,
        'is_closed': is_closed,
        'has_won': has_won
    })

@login_required
def toggle_watchlist(request, listing_id):
    listing = get_object_or_404(AuctionListing, pk=listing_id)
    
    
    watchlist_item = Watchlist.objects.filter(user=request.user, auction=listing).first()  

    if watchlist_item:
        watchlist_item.delete()

    else:
        Watchlist.objects.create(user=request.user, auction=listing)  

    return redirect('listing_page', listing_id=listing.id)

@login_required
def place_bid(request, listing_id):
    listing = get_object_or_404(AuctionListing, pk=listing_id)

    if request.method == "POST":
        try:
            bid_amount = float(request.POST.get('bid_amount'))
        except (TypeError, ValueError):
            messages.error(request, "Invalid bid amount.")
            return redirect('listing_page', listing_id=listing.id)


        if bid_amount < listing.starting_bid:
            messages.error(request, "Your bid must be at least the starting bid.")
            return redirect('listing_page', listing_id=listing.id)

      
        current_bid = listing.bids.order_by('-amount').first()

        if current_bid and bid_amount <= current_bid.amount:
            messages.error(request, "Your bid must be higher than the current bid.")
            return redirect('listing_page', listing_id=listing.id)

       
        Bid.objects.create(amount=bid_amount, bidder=request.user, auction=listing)
        messages.success(request, "Your bid was placed successfully!")
        return redirect('listing_page', listing_id=listing.id)

 
    return redirect('listing_page', listing_id=listing.id)

@login_required
def close_auction(request, listing_id):
    listing = get_object_or_404(AuctionListing, pk=listing_id)

    if listing.creator != request.user:
        return redirect('listing_page', listing_id=listing.id)  

    
    highest_bid = listing.bids.order_by('-amount').first()
    if highest_bid:
        listing.winner = highest_bid.bidder  
    listing.is_active = False  
    listing.save()

    return redirect('listing_page', listing_id=listing.id)

@login_required
def watchlist_view(request):
    watchlist_items = Watchlist.objects.filter(user=request.user)
    listings = [item.auction for item in watchlist_items]
    
    return render(request, "auctions/watchlist.html", {
        "listings": listings
    })


def category_listings(request, category_name):
    listings = AuctionListing.objects.filter(category=category_name, is_active=True)

    return render(request, "auctions/category_listings.html", {
        "category_name": category_name,
        "listings": listings,
    })
