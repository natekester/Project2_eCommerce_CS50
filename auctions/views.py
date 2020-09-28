from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django import forms

from . import util

from .models import User, Auction, Bid, Watchlist, Comment

class CommentForm(forms.Form):
    comment = forms.CharField(max_length=100)
    


def index(request):
    return render(request, "auctions/index.html", {
        "Auction": Auction.objects.all()
    })


def item(request, id):

    highest_bid = util.get_highest_bid(id)
    print("highest_bid")
    print(highest_bid)
   

    auc = Auction.objects.get(pk = id)
    bids =  Bid.objects.filter(auction=Auction.objects.get(pk = id))
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
            # return redirect(request, "auctions/item.html", {
            #     "id" : id,
            #     "auc": auc,
            #     "bids": bids,
            #     "comments": Comment.objects.filter(auction=Auction.objects.get(pk = id)),
            #     "highest_bid" : highest_bid
            # })

         elif 'bid' in request.POST:
            print("we just recieved a bid")
             #we will need to make sure the bid is bigger than the current largest bid
             #if it is bigger - replace the current winning bid with the new bid - update the page with the new current largest bidder.
            return render(request, "auctions/item.html", {
            "auc": auc,
            "bids": bids,
            "comments": Comment.objects.filter(auction=Auction.objects.get(pk = id)),
            "highest_bid" : highest_bid
             })
    else:

        return render(request, "auctions/item.html", {
                "auc": auc,
                "bids": bids,
                "comments": Comment.objects.filter(auction=Auction.objects.get(pk = id)),
                "highest_bid" : highest_bid


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
