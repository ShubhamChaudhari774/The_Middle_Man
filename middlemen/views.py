from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Profile, Product, RestaurantRequest, Message, SavedProducer, Producer, Customer
from .forms import (SignUpForm, LoginForm, ProfileEditForm,
                    ProductForm, RestaurantRequestForm, BrowseFilterForm)


def profileView(request):
    return render(request, "profile.html")

def messagesView(request):
    if request.user.is_authenticated:
        messages = Message.objects.filter(MessageTo=request.user)
        return render(request, "messages.html", {'messages': messages})
    else:
        return redirect(home)
    
def viewMessage(request, msgID):
    if request.user.is_authenticated:
        message = Message.objects.get(id=msgID)
        message.IsNewMessage = False
        message.save()
        return render(request, "viewMessage.html", {'message': message})
    else:
        return redirect(home)

def sendMessageView(request):
    if request.user.is_authenticated:
        return render(request, 'sendMessage.html')
    else:
        return redirect(home)

def sendMessageAction(request):
    if request.user.is_authenticated:
        MessageTo = request.POST['To']
        MessageFrom = request.user.username
        MessageBody = request.POST['message']
        IsNewMessage = True
        message = Message(MessageTo=MessageTo, MessageFrom=MessageFrom, MessageBody=MessageBody, IsNewMessage=IsNewMessage)
        message.save()
        return redirect(messagesView)
    else:
        return redirect(home)

def deleteMessage(request, msgID):
    if request.user.is_authenticated:
        message = Message.objects.get(id=msgID)
        if message.MessageTo == request.user.username:
            message.delete()
            return redirect(messagesView)
        else:
            return redirect(home)
    else:
        return redirect(home)

def searchView(request):
    return render(request, "search.html")


# ─── HOME ─────────────────────────────────────────────────────────────────────
def home(request):
    featured_products = Product.objects.filter(available=True).order_by('-id')[:4]
    why_list = [
        ('💸', 'Fair Pricing',     'No distributor markup. Producers earn more, restaurants pay less.'),
        ('📍', 'Local First',      'Source from farms near you. Fresh ingredients, reduced transport.'),
        ('🔒', 'Verified Sellers', 'Every producer profile is rated and reviewed by real buyers.'),
        ('💬', 'Direct Messaging', 'Negotiate deals and build relationships right inside the platform.'),
    ]
    context = {
        'featured_products': featured_products,
        'producer_count': Profile.objects.filter(role='producer').count() or 500,
        'buyer_count':    Profile.objects.filter(role='buyer').count() or 1200,
        'why_list': why_list,
    }
    return render(request, 'home.html', context)


# ─── ABOUT ────────────────────────────────────────────────────────────────────
def about(request):
    team = [
        {'name': 'Aditi Rai',        'role': 'Team Leader & Developer',  'initials': 'AR', 'bio': 'Coordinates the team, sets goals, and ensures deadlines are met.'},
        {'name': 'Caeden Webb',       'role': 'Scribe & Developer',        'initials': 'CW', 'bio': 'Documents decisions and wrote the project abstract.'},
        {'name': 'Joseph Wysocki',    'role': 'QA & Developer',            'initials': 'JW', 'bio': 'Ensures the app is bug-free through end-to-end testing.'},
        {'name': 'Shubham Chaudhari', 'role': 'Architect & Developer',     'initials': 'SC', 'bio': 'Designs the system architecture and leads UI implementation.'},
    ]
    impact = [
        ('🌾', '500+',  'Producers Onboarded'),
        ('🍽️', '1,200+', 'Restaurants Connected'),
        ('💰', '$2M+', 'Saved in Fees'),
        ('📍', '47',   'States Covered'),
    ]
    return render(request, 'about.html', {'team': team, 'impact': impact})


def loginView(request):
    """
    This view will render the login page if the user is not authenticated, it will return the user to the home page if the user is already logged in
    """
    if request.user.is_authenticated == True:
        return redirect(home)
    else:
        return render(request, 'login.html')

