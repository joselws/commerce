from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.db.models import Max
from .utils import image_is_valid, name_is_valid, price_is_valid
from .models import User, Category, Item, Bid, Comment


def index(request):
    """Main page, it displays all recent-active items available"""
    items = Item.objects.filter(active=True).order_by('updated_at').reverse()
    page_title = "Recent Items"
    empty = "There are no active items in the auction!"
    return render(request, "auctions/items.html", {
        'items': items,  #Show from the most recent to the oldest
        'page_title': page_title,
        'empty': empty
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
    if request.user.is_authenticated:
        logout(request)
        return HttpResponseRedirect(reverse("index"))
    else:
        return HttpResponseRedirect(reverse('login'))


def register(request):
    if request.method == "POST":

        if not request.user.is_authenticated:
            username = request.POST["username"]

            # Ensure password matches confirmation
            password = request.POST["password"]
            confirmation = request.POST["confirmation"]

            if len(password) == 0:
                return render(request, "auctions/register.html", {
                    "message": 'Password must be at least 1 character long.'
                }) 

            if password != confirmation:
                return render(request, "auctions/register.html", {
                    "message": "Passwords must match."
                })

            # Attempt to create new user
            try:
                # empty email field necessary or authenticate() wont work
                user = User.objects.create_user(username, '', password)
                user.save()
            except IntegrityError:
                return render(request, "auctions/register.html", {
                    "message": "Username already taken."
                })
            except ValueError:
                return render(request, 'auctions/register.html', {
                    'message': 'Username must contain at least 1 letter.'
                })
            else:
                login(request, user)
                return HttpResponseRedirect(reverse("index"))

        # user is authenticated
        else:
            return HttpResponseRedirect(reverse('index'))

    # Get request
    else:
        return render(request, "auctions/register.html")


def create(request):
    """Create a new item page"""
    if request.user.is_authenticated:
        #Make available for all render methods all categories as context
        categories = Category.objects.all()

        #In case the user submitted the form:
        if request.method == 'POST':
            name = request.POST['name']
            if not name_is_valid(name):
                return render(request, "auctions/create.html", {
                    'message': 'Name length must be larger than 1!',
                    'categories': categories
                })

            # Get the user object from the current logged in user
            user = User.objects.get(pk=request.user.id)
            #These fields below are optional and might have None as their value
            description = request.POST['description']

            try:
                image = request.FILES['image']
            except KeyError:
                image = ''
            finally:
                if not image_is_valid(image):
                    return render(request, "auctions/create.html", {
                        'message': 'Not a valid image format!',
                        'categories': categories
                    })

            try:
                category = Category.objects.get(category=request.POST['category'])
            except KeyError:
                category = Category.objects.get(category='Other')

            #The user might have input a non-number value
            if not price_is_valid(request.POST['price']):
                return render(request, "auctions/create.html", {
                    'message': 'Price must be a positive number!',
                    'categories': categories
                })
            starting_price = round(float(request.POST['price']), 2) 

            #If all went well, create the item and redirect the user to the index page
            item = Item.objects.create(name=name, description=description, starting_price=starting_price, 
                category=category, user=user)
            return HttpResponseRedirect(reverse("item", args=(item.id,)))


        #In case we came from a direct link (GET), just render the page normally
        return render(request, "auctions/create.html", {
            'categories': categories
        })

    # user is not authenticated
    else:
        return HttpResponseRedirect(reverse('login'))


def item(request, item_id):
    """ Individual page for each item """
    # Get the particular item we are rendering, along with its bids and comments
    item = get_object_or_404(Item, pk=item_id)

    # If we are going to open or close the item
    if request.method == "POST":
        if request.user.is_authenticated:
            # only item creator can activate/deactivate item
            if request.user.id == item.user.id:
                # Switch its value between True and False
                item.active = not item.active
                item.save()
                return HttpResponseRedirect(reverse('item', args=(item.id,)))
        else:
            return HttpResponseRedirect(reverse('login'))

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
        next_bid = float(item.starting_price) + 1
        max_bid = None

    return render(request, 'auctions/item.html', {
            'item': item,
            'bids': bids,
            'comments': comments,
            'max_bid': max_bid,
            'next_bid': next_bid
        })


def watch(request, item_id):
    """ Handles the watchlist addition and deletion from users in a item """
    item = get_object_or_404(Item, pk=item_id)
    if request.method == "POST":

        # Redirect nonauthenticated users to login
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('login'))

        user = User.objects.get(pk=request.user.id)

        # Redirect the creator to its item view
        if user.id == item.user.id:
            return HttpResponseRedirect(reverse('item', args=(item.id,)))

        #Remove the user from this item watchlist if he/she is already in
        if user in item.watchlist.all():
            item.watchlist.remove(user)
        #Otherwise, add the user to the watchlist of this item
        else:
            item.watchlist.add(user)

    # Redirect the user back to the item page both on GET and POST
    return HttpResponseRedirect(reverse('item', args=(item.id,))) 


def bid(request, item_id):
    """ Handles the bid POST logic for each item """
    item = get_object_or_404(Item, pk=item_id)

    if request.method == "POST":

        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('login'))

        user = User.objects.get(pk=request.user.id)

        # Item creator cant bid and is redirected to the item
        if user.id == item.user.id:
            return HttpResponseRedirect(reverse('item', args=(item.id,)))

        # bids in not acceptable format are rejected
        if not price_is_valid(request.POST['bid']):
            return HttpResponseRedirect(reverse('item', args=(item.id,)))
        bid = round(float(request.POST['bid']), 2)

        # Get the maximum bid (or starting price if there is none)
        try:
            max_bid = float(Bid.objects.filter(item=item).aggregate(Max('bid'))['bid__max'])
        except TypeError:
            max_bid = item.starting_price

        # Valid bids are accepted
        if bid > max_bid:
            Bid.objects.create(bid=bid, item=item, user=user)
        else:
            return HttpResponseRedirect(reverse('item', args=(item.id,)))

    # GET requests or finish processing POST
    return HttpResponseRedirect(reverse('item', args=(item.id,)))
                

