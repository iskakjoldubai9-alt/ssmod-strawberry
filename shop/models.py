from django.db import models
from cloudinary.models import CloudinaryField


# --- ТОПТОМДОР МОДЕЛИ (Лайк кошулду) ---
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

    # ЖАҢЫ: Лайктардын санын сактоочу талаа
    # Бул аркылуу кайсы товар өтүмдүү экенин админ панелден көрө аласыз
    likes = models.PositiveIntegerField(
        default=0,
        verbose_name="Лайктардын саны"
    )

    def __str__(self):
        return f"{self.title} ({self.pieces} даана) — ❤️ {self.likes}"

    class Meta:
        verbose_name = "Топтом"
        verbose_name_plural = "Топтомдор"


# --- ЖАҢЫ КОШУЛГОН МУЗЫКА МОДЕЛИ (Өзгөртүүсүз) ---
class BackgroundMusic(models.Model):
    title = models.CharField(max_length=100, verbose_name="Музыканын аталышы (мис: Luxury Jazz)")

    # Музыканы Cloudinary'ге же түз серверге жүктөө
    audio_file = CloudinaryField(
        resource_type='video',  # Cloudinary аудиону 'video' тибинде кабыл алат
        folder='sets/music/',
        verbose_name="MP3 файл"
    )

    is_active = models.BooleanField(
        default=False,
        verbose_name="Азыр ушул музыка ойносунбу?"
    )

    def save(self, *args, **kwargs):
        # Эгерде бир музыка активдүү болсо, калган баарын автоматтык түрдө өчүрөт
        if self.is_active:
            BackgroundMusic.objects.filter(is_active=True).exclude(id=self.id).update(is_active=False)
        super().save(*args, **kwargs)

    def __str__(self):
        status = " [АКТИВДҮҮ]" if self.is_active else ""
        return f"{self.title}{status}"

    class Meta:
        verbose_name = "Фондук музыка"
        verbose_name_plural = "Фондук музыкалар"