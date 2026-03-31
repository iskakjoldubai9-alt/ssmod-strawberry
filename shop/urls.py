from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    # views.price эмес, views.price_page болушу керек:
    path('price/', views.price, name='price'), 
    path('reviews/', views.reviews, name='reviews'),
    path('contact/', views.contact, name='contact'),
path('strawberry-chat/', views.strawberry_chat_api, name='strawberry_chat'),
]