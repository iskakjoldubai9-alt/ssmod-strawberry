from django.contrib import admin
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

    # --- 💬 ПИКИРЛЕР БӨЛҮМҮ ---
    path('reviews/', views.reviews, name='reviews'),
    path('delete-review/<int:review_id>/', views.delete_review, name='delete_review'),
    # ПИКИРЛЕРДИН лайкын бөлүү үчүн ушул сап маанилүү:
    path('toggle-review-like/<int:review_id>/', views.toggle_review_like, name='toggle_review_like'),

    # --- 🤖 API & ФУНКЦИЯЛАР ---
    path('strawberry-chat/', views.strawberry_chat_api, name='strawberry_chat'),
    path('submit-order/', views.submit_order, name='submit_order'),

    # Бул топтомдордун (price беттеги) лайкы үчүн:
    path('toggle-like/<int:set_id>/', views.toggle_like, name='toggle_like'),
]

# Сүрөттөр жана статикалык файлдар үчүн (DEBUG режиминде)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# 404 катасы (Баракча табылбаса)
handler404 = 'shop.views.page_not_found'