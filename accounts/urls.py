from django.urls import path
from .views import login_view, profile_view, logout_view, submit_order, reviews

app_name = 'accounts'  # Namespace колдонуу сунушталат

urlpatterns = [
    # Кирүү барагы (Аты жана номери менен код алуу)
    path('login/', login_view, name='login'),

    # Жеке кабинет (Кардардын өзүнүн товарлары жана маалыматы)
    path('profile/', profile_view, name='profile'),

    # Системадан чыгуу
    path('logout/', logout_view, name='logout'),

    # Заказды кабыл алуу (AJAX сурамдары үчүн)
    path('submit-order/', submit_order, name='submit_order'),

    # Пикирлерди кабыл алуу жана көрсөтүү
    path('reviews/', reviews, name='reviews'),
]