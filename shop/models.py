from django.db import models
from cloudinary.models import CloudinaryField


# ====================== 🎁 ТОПТОМДОР МОДЕЛИ ======================
class ProductSet(models.Model):
    title = models.CharField(max_length=200, verbose_name="Топтомдун аталышы")
    pieces = models.IntegerField(verbose_name="Даана саны")
    price = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="Баасы (сом)")
    ready_time = models.CharField(
        max_length=100,
        verbose_name="Даяр болуу убактысы",
        default="2 саат"
    )
    image = CloudinaryField(
        folder='sets/images/',
        blank=True,
        null=True,
        verbose_name="Сүрөтү"
    )
    video = CloudinaryField(
        resource_type='auto',
        folder='sets/videos/',
        blank=True,
        null=True,
        verbose_name="Видеосу"
    )
    whatsapp_msg = models.TextField(verbose_name="WhatsApp билдирүүсү")

    # Лайктардын санын сактоочу талаа
    likes = models.PositiveIntegerField(
        default=0,
        verbose_name="Лайктардын саны"
    )

    def __str__(self):
        return f"{self.title} ({self.pieces} даана) — ❤️ {self.likes}"

    class Meta:
        verbose_name = "Топтом"
        verbose_name_plural = "Топтомдор"


## ====================== 💬 ПИКИРЛЕР МОДЕЛИ (ОҢДОЛДУ) ======================
class Review(models.Model):
    name = models.CharField(max_length=100, verbose_name="Кардардын аты")
    message = models.TextField(verbose_name="Пикирдин тексти")
    stars = models.IntegerField(default=5, verbose_name="Жылдыз саны")

    # БУЛ ТАЛААНЫ КОШУҢУЗ:
    image = CloudinaryField(
        folder='reviews/images/',
        blank=True,
        null=True,
        verbose_name="Кардардын сүрөтү"
    )

    # Админдин жообу (Эгер мурунку коддо бар болсо)
    admin_reply = models.TextField(blank=True, null=True, verbose_name="Админдин жообу")

    likes = models.PositiveIntegerField(default=0, verbose_name="Лайктар")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Кошулган убактысы")

    def __str__(self):
        return f"{self.name} — {self.stars} ★"

    class Meta:
        verbose_name = "Пикир"
        verbose_name_plural = "Пикирлер"


# ====================== 🎵 МУЗЫКА МОДЕЛИ ======================
class BackgroundMusic(models.Model):
    title = models.CharField(max_length=100, verbose_name="Музыканын аталышы")
    audio_file = CloudinaryField(
        resource_type='video',  # Cloudinary аудиону 'video' катары сактайт
        folder='sets/music/',
        verbose_name="MP3 файл"
    )
    is_active = models.BooleanField(
        default=False,
        verbose_name="Азыр ойнолсунбу?"
    )

    def save(self, *args, **kwargs):
        # Бир музыка иштесе, калгандарын автоматтык түрдө өчүрүү
        if self.is_active:
            BackgroundMusic.objects.filter(is_active=True).exclude(id=self.id).update(is_active=False)
        super().save(*args, **kwargs)

    def __str__(self):
        status = " [АКТИВДҮҮ]" if self.is_active else ""
        return f"{self.title}{status}"

    class Meta:
        verbose_name = "Фондук музыка"
        verbose_name_plural = "Фондук музыкалар"