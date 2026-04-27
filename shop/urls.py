from django.http import HttpResponse
from django.contrib import admin
from django.urls import path, include
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from shop import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('price/', views.price, name='price'),
    path('contact/', views.contact, name='contact'),
    path('accounts/', include('accounts.urls')),


    # --- 🛒 КОРЗИНА БӨЛҮМҮ (КАТАНЫ УШУЛ ОҢДОЙТ) ---
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),

    path('google46a46ad5f8267878.html', lambda r: HttpResponse("google-site-verification: google46a46ad5f8267878.html")),

    # --- 💬 ПИКИРЛЕР БӨЛҮМҮ ---
    path('reviews/', views.reviews, name='reviews'),
    path('delete-review/<int:review_id>/', views.delete_review, name='delete_review'),
    path('toggle-review-like/<int:review_id>/', views.toggle_review_like, name='toggle_review_like'),

    # --- 🤖 API & ФУНКЦИЯЛАР ---
    path('strawberry-chat/', views.strawberry_chat_api, name='strawberry_chat'),
    path('submit-order/', views.submit_order, name='submit_order'),
    path('toggle-like/<int:set_id>/', views.toggle_like, name='toggle_like'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'shop.views.page_not_found'