def signupView(request):
    """
    This view will render the signup page if the user is not authenticated, it will return the user to the home page if the user is already logged in
    """
    if request.user.is_authenticated == True:
        return redirect(home)
    else:
        return render(request, 'signup.html')

def loginUser(request):
    """
    This view will login a user based on the form submitted by loginView
    """
    if request.user.is_authenticated == True:
        return redirect(home)
    else:
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user != None:
                login(request, user)
            else:
                return redirect(loginView)

            if request.user.id not in Profile.objects.values_list("user_id", flat=True):
                if request.user.username in Customer.objects.values_list("username", flat=True):
                    user_role = "Buyer"
                elif request.user.username in Producer.objects.values_list("username", flat=True):
                    user_role = "Producer"
                else:
                    user_role = "Unknown"
                profile = Profile(user_id=request.user.id, role=user_role)
                profile.save()

            return redirect(home)
        else:
            return redirect(loginView)

def logoutUser(request):
    logout(request)
    return redirect(loginView)

def signupUser(request):
    """
    This view will sign up a user based upon the form submitted by the signup view
    """
    if request.user.is_authenticated == True:
        return redirect(home)
    else:
        # Validate that the user does not already exist
        try:
            user = User.objects.get(username=request.POST['username'])
        except:
            user = None

        # Validate to make sure that the password entries match
        if (request.POST['password'] != request.POST['reenteredPassword']):
            return redirect(signupView)

        # Add the user to customer/producer tables
        if request.POST['userType'] == 'producer':
            result = Producer.createProducer(username=request.POST['username'])
            if (result != 0):
                return redirect(signupView)
        else:
            result = Customer.createCustomer(username=request.POST['username'])
            if (result != 0):
                return redirect(signupView)

        # Create the user in the user table
        User.objects.create_user(username=request.POST['username'], password=request.POST['password'], email=request.POST['email'], first_name=request.POST['firstName'], last_name=request.POST['lastName'])

        # Redirect to the login page
        return redirect(loginView)


# ─── BROWSE ───────────────────────────────────────────────────────────────────
def browse(request):
    user_profile = None
    if request.user.is_authenticated:
        try:
            user_profile = request.user.profile
        except Profile.DoesNotExist:
            pass

    is_producer = user_profile and user_profile.is_producer()
    filter_form = BrowseFilterForm(request.GET or None)

    search    = request.GET.get('search', '')
    category  = request.GET.get('category', '')
    state     = request.GET.get('state', '')
    max_price = request.GET.get('max_price', '')
    avail_only = request.GET.get('available_only', '')
    organic   = request.GET.get('organic', '')
    sort      = request.GET.get('sort', 'name')

    if is_producer:
        # Producer sees: restaurant requests (what buyers want)
        qs = RestaurantRequest.objects.filter(active=True).select_related('buyer__user')
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(buyer__business_name__icontains=search))
        if category:
            qs = qs.filter(category=category)
        if state:
            qs = qs.filter(buyer__state__icontains=state)
        qs = qs.order_by('title' if sort == 'name' else '-id')
        context = {
            'is_producer': True,
            'requests': qs,
            'filter_form': filter_form,
            'result_count': qs.count(),
            'categories': ['Vegetables', 'Fruits', 'Dairy & Eggs', 'Meat & Poultry'],
        }
    else:
        # Buyer / guest sees: product listings from producers
        qs = Product.objects.select_related('producer__user').order_by('producer__user')
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(producer__business_name__icontains=search))
        if category:
            qs = qs.filter(category=category)
        if state:
            qs = qs.filter(producer__state__icontains=state)
        if max_price:
            try:
                qs = qs.filter(price__lte=float(max_price))
            except ValueError:
                pass
        if avail_only:
            qs = qs.filter(available=True)
        if organic == "true":
            qs = qs.filter(organic=True)
        if sort == 'price':
            qs = qs.order_by('price')
        elif sort == '-price':
            qs = qs.order_by('-price')
        else:
            qs = qs.order_by('name')
        context = {
            'is_producer': False,
            'products': qs,
            'filter_form': filter_form,
            'result_count': qs.count(),
            'user_profile': user_profile,
            'categories': ['Vegetables', 'Fruits', 'Dairy & Eggs', 'Meat & Poultry'],
        }

    return render(request, 'browse.html', context)


