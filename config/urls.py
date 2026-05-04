from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Импорттор
from django.contrib.sitemaps.views import sitemap
from shop.sitemaps import StaticViewSitemap

# Карталардын тизмеси
sitemaps = {
    'static': StaticViewSitemap,
}

urlpatterns = [
    # 1. Админ панели
    path('admin/', admin.site.urls),

    # 2. Негизги колдонмо (shop)
    path('', include('shop.urls')),

    # 3. Аккаунттар (accounts)
    path('accounts/', include('accounts.urls')),

    # 4. Google үчүн Sitemap
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps},
         name='django.contrib.sitemaps.views.sitemap'),
]

# Каталарды иштетүү (Handlers)
handler404 = 'shop.views.custom_page_not_found'
handler500 = 'shop.views.custom_server_error'

# Медиа жана статикалык файлдар (DEBUG режиминде)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)