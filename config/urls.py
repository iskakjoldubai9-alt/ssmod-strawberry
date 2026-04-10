from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ====================== Админ панели ======================
    path('admin/', admin.site.urls),

    # ====================== Негизги колдонмо (shop) ======================
    # Бардык баракчалар, API'лер жана лайк функциясы ушул жерден келет
    path('', include('shop.urls')),
]

# ====================== Медиа файлдар (DEBUG режиминде) ======================
# Cloudinary колдонуп жатканыңа карабастан, локалдык тест үчүн калтыруу сунушталат
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# ====================== Кошумча: 404 жана 500 ошибкалар үчүн (милдеттүү эмес) ======================
# handler404 = 'shop.views.page_not_found'
# handler500 = 'shop.views.server_error'