from django.urls import path
from . import views

urlpatterns = [
    # --- 📄 Негизги баракчалар ---
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('price/', views.price, name='price'),
    path('reviews/', views.reviews, name='reviews'),
    path('contact/', views.contact, name='contact'),

    # --- 🤖 AI Чат жана Заказ жөнөтүү (API) ---
    path('strawberry-chat/', views.strawberry_chat_api, name='strawberry_chat'),
    path('submit-order/', views.submit_order, name='submit_order'),

    # --- ❤️ Лайк басуу үчүн жаңы жол ---
    # Бул сап JavaScript'тен келген лайк сурамдарын кабыл алат
    path('toggle-like/<int:set_id>/', views.toggle_like, name='toggle_like'),
]