# ─── PRODUCER PROFILE (manage own) ───────────────────────────────────────────
@login_required
def producer_profile(request):
    profile = get_object_or_404(Profile, user_id=request.user.id)
    if profile.is_buyer():
        return redirect('buyer_profile')

    products = Product.objects.filter(producer_id=request.user.id).order_by('-created_at')
    product_form = ProductForm()
    profile_message = ''
    product_message = ''
    new_product = False
    if request.method == 'POST':
        action = request.POST.get('action')
        if action[-1].isnumeric():
            values = action.split()
            action = values[0]
            id = values[1]
        print(action)
        if action == 'edit_profile':
            pf = ProfileEditForm(request.POST, request.FILES, instance=profile)
            if pf.is_valid():
                pf.save()
                profile_message = "Profile updated!"
        elif action == 'new_product':
            new_product = True
        elif action == 'add_product':
            product_form = ProductForm(request.POST, request.FILES)
            if product_form.is_valid():
                prod = product_form.save(commit=False)
                prod.producer_id = request.user.id
                prod.save()
                product_message = f"'{prod.name}' added to your listings."
        elif action == 'delete_product':
            Product.objects.filter(id=id).delete()
            product_message = "Product removed."
        elif action == 'toggle_available':
            prod = get_object_or_404(Product, id=id)
            prod.available = not prod.available
            prod.save()

    name1 = request.user.first_name
    name2 = request.user.last_name
    

    profile_form = ProfileEditForm(initial={
            'email': request.user.email,
            }, instance=profile)
    return render(request, 'producer_profile.html', {
        'profile': profile,
        'products': products,
        'profile_form': profile_form,
        'product_form': product_form,
        'name' : name1 + " " + name2,
        'prof_message' : profile_message,
        'prod_message' : product_message,
        'new_product' : new_product
    })


# ─── BUYER PROFILE (manage own) ──────────────────────────────────────────────
@login_required
def buyer_profile(request):
    profile = get_object_or_404(Profile, user_id=request.user.id)
    if profile.is_producer():
        return redirect('producer_profile')

    saved = SavedProducer.objects.filter(buyer=profile).select_related('producer__user')
    my_requests = profile.requests.all().order_by('-created_at')
    req_form = RestaurantRequestForm()

    profile_message = ""

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'edit_profile':
            pf = ProfileEditForm(request.POST, request.FILES, instance=profile)
            if pf.is_valid():
                pf.save()
                profile.user.first_name = pf.cleaned_data.get('first_name', '')
                profile.user.last_name  = pf.cleaned_data.get('last_name', '')
                profile.user.save()
                profile_message = "Profile updated!"
                return redirect('buyer_profile')
        elif action == 'add_request':
            req_form = RestaurantRequestForm(request.POST)
            if req_form.is_valid():
                rq = req_form.save(commit=False)
                rq.buyer = profile
                rq.save()
                profile_message = "Request posted! Producers can now find you."
                return redirect('buyer_profile')
        elif action == 'delete_request':
            rid = request.POST.get('request_id')
            RestaurantRequest.objects.filter(id=rid, buyer=profile).delete()
            profile_message = "Request removed."
            return redirect('buyer_profile')
        elif action == 'unsave':
            pid = request.POST.get('producer_id')
            SavedProducer.objects.filter(buyer=profile, producer_id=pid).delete()
            profile_message = "Removed from saved."
            return redirect('buyer_profile')

    profile_form = ProfileEditForm(instance=profile, initial={
        'first_name': profile.user.first_name,
        'last_name':  profile.user.last_name,
    })
    return render(request, 'buyer_profile.html', {
        'profile': profile,
        'saved': saved,
        'my_requests': my_requests,
        'profile_form': profile_form,
        'req_form': req_form,
        'profile_message' : profile_message
    })
