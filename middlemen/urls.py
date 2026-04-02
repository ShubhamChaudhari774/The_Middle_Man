from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('browse/', views.browse, name='browse'),
    path('about/', views.about, name='about'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup_view, name='signup'),
    path('buyer-profile/', views.buyer_profile, name='buyer_profile'),
    path('producer-profile/', views.producer_profile, name='producer_profile'),
    path('messages/', views.messages_view, name='messages'),
    path('messages/start/<int:user_id>/', views.start_message, name='start_message'),
    path('save-producer/<int:producer_id>/', views.save_producer, name='save_producer'),
]

