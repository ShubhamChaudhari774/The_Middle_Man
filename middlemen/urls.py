from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('browse/', views.browse, name='browse'),
    path('about/', views.about, name='about'),
    path('login/', views.loginView, name='login'),
    path('loginUser/', views.loginUser, name='loginUser'),
    path('logout/', views.logoutUser, name='logout'),
    path('signup/', views.signupView, name='signup'),
    path('signupUser/', views.signupUser, name='signupUser'),
    path('buyer-profile/', views.buyer_profile, name='buyer_profile'),
    path('producer-profile/', views.producer_profile, name='producer_profile'),
    path('messages/', views.messagesView, name='messages'),
    path('sendMessagePage/', views.sendMessageView, name='sendMessageView'),
    path('sendMessage/', views.sendMessageAction, name='sendMessageAction'),
    path('viewMessage/<int:msgID>', views.viewMessage, name='viewMessage'),
    path('deleteMessage/<int:msgID>', views.deleteMessage, name='deleteMessage'),
]

