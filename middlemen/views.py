from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from middlemen.models import Producer, Customer

# Create your views here.

def homeView(request):
    """
    This view will return the home page of the logged in user; if a user is not logged in it will redirect to the loginView view
    """
    return render(request, 'home.html', {'user': request.user})

def loginView(request):
    """
    This view will render the login page if the user is not authenticated, it will return the user to the home page if the user is already logged in
    """
    if request.user.is_authenticated == True:
        return redirect(homeView)
    else:
        return render(request, 'login.html')

def loginUser(request):
    """
    This view will login a user based on the form submitted by loginView
    """
    if request.user.is_authenticated == True:
        return redirect(homeView)
    else:
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            request.session['username'] = username # store username in session cookie for future reference.
            if user != None:
                login(request, user)
            else:
                return redirect(loginView)
            return redirect(homeView)
        else:
            return redirect(loginView)

def signupView(request):
    """
    This view will render the signup page if the user is not authenticated, it will return the user to the home page if the user is already logged in
    """
    if request.user.is_authenticated == True:
        return redirect(homeView)
    else:
        return render(request, 'signup.html')

def signupUser(request):
    """
    This view will sign up a user based upon the form submitted by the signup view
    """
    if request.user.is_authenticated == True:
        return redirect(homeView)
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
    
def browseView(request):
    name = request.session['username']
    
    print(name)

    if Producer.objects.filter(username=name).exists():
        user_type = 'Producer'
    elif Customer.objects.filter(username=name).exists():
        user_type = 'Customer'
    else:
        user_type = "Undetermined"
        print("Username not found")

    print(user_type)

    if user_type == "Producer":
        users_to_list = Customer.objects.all()
    elif user_type == "Customer":
        users_to_list = Producer.objects.all()
    else:
        print("User type undetermined.")

    filtered_users = User.objects.filter(username__in=users_to_list)

    return render(request, "browse.html", {"rows" : filtered_users})

def profileView(request):
    return render(request, "profile.html")

def messagesView(request):
    return render(request, "messages.html")

def searchView(request):
    return render(request, "search.html")


def logoutUser(request):
    logout(request)
    return redirect(loginView)