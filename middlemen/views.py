from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate

# Create your views here.

def homeView(request):
    """
    This view will return the home page of the logged in user; if a user is not logged in it will redirect to the loginView view
    """
    if request.user.is_authenticated == True:
        return render(request, 'home.html', {'user': request.user})
    else:
        return redirect(loginView)

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
    pass