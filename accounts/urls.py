from django.urls import path
from .views import login_view, profile_view, logout_view

urlpatterns = [
    # Кирүү барагы (Аты жана номери менен код алуу)
    path('login/', login_view, name='login'),

    # Жеке кабинет (Кардардын өзүнүн товарлары жана маалыматы)
    path('profile/', profile_view, name='profile'),

    # Системадан чыгуу
    path('logout/', logout_view, name='logout'),
]