from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import ProductSet, BackgroundMusic


# 1. МУЗЫКА ҮЧҮН АДМИН ПАНЕЛЬ
@admin.register(BackgroundMusic)
class BackgroundMusicAdmin(admin.ModelAdmin):
    # Тизмеде аталышы жана активдүүлүгү көрүнөт
    list_display = ('title', 'is_active', 'get_audio_player')

    # Тизмеден эле "is_active" кутучасын басып алмаштырса болот
    list_editable = ('is_active',)

    # Админ панелден музыканы угуп көрүү үчүн плеер
    def get_audio_player(self, obj):
        if obj.audio_file:
            return mark_safe(
                f'<audio src="{obj.audio_file.url}" controls style="height:30px;"></audio>'
            )
        return "Файл жок"

    get_audio_player.short_description = "Угуп көрүү"


# 2. ПРОДУКЦИЯ ҮЧҮН АДМИН ПАНЕЛЬ (ЛАЙК МЕНЕН ЖАҢЫРТЫЛДЫ)
@admin.register(ProductSet)
class ProductSetAdmin(admin.ModelAdmin):
    # Тизмеге 'likes' талаасы кошулду, эми канча лайк басылганын көрөсүз
    list_display = ('title', 'price', 'pieces', 'likes', 'get_media_preview')

    # Лайктарды кокустан өзгөртүп албаш үчүн 'readonly_fields' кылып койдук
    readonly_fields = ('likes', 'get_media_preview')

    # Популярдуу товарларды башында көрсөтүү үчүн лайк боюнча иреттөө
    ordering = ('-likes',)

    # Админ панелдин ичиндеги форманын талаалары
    fields = (
        'title',
        'pieces',
        'price',
        'likes',  # Бул жерден да көрүнүп турат
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