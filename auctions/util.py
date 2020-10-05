from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
import datetime
import pytz



from datetime import datetime
from .models import User, Auction, Bid, Watchlist, Comment

def get_highest_bid(auction_id):
    try: 
        bid = Bid.objects.filter(auction_id = auction_id).order_by('-bid')[0]
        highest_bid = bid.bid
        print(highest_bid)
    except:
        highest_bid = None
    return highest_bid


def get_winner(auction_id):
    try: 
        winning_bid = Bid.objects.filter(auction_id = auction_id).order_by('-bid')[0]
        winner = winning_bid.biding_user.username
        print("the winner was: "+ winner)
    except:
        winner = Auction.objects(pk = auction_id).creating_user
    return winner

def get_if_open(id):


    auc = Auction.objects.get(pk= id)

    now = datetime.today()

    utc=pytz.UTC

    now = utc.localize(now) 
    end_date = auc.auction_end

    if end_date < now:

        auc.auction_status = 'Closed'
        print("changing auction status")
        auc.save() 
    

    if auc.auction_status == 'Open':
        
        return True
    else:
        
        return False
