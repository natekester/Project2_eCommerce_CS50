from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms

from .models import User, Auction, Bid, Watchlist, Comment

def get_highest_bid(auction_id):
    try: 
        bid = Bid.objects.filter(auction_id = auction_id).order_by('-bid')[0]
        highest_bid = bid.bid
        print(highest_bid)
    except:
        highest_bid = None
    return highest_bid
    