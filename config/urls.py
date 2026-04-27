from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Бул импортторду кошуңуз:
from django.contrib.sitemaps.views import sitemap
from shop.sitemaps import StaticViewSitemap

# Карталардын тизмеси
sitemaps = {
    'static': StaticViewSitemap,
}

urlpatterns = [
    # ====================== Админ панели ======================
    path('admin/', admin.site.urls),

    # ====================== Негизги колдонмо (shop) ======================
    path('', include('shop.urls')),

    # ====================== Google үчүн Sitemap ======================
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps},
         name='django.contrib.sitemaps.views.sitemap'),
]

# ====================== Каталарды иштетүү (Handlers) ======================
# Бул функциялар 'shop' тиркемесиндеги 'views.py' ичинде болушу керек
handler404 = 'shop.views.custom_page_not_found'
handler500 = 'shop.views.custom_server_error'

# ====================== Медиа файлдар ======================
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # config/urls.py

    urlpatterns = [
        path('admin/', admin.site.urls),
        path('', include('shop.urls')),
        path('accounts/', include('accounts.urls')),  # Ушул сапты кошуңуз
    ]
  