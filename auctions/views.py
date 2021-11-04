from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse

from .models import User, Category, Item, Bid, Comment


def index(request):
    """Main page, it displays all active items available"""
    items = Item.objects.filter(active=True).order_by('id').reverse()
    return render(request, "auctions/index.html", {
        'items': items  #Show from the most recent to the oldest
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


@login_required()
def create(request):
    """Create a new item page"""
    #Make available for all render methods all categories as context
    categories = Category.objects.all()

    #In case the user submitted the form:
    if request.method == 'POST':
        name = request.POST['name']
        # We receive the user id from the form, get the user object from that
        user = User.objects.get(pk=request.POST['user'])
        #These fields below are optional and might have None as their value
        description = request.POST['description']
        image = request.POST['image']
        #Create a category instance for this field
        category = Category.objects.get(category=request.POST['category'])
        
        #The user might have input a non-number value
        try:
            starting_price = round(float(request.POST['price']), 2)

        #ValueError arises if we try to convert a non-valid string into a float
        #i.e: words to float
        except ValueError:
            message = "You entered a non valid number at price, please try again!"
            return render(request, "auctions/create.html", {
                'message': message,
                'categories': categories
            })

        #If all went well, create the item and redirect the user to the index page
        Item.objects.create(name=name, description=description, starting_price=starting_price, 
            image=image, category=category, user=user)
        return HttpResponseRedirect(reverse("index"))


    #In case we came from a direct link (GET), just render the page normally
    return render(request, "auctions/create.html", {
        'categories': categories
    })


def item(request, item_id):
    """ Individual page for each item """
    # Get the particular item we are rendering, along with its bids and comments
    item = Item.objects.get(pk=item_id)

    # If we are going to open or close the item
    if request.method == "POST":
        # Switch its value between True and False
        item.active = not item.active
        item.save()
        return HttpResponseRedirect(reverse('item', args=(item.id,)))

    # Get the bids in descending order by bid value
    # Django by default arranges it in ascending order, so we reverse it
    bids = Bid.objects.filter(item=item).order_by('bid').reverse()
    comments = Comment.objects.filter(item=item).order_by('id').reverse()
    
    # Get the max bid object of the item, 
    # which is the first one of the list as it was previously ordered by bid value
    if bids:
        max_bid = bids.first()  
        next_bid = max_bid.bid + 1      # Useful for defining html numeric input attributes
        
    # If no bids exist, then the next bid is the starting price of the item
    else:
        next_bid = float(item.price) + 1
        max_bid = None

    return render(request, 'auctions/item.html', {
            'item': item,
            'bids': bids,
            'comments': comments,
            'max_bid': max_bid,
            'next_bid': next_bid
        })


def watch(request):
    """ Handles the watchlist addition and deletion from users in a item """
    if request.method == "POST":
        # Get the item and the user
        item = Item.objects.get(pk=int(request.POST['item']))
        user = User.objects.get(pk=int(request.POST['user']))

        #Remove the user from this item watchlist if he/she is already in
        if user in item.watchlist.all():
            item.watchlist.remove(user)
        #Otherwise, add the user to the watchlist of this item
        else:
            item.watchlist.add(user)

    # Redirect the user back to the item page
    return HttpResponseRedirect(reverse('item', args=(item.id,))) 


def bid(request):
    """ Handles the bid POST logic for each item """
    # Get the item and the user from the form data to create the bid instance
    if request.method == "POST":
        item = Item.objects.get(pk=int(request.POST['item']))
        user = User.objects.get(pk=int(request.POST['user']))

        # Catch any potential input error, if so, redirects the user to the item page
        try:
            # Make sure to format the bid entered by the user to 2 decimals
            bid = round(float(request.POST['bid']), 2)

        except:
            return HttpResponseRedirect(reverse('item', args=(item.id,)))
        
        # If there are previously existing bids:
        # Check with the highest bids and the starting price
        bids = Item.bids.all().order_by('bid').reverse()
        # And its starting price
        if bids:
            if bid > bids[0].bid and bid > item.price:
                Bid.objects.create(bid=bid, item=item, user=user)

            return HttpResponseRedirect(reverse('item', args=(item.id,)))
        
        else:
            if bid > item.price:
                Bid.objects.create(bid=bid, item=item, user=user)

            return HttpResponseRedirect(reverse('item', args=(item.id,)))

    return HttpResponseRedirect(reverse('index'))
                

def comment(request):
    """ Handles the comment POST logic for a item """
    if request.method == "POST":
        item = Item.objects.get(pk=int(request.POST['item']))
        user = User.objects.get(pk=int(request.POST['user']))
        # Create comment if the user didn't submit an empty comment
        if request.POST['comment']:
            comment = request.POST['comment']
            Comment.objects.create(comment=comment, user=user, item=item)
            return HttpResponseRedirect(reverse('item', args=(item.id,)))
        
        else:
            return HttpResponseRedirect(reverse('item', args=(item.id,)))

    return HttpResponseRedirect(reverse('index'))


@login_required()
def watchlist(request, user_id):
    """ Handles the 'visit watchlist' page """
    user = User.objects.get(pk=user_id)
    # Get all the items on the user watchlist
    items = user.watchlist.all().order_by('id').reverse()
    return render(request, "auctions/watchlist.html", {
        'items': items
    })


def category(request):
    """ Displays a link list of all categories to the user """
    categories = Category.objects.all()
    return render(request, "auctions/categories.html", {
        'categories': categories
    })


def category_page(request, category_name):
    """ Displays all active items for a given category """
    # Get the category object from the name given in the URL
    category = Category.objects.get(category=category_name)
    # Get all active items from the given category from the most recent
    items = Item.objects.filter(category=category, active=True).order_by('id').reverse()
    return render(request, "auctions/category_page.html", {
        'items': items,
        'category_name': category_name
    })