import os
import django
from django.contrib.auth import get_user_model

# Сиздин settings.py файлы 'config' папкасында болгондуктан ушундай калтырабыз
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

User = get_user_model()

# Сиз сураган маалыматтар:
username = 'iskak'
password = 'YourPassword235467!' # Коопсуздук үчүн кичине татаалдаштырдык (YourPassword коштук)
email = 'admin@lux.kg'

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"Ийгиликтүү: Админ '{username}' түзүлдү!")
else:
    # Эгер бул логин бар болсо, паролун жаңылап коёт
    user = User.objects.get(username=username)
    user.set_password(password)
    user.save()
    print(f"Админ '{username}' мурда эле бар болчу, паролу жаңыланды.")