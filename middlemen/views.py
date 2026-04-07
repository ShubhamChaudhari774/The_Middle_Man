from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from .models import Profile, Product, RestaurantRequest, Message, SavedProducer, Producer, Customer
from .forms import (SignUpForm, LoginForm, ProfileEditForm,
                    ProductForm, RestaurantRequestForm, MessageForm, BrowseFilterForm)

def profileView(request):
    return render(request, "profile.html")

def messagesView(request):
    return render(request, "messages.html")

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
        qs = Product.objects.select_related('producer__user').order_by('name')
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
    profile = get_object_or_404(Profile, user=request.user)
    if not profile.is_producer():
        return redirect('buyer_profile')

    products = profile.products.all().order_by('-created_at')
    product_form = ProductForm()

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'edit_profile':
            pf = ProfileEditForm(request.POST, request.FILES, instance=profile)
            if pf.is_valid():
                pf.save()
                profile.user.first_name = pf.cleaned_data.get('first_name', '')
                profile.user.last_name  = pf.cleaned_data.get('last_name', '')
                profile.user.save()
                messages.success(request, "Profile updated!")
                return redirect('producer_profile')
        elif action == 'add_product':
            product_form = ProductForm(request.POST, request.FILES)
            if product_form.is_valid():
                prod = product_form.save(commit=False)
                prod.producer = profile
                prod.save()
                messages.success(request, f"'{prod.name}' added to your listings.")
                return redirect('producer_profile')
        elif action == 'delete_product':
            pid = request.POST.get('product_id')
            Product.objects.filter(id=pid, producer=profile).delete()
            messages.success(request, "Product removed.")
            return redirect('producer_profile')
        elif action == 'toggle_available':
            pid = request.POST.get('product_id')
            prod = get_object_or_404(Product, id=pid, producer=profile)
            prod.available = not prod.available
            prod.save()
            return redirect('producer_profile')

    profile_form = ProfileEditForm(instance=profile, initial={
        'first_name': profile.user.first_name,
        'last_name':  profile.user.last_name,
    })
    return render(request, 'producer_profile.html', {
        'profile': profile,
        'products': products,
        'profile_form': profile_form,
        'product_form': product_form,
    })


# ─── BUYER PROFILE (manage own) ──────────────────────────────────────────────
@login_required
def buyer_profile(request):
    profile = get_object_or_404(Profile, user=request.user)
    if not profile.is_buyer():
        return redirect('producer_profile')

    saved = SavedProducer.objects.filter(buyer=profile).select_related('producer__user')
    my_requests = profile.requests.all().order_by('-created_at')
    req_form = RestaurantRequestForm()

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'edit_profile':
            pf = ProfileEditForm(request.POST, request.FILES, instance=profile)
            if pf.is_valid():
                pf.save()
                profile.user.first_name = pf.cleaned_data.get('first_name', '')
                profile.user.last_name  = pf.cleaned_data.get('last_name', '')
                profile.user.save()
                messages.success(request, "Profile updated!")
                return redirect('buyer_profile')
        elif action == 'add_request':
            req_form = RestaurantRequestForm(request.POST)
            if req_form.is_valid():
                rq = req_form.save(commit=False)
                rq.buyer = profile
                rq.save()
                messages.success(request, "Request posted! Producers can now find you.")
                return redirect('buyer_profile')
        elif action == 'delete_request':
            rid = request.POST.get('request_id')
            RestaurantRequest.objects.filter(id=rid, buyer=profile).delete()
            messages.success(request, "Request removed.")
            return redirect('buyer_profile')
        elif action == 'unsave':
            pid = request.POST.get('producer_id')
            SavedProducer.objects.filter(buyer=profile, producer_id=pid).delete()
            messages.success(request, "Removed from saved.")
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
    })


# ─── MESSAGING ────────────────────────────────────────────────────────────────
@login_required
def messages_view(request):
    user = request.user
    # All users the current user has talked to
    partners_ids = Message.objects.filter(
        Q(sender=user) | Q(recipient=user)
    ).values_list('sender', 'recipient')

    partner_set = set()
    for s, r in partners_ids:
        partner_set.add(s if s != user.id else r)

    partners = User.objects.filter(id__in=partner_set)

    # active conversation
    active_id = request.GET.get('with')
    active_user = None
    conversation = []
    msg_form = MessageForm()

    if active_id:
        active_user = get_object_or_404(User, id=active_id)
        conversation = Message.objects.filter(
            Q(sender=user, recipient=active_user) |
            Q(sender=active_user, recipient=user)
        ).order_by('created_at')
        # mark received as read
        conversation.filter(recipient=user, read=False).update(read=True)

        if request.method == 'POST':
            msg_form = MessageForm(request.POST)
            if msg_form.is_valid():
                m = msg_form.save(commit=False)
                m.sender = user
                m.recipient = active_user
                m.save()
                return redirect(f'/messages/?with={active_id}')

    unread_count = Message.objects.filter(recipient=user, read=False).count()

    return render(request, 'messages.html', {
        'partners': partners,
        'active_user': active_user,
        'conversation': conversation,
        'msg_form': msg_form,
        'unread_count': unread_count,
    })


# ─── START CONVERSATION (from browse) ────────────────────────────────────────
@login_required
def start_message(request, user_id):
    recipient = get_object_or_404(User, id=user_id)
    return redirect(f'/messages/?with={user_id}')


# ─── SAVE PRODUCER (buyer action) ─────────────────────────────────────────────
@login_required
def save_producer(request, producer_id):
    buyer_profile = get_object_or_404(Profile, user=request.user, role='buyer')
    producer_profile_obj = get_object_or_404(Profile, id=producer_id, role='producer')
    SavedProducer.objects.get_or_create(buyer=buyer_profile, producer=producer_profile_obj)
    messages.success(request, f"{producer_profile_obj.business_name or producer_profile_obj.user.username} saved!")
    return redirect('browse')
