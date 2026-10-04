from django.http import HttpResponse
from django.shortcuts import render
from . models import Customer, Restaurant
from django.shortcuts import render, redirect
from .models import Restaurant, Item, Cart
import razorpay
from django.conf import settings

# Create your views here.
def index(request):
    return render(request, 'delivery/index.html')
    
def open_signup(request):
    return render(request, 'delivery/signup.html')
def open_signin(request):
    return render(request, 'delivery/signin.html')

def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        address = request.POST.get('address')
        
        try:
            Customer.objects.get(username = username)
            return HttpResponse("Duplicate username!")
        except:
            Customer.objects.create(
                username = username,
                password = password,
                email = email,
                mobile = mobile,
                address = address,
            )
            
    return render(request, 'delivery/signin.html')


def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            customer = Customer.objects.get(
                username=username,
                password=password
            )

            if username == 'admin':
                return render(request, 'delivery/admin_home.html')
            else:
                restaurantList = Restaurant.objects.all()
                return render(request, 'delivery/customer_home.html',{"restaurantList":restaurantList, "username": username})

        except Customer.DoesNotExist:
            return HttpResponse("Invalid username or password")

    return render(request, 'delivery/signin.html')

def open_add_restaurant(request):
    return render(request, 'delivery/add_restaurant.html')
def add_restaurant(request):

    if request.method == 'POST':

        print("========== ADD RESTAURANT ==========")
        print("POST DATA:", request.POST)

        name = request.POST.get('name', '').strip()

        picture = (
            request.POST.get('picture')
            or request.POST.get('picture_url')
            or ''
        ).strip()

        cuisine = request.POST.get('cuisine', '').strip()
        rating = request.POST.get('rating', '').strip()

        print("NAME:", name)
        print("PICTURE:", picture)
        print("CUISINE:", cuisine)
        print("RATING:", rating)

        # Check required fields
        if not name:
            return render(
                request,
                'delivery/add_restaurant.html',
                {'error': 'Restaurant name is required.'}
            )

        if not picture:
            return render(
                request,
                'delivery/add_restaurant.html',
                {'error': 'Picture URL is required.'}
            )

        if not cuisine:
            return render(
                request,
                'delivery/add_restaurant.html',
                {'error': 'Cuisine is required.'}
            )

        if not rating:
            return render(
                request,
                'delivery/add_restaurant.html',
                {'error': 'Rating is required.'}
            )

        # Create restaurant
        Restaurant.objects.create(
            name=name,
            picture=picture,
            cuisine=cuisine,
            rating=float(rating)
        )

        return redirect('/open_show_restaurant')

    return render(
        request,
        'delivery/add_restaurant.html'
    )
def open_show_restaurant(request):
    restaurant_list = Restaurant.objects.all()

    return render(
        request,
        'delivery/show_restaurants.html',
        {
            'restaurant_list': restaurant_list
        }
    )
def open_update_restaurant(request, id):
    restaurant = Restaurant.objects.get(id=id)

    if request.method == 'POST':
        restaurant.name = request.POST.get('name')
        restaurant.picture = request.POST.get('picture')
        restaurant.cuisine = request.POST.get('cuisine')
        restaurant.rating = request.POST.get('rating')

        restaurant.save()

        return redirect('open_show_restaurant')

    return render(
        request,
        'delivery/update_restaurant.html',
        {'restaurant': restaurant}
    )
def delete_restaurant(request, id):

    restaurant = Restaurant.objects.filter(id=id).first()

    if restaurant:
        restaurant.delete()

    return redirect('/open_show_restaurant')

def open_update_menu(request, restaurant_id):

    restaurant = Restaurant.objects.get(id=restaurant_id)

    items = Item.objects.filter(
        restaurant=restaurant
    )

    return render(
        request,
        'delivery/update_menu.html',
        {
            'restaurant': restaurant,
            'item_list': items,
            'restaurant_id': restaurant_id
        }
    )

def update_menu(request, restaurant_id):

    restaurant = Restaurant.objects.get(id=restaurant_id)

    if request.method == 'POST':

        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        picture = request.POST.get('picture')
        vegetarian = request.POST.get('vegetarian') == 'on'

        # Check required fields
        if name and price:

            Item.objects.create(
                restaurant=restaurant,
                name=name,
                description=description or '',
                price=float(price),
                vegetarian=vegetarian,
                picture=picture or ''
            )

        return redirect('open_update_menu', restaurant_id=restaurant_id)

    items = Item.objects.filter(restaurant=restaurant)

    return render(
        request,
        'delivery/update_menu.html',
        {
            'restaurant': restaurant,
            'item_list': items,
            'restaurant_id': restaurant_id
        }
    )


def view_menu(request, restaurant_id, username):
    restaurant = Restaurant.objects.get(id = restaurant_id)
    itemList = restaurant.items.all()
    #itemList = Item.objects.all()
    return render(request, 'delivery/customer_menu.html',
                  {"itemList": itemList,
                   "restaurant": restaurant,
                   "username":username})
def add_to_cart(request, item_id, username):

    item = Item.objects.get(id=item_id)

    customer = Customer.objects.get(username=username)

    cart, created = Cart.objects.get_or_create(
        customer=customer
    )

    cart.items.add(item)

    return render(
        request,
        'delivery/item_added.html',
        {
            'item': item,
            'username': username
        }
    )

def show_cart(request, username):

    customer = Customer.objects.get(
        username=username
    )

    cart = Cart.objects.filter(
        customer=customer
    ).first()

    items = cart.items.all() if cart else []

    total_price = cart.total_price() if cart else 0

    return render(
        request,
        'delivery/cart.html',
        {
            'itemList': items,
            'total_price': total_price,
            'username': username
        }
    )
def checkout(request, username):

    customer = Customer.objects.get(
        username=username
    )

    cart = Cart.objects.filter(
        customer=customer
    ).first()

    cart_items = cart.items.all() if cart else []

    total_price = cart.total_price() if cart else 0

    if total_price == 0:

        return render(
            request,
            'delivery/checkout.html',
            {
                'error': 'Your cart is empty!',
                'username': username
            }
        )

    client = razorpay.Client(
        auth=(
            settings.RAZORPAY_KEY_ID,
            settings.RAZORPAY_KEY_SECRET
        )
    )

    amount = int(float(total_price) * 100)

    order_data = {
        'amount': amount,
        'currency': 'INR',
        'receipt': f'mealmate_{customer.id}',
    }

    order = client.order.create(
        data=order_data
    )

    return render(
        request,
        'delivery/checkout.html',
        {
            'username': username,
            'cart_items': cart_items,
            'total_price': total_price,
            'razorpay_key_id': settings.RAZORPAY_KEY_ID,
            'order_id': order['id'],
            'amount': amount,
        }
    )