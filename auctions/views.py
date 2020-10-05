from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django import forms
from datetime import datetime, timedelta
from . import util

from .models import User, Auction, Bid, Watchlist, Comment


def index(request):
    if request.method == "POST":
        filter = request.POST["category"]
        print(filter)
        return redirect(reverse('filter', kwargs={ 'filter': filter }))


    else:

        auctions = Auction.objects.filter(auction_status="Open")
        for auction in auctions:
            util.get_if_open(auction.id)
        
        return render(request, "auctions/index.html", {
            "Auction": Auction.objects.filter(auction_status="Open")

        })

def filter(request,filter):
    #render a page with list of active auctions that have the category of the filters
    if request.method == "POST":
        if request.POST["category"] == "all":
            return redirect(reverse('index'))
    elif filter == "all":
        return redirect(reverse('index'))
    else:
        return render(request, "auctions/index.html", {
            "Auction": Auction.objects.filter(auction_status = "Open", category = filter )
        }) 

def closed(request, id):
    #render a closed page that shows the winner and amount
    #the actual winner user should get a congrats page
    
    winning_user = util.get_winner(id)
    auc = Auction.objects.get(pk = id)
    bids =  Bid.objects.filter(auction=Auction.objects.get(pk = id))
    highest_bid = util.get_highest_bid(id)


    return render(request, "auctions/closed.html", {
        "auc": auc,
        "bids": bids,
        "comments": Comment.objects.filter(auction=Auction.objects.get(pk = id)),
        "winning_user" : winning_user,
        "highest_bid" : highest_bid

    })


def item(request, id):
    is_open = util.get_if_open(id)
    error = False
    
    if(is_open == False):

        return redirect(reverse('closed', kwargs={ 'id': id }))
    highest_bid = util.get_highest_bid(id)

    auc = Auction.objects.get(pk = id)
    bids =  Bid.objects.filter(auction=Auction.objects.get(pk = id))
    if request.user.is_authenticated:
        users_watchlist = Watchlist.objects.filter(auction = auc, user = request.user).count()
        print(f"is the auction setup for the user? {users_watchlist}")
        if users_watchlist >= 1:
            remove = True
        else:
            remove = False
    else:
        remove = False
    
    
    if highest_bid == None:
        acceptable_bid = auc.largest_bid+ 0.01
    else:
        acceptable_bid = highest_bid + 0.01

    if request.method == "POST":
         if 'Text' in request.POST:
            #and it's a comment
            current_user = request.POST["userId"]
            user = User.objects.get(username = current_user)
            comment = request.POST.get("Text")
            print("our comment is: "+ comment)
            comment_to_save = Comment(auction =auc, user = user, comment = comment )
            comment_to_save.save()
            return redirect(reverse('item', kwargs={ 'id': id }))


         elif 'bid' in request.POST:
            print("we just recieved a bid")
            bid = request.POST["bid"]
            if float(bid) >= acceptable_bid:
                current_user = request.POST["userId"]
                user = User.objects.get(username = current_user)
                b = Bid(auction = auc, bid = bid, biding_user = user, bid_input_time= datetime.now() )
                b.save()
                auc = Auction.objects.get(pk= id)
                auc.largest_bid = bid
                auc.save()
                #TODO add a page that says "thanks for making the bid on this item page"
                return redirect(reverse('winning', kwargs={ 'id': id }))

            else:
                #do nothing and redirect
                print("bid was not in the acceptable range")

             #we will need to make sure the bid is bigger than the current largest bid
             #if it is bigger - replace the current winning bid with the new bid - update the page with the new current largest bidder.
                return redirect(reverse('error', kwargs={ 'id': id }))
         elif 'watchlist' in request.POST:
            #if a user adds to watch list - add the user and auction item to the watchlist model
            current_user = request.POST["userId"]
            user = User.objects.get(username = current_user)
            if (Watchlist.objects.filter(auction = auc, user = user).count()) == 0:
                print(Watchlist.objects.filter(auction = auc, user = user).count())
                wl = Watchlist(auction = auc, user = user)
                wl.save()
            print("redirecting to watchlist")
            return redirect(reverse('watchlist', kwargs={ 'id': user.id }))

         elif 'remove_watchlist' in request.POST:
                        #if a user adds to watch list - add the user and auction item to the watchlist model
            current_user = request.POST["userId"]
            user = User.objects.get(username = current_user)
            
            auc = Auction.objects.get(pk=id)
            to_delete = Watchlist.objects.filter(auction = auc, user = user)
            to_delete.delete()
            
            return redirect(reverse('item', kwargs={ 'id': id }))

         elif 'close' in request.POST:
            #Make sure the usre is the one who created - and then change status and show winning bid and person
            auc = Auction.objects.get(pk = id)
            auc.auction_status = "closed"
            auc.save()

            return redirect(reverse('closed', kwargs={ 'id': id }))
         else:
            return redirect(reverse('item', kwargs={ 'id': id }))
    else:

        return render(request, "auctions/item.html", {
                "auc": auc,
                "bids": bids,
                "comments": Comment.objects.filter(auction=Auction.objects.get(pk = id)),
                "highest_bid" : highest_bid,
                "acceptable_bid" : acceptable_bid,
                "error": error,
                "remove": remove
            })




def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
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

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
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

def create(request):
    if request.method == "POST":
        image = request.POST["image"]
        title = request.POST["title"]
        starting_bid = request.POST["starting_bid"]
        category = request.POST["category"]
        current_user = request.user

        desc = request.POST["desc"]
        auction_status = "Open"
        auction_start = datetime.now()
        auction_end = auction_start + timedelta(days = 7)
        if image == "":
            image = 'data:image/png;base64,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'

        auc = Auction(image = image, title = title, largest_bid = starting_bid, category = category, auction_start = auction_start, auction_end = auction_end, creating_user = current_user, desc = desc, auction_status = auction_status)
        auc.save()


        return redirect(reverse('index'))


    else:
        return render(request, "auctions/create.html")

def error(request, id):
    auc = Auction.objects.get(pk=id)
    return render(request, "auctions/error.html", {
        "auc": auc
    })

def winning(request, id):
    auc = Auction.objects.get(pk=id)
    return render(request, "auctions/winning.html", {
        "auc": auc
    })

def watchlist(request, id):
    if request.method == "POST":
        
        #if a user adds to watch list - add the user and auction item to the watchlist model
        current_user = request.POST["userId"]
        user = User.objects.get(username = current_user)
        auc_id = int(request.POST["auctionID"])
        print(f"trying to assign auction with id {auc_id}")
       
        auc = Auction.objects.get(pk=auc_id)


        to_delete = Watchlist.objects.filter(auction = auc, user = user)
        to_delete.delete()
        
        return redirect(reverse('watchlist', kwargs={ 'id': user.id }))
        
    else:
        user = User.objects.get(pk=id)
       
        return render(request, "auctions/watchlist.html", {
            "Auction": Watchlist.objects.filter(user=user)
        })