def comment(request, item_id):
    """ Handles the comment POST logic for a item """
    item = get_object_or_404(Item, pk=item_id)

    if request.method == "POST":
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('login'))

        user = User.objects.get(pk=request.user.id)

        # Create comment if the user didn't submit an empty comment
        if len(request.POST['comment']) > 1:
            comment = request.POST['comment']
            Comment.objects.create(comment=comment, user=user, item=item)
        
    return HttpResponseRedirect(reverse('item', args=(item.id,)))


def watchlist(request):
    """ Handles the 'visit watchlist' page """
    if request.user.is_authenticated:
        page_title = "Watchlist"
        empty = "There are no active items in your watchlist!"
        user = User.objects.get(pk=request.user.id)
        # Get all the items on the user watchlist
        items = user.watchlist.all().order_by('updated_at').reverse()
        return render(request, "auctions/items.html", {
            'items': items,
            'page_title': page_title,
            'empty': empty
        })

    # user is not authenticated
    else:
        return HttpResponseRedirect(reverse('login'))


def category(request):
    """ Displays a link list of all categories to the user """
    categories = Category.objects.all()
    return render(request, "auctions/categories.html", {
        'categories': categories
    })


def category_page(request, category_name):
    """ Displays all active items for a given category """
    # Get the category object from the name given in the URL
    category = get_object_or_404(Category, category=category_name)
    empty = "There are no active items for this category!"
    # Get all active items from the given category from the most recent
    items = Item.objects.filter(category=category, active=True).order_by('updated_at').reverse()
    return render(request, "auctions/items.html", {
        'items': items,
        'page_title': category_name,
        'empty': empty
    })


def edit(request, item_id):
    """ Display the create template with the item data in the form """
    #Make available for all render methods all categories as context
    item = get_object_or_404(Item, pk=item_id)
    
    if request.user.is_authenticated:
        categories = Category.objects.all()

        # item creator (authorized user)
        if request.user.id == item.user.id:

            #In case the user submitted the form:
            if request.method == 'POST':

                name = request.POST['name']
                if name_is_valid(name):
                    item.name = name
                else:
                    return render(request, 'auctions/edit.html', {
                        'message': 'Name length must be larger than 1!',
                        'categories': categories,
                        'item': item
                    })

                #These fields below are optional and might have None as their value
                item.description = request.POST['description']

                try:
                    image = request.FILES['image']
                except KeyError:
                    item.image = ''
                else:
                    if image_is_valid(image):
                        item.image = ''
                    else:
                        return render(request, 'auctions/edit.html', {
                            'message': 'Not a valid image format!',
                            'categories': categories,
                            'item': item
                        })
                
                try:
                    category = Category.objects.get(category=request.POST['category'])
                except KeyError:
                    category = Category.objects.get(category='Other')
                finally:
                    item.category = category
                
                #If all went well, create the item and redirect the user to the index page
                try:
                    item.save()
                except:
                    return HttpResponseRedirect(reverse('item', args=(item.id,)))

                return HttpResponseRedirect(reverse("item", args=(item.id,)))

            #In case we came from a direct link (GET), just render the page normally
            return render(request, "auctions/edit.html", {
                'categories': categories,
                'item': item,
                'message': 'Edit your item.'
            })
            
        # Unauthorized user
        else:
            return HttpResponseRedirect(reverse('item', args=(item.id,)))
    
    # user is not authenticated
    else:
        return HttpResponseRedirect(reverse('login'))


def delete(request, item_id):
    """ View that handles the deletion of items """
    item = get_object_or_404(Item, pk=item_id)

    if request.method == 'POST':

        if request.user.is_authenticated:

            if request.user.id == item.user.id:
                item.delete()
                return HttpResponseRedirect(reverse('index'))

            # The signed in user is not authorized
            else:
                return HttpResponseRedirect(reverse('item', args=(item.id,)))

        # User is not authenticated
        else:
            return HttpResponseRedirect(reverse('login'))

    # request method == GET
    else:
        return HttpResponseRedirect(reverse('item', args=(item.id,)))


def populars(request):
    """ Displays active items ordered by popularity in descending order """
    items = Item.objects.filter(active=True).order_by('popularity').reverse()
    page_title = 'Most popular'
    empty = 'There are no active items in the auction!'

    return render(request, 'auctions/items.html', {
        'items': items,
        'page_title': page_title,
        'empty': empty
    })


def my_items(request):
    """ Display all user's items """
    if request.user.is_authenticated:
        user = User.objects.get(id=request.user.id)
        items = Item.objects.filter(active=True, user=user).order_by('created_at').reverse()
        page_title = 'My items'
        empty = 'You have no items!'

        return render(request, 'auctions/items.html', {
            'items': items,
            'page_title': page_title,
            'empty': empty
        })

    # user is not authenticated
    else:
        return HttpResponseRedirect(reverse('login'))