from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import ProductSet, BackgroundMusic, Category  # Category модели кошулду


# ====================== 📂 1. КАТЕГОРИЯЛАР ҮЧҮН АДМИН ПАНЕЛЬ ======================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    # Категориянын аты жана анын HTML фильтрдеги коду (slug) көрүнүп турат
    list_display = ('title', 'slug')

    # Аталышын жазганда slug автоматтык түрдө өзү жазылышы үчүн (ыңгайлуулук үчүн)
    prepopulated_fields = {'slug': ('title',)}


# ====================== 🎵 2. МУЗЫКА ҮЧҮН АДМИН ПАНЕЛЬ ======================
@admin.register(BackgroundMusic)
class BackgroundMusicAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'get_audio_player')
    list_editable = ('is_active',)

    def get_audio_player(self, obj):
        if obj.audio_file:
            return mark_safe(
                f'<audio src="{obj.audio_file.url}" controls style="height:30px;"></audio>'
            )
        return "Файл жок"

    get_audio_player.short_description = "Угуп көрүү"


# ====================== 🎁 3. ПРОДУКЦИЯ ҮЧҮН АДМИН ПАНЕЛЬ ======================
@admin.register(ProductSet)
class ProductSetAdmin(admin.ModelAdmin):
    # Тизмеге 'category' кошулду. Эми кайсы категорияда экени дароо көрүнөт жана тизмеден түз эле өзгөртсө болот
    list_display = ('title', 'category', 'price', 'pieces', 'likes', 'get_media_preview')

    # Тизмеден эле категорияны заматта алмаштыруу мүмкүнчүлүгү
    list_editable = ('category',)

    readonly_fields = ('likes', 'get_media_preview')
    ordering = ('-likes',)

    # Форманын ичине да 'category' талаасы кошулду (тандап киргизүү үчүн)
    fields = (
        'title',
        'category',  # <--- Ушул жерден тандап киргизесиз
        'pieces',
        'price',
        'likes',
        'ready_time',
        'image',
        'video',
        'get_media_preview',
        'whatsapp_msg'
    )

    def get_media_preview(self, obj):
        if obj.video:
            return mark_safe(
                f'<video src="{obj.video.url}" width="150" height="100" '
                f'controls muted style="border-radius:10px; object-fit:cover;"></video>'
            )
        elif obj.image:
            return mark_safe(
                f'<img src="{obj.image.url}" width="100" height="100" '
                f'style="border-radius:10px; object-fit:cover;" />'
            )
        return "Медиа жок"

    get_media_preview.short_description = "Алдын ала көрүү"