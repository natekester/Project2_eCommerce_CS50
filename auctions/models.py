from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from datetime import datetime, timedelta

#we should add a listing class
#lets look at requirements first before making more tables
#needs 3 models in adition to User.
#auction listings,
#bids
# and comments on auction listings

class User(AbstractUser):
    pass

class Auction(models.Model):
    #setting up relative model variables for default
    end_date = datetime.today() + timedelta(4)

    #setting up models
    image = models.CharField(max_length = 1000, default = 'https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.dreamstime.com%2Fillustration%2Fno-image-available.html&psig=AOvVaw0BsrOjftE4apdhInuJiRA5&ust=1601135009139000&source=images&cd=vfe&ved=0CAIQjRxqFwoTCMji3u3ShOwCFQAAAAAdAAAAABAO')
    title = models.CharField(max_length= 120)  
    starting_bid = models.FloatField(validators=[MinValueValidator(0.01), MaxValueValidator(500000)])
    
    auction_start = models.DateTimeField(datetime.now)
    auction_end = models.DateTimeField(end_date)
    creating_user = models.ForeignKey(User, on_delete = models.PROTECT)
    desc = models.CharField(max_length=500)
    auction_status = models.CharField(max_length=32)#for now it should either be 'open' or 'closed'

class Bid(models.Model):
    auction = models.ForeignKey(Auction, on_delete = models.PROTECT)
    bid = models.FloatField(validators=[MinValueValidator(0.01), MaxValueValidator(100000)])
    biding_user = models.ForeignKey(User, on_delete = models.PROTECT)
    bid_input_time = models.DateTimeField(datetime.now)
    

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete = models.PROTECT)
    auction = models.ForeignKey(Auction, on_delete = models.CASCADE)
    comment = models.CharField(max_length=250)

class Watchlist(models.Model):
    auction = models.ForeignKey(Auction, on_delete = models.CASCADE)
    user = models.ForeignKey(User, on_delete = models.PROTECT)
    

