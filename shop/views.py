import time
import random
import requests
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from .models import ProductSet
from fuzzywuzzy import fuzz


# 📩 TELEGRAM ЖӨНӨТҮҮ
def send_telegram_message(name, phone, message):
    token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID
    url = f"https://api.telegram.org/bot{token}/sendMessage"

    text = (
        f"🍰 *Жаңы заказ (SSMOD)*\n\n"
        f"👤 *Аты:* {name}\n"
        f"📞 *Тел:* {phone}\n"
        f"💬 *Билдирүү:* {message if message else 'Жок'}"
    )

    payload = {'chat_id': chat_id, 'text': text, 'parse_mode': 'Markdown'}

    try:
        response = requests.post(url, data=payload)
        print(response.text)  # DEBUG
    except Exception as e:
        print(f"Telegram Error: {e}")


# 🤖 AI ЧАТ (АКЫЛДУУ БЕКЕР БОТ)
def strawberry_chat_api(request):
    time.sleep(1)

    # ✅ GET + POST колдоо
    user_query = request.GET.get('message') or request.POST.get('message', '')
    user_query = user_query.lower().strip()

    if not user_query:
        return JsonResponse({'reply': "Салам! 🍓 Кантип жардам берейин?"})

    # 📚 БАЗА
    knowledge_base = {
        # --- 1. САЛАМДАШУУ ЖАНА ЖАКШЫ МААНАЙ ---
        "саламдашуу": {
            "keywords": ["салам", "привет", "hello", "амансызбы", "кандай", "кеч жарык", "кутуман"],
            "reply": "Саламатсызбы! Эң таттуу десерттердин мекени — SSMOD жардамчысымын 🍓 Сизге кандай жардам бере алам?"
        },
        "ыраазычылык": {
            "keywords": ["рахмат", "спасибо", "чоң рахмат", "ыраазы", "жакшы"],
            "reply": "Сизге да чоң рахмат! Сиздин жылмаюуңуз — биздин ийгилигибиз! 😊✨"
        },

        # --- 2. ПРОДУКЦИЯ ЖАНА МЕНЮ ---
        "клубника": {
            "keywords": ["клубника", "кулпунай", "шоколад", "белек", "набор"],
            "reply": "Биз эң таза жана жаңы клубникаларды колдонобуз. Бельгия шоколады менен капталган десерттерибиз эң популярдуу! 🍫🍓"
        },
        "торттор": {
            "keywords": ["торт", "вупи пай", "красный бархат", "молочная девочка", "заказ торт"],
            "reply": "Ооба, бизде ар кандай майрамдарга торттор бар. Заказды 1-2 күн мурун берсеңиз болот 🍰"
        },
        "баалар": {
            "keywords": ["баа", "канча", "сом", "цена", "прайс", "дорого", "арзан"],
            "reply": "Баалар топтомдун өлчөмүнө жараша: 8-клубника 800 сомдон башталат. Толук прайс 'Баалар' бөлүмүндө 💸"
        },

        # --- 3. ЖЕТКИРҮҮ ЖАНА ДАРЕК ---
        "жеткирүү": {
            "keywords": ["жеткирүү", "доставка", "курьер", "алып келүү"],
            "reply": "Ош шаары ичинде жеткирүү 100-150 сом. 3төн ашык топтом алсаңыз — акысыз! 🚚"
        },
        "дарек": {
            "keywords": ["кайда", "адрес", "жер", "ориентир", "локация"],
            "reply": "Биз Ош шаарындабыз. Негизги филиал: Ленин көчөсү (борбордо) 📍"
        },
        "иш_убактысы": {
            "keywords": ["качан", "убакыт", "ачык", "жабык", "график"],
            "reply": "Биз күн сайын саат 10:00дөн 22:00гө чейин кызматтабыз 🕙"
        },

        # --- 4. ЗАКАЗ ЖАНА ТӨЛӨМ ---
        "заказ": {
            "keywords": ["заказ", "буюртма", "алайын", "сатып алуу"],
            "reply": "Заказ берүү үчүн сайттагы 'Заказ берүү' баскычын басып, номериңизди калтырыңыз же бизге чалыңыз 😍"
        },
        "төлөм": {
            "keywords": ["төлөм", "акча", "карта", "элсом", "оденьги", "накталай"],
            "reply": "Төлөмдөрдү МБанк, Элсом же накталай кабыл алабыз 💳"
        },

        # --- 5. КОМПАНИЯ ЖАНА АДМИН ---
        "админ": {
            "keywords": ["админ", "жетекчи", "ким", "искак", "хозяин"],
            "reply": "Мен, Жолдубай уулу Искак, SSMOD негиздөөчүсү катары ар бир клубниканын сапатына жана шоколаддын тазалыгына жеке өзүм кепилдик берем. Биз 2 жылдан бери Ош шаарында миңдеген кыздарга жылмаюу тартууладык. Биздин максат — сиздин жакыныңызды бактылуу кылуу."
        },
        "вакансия": {
            "keywords": ["жумуш", "вакансия", "иш", "курьер керек", "кондитер"],
            "reply": "Учурда вакансиялар боюнча @ssmod_admin Телеграм номерине жазсаңыз болот 💼"
        },
        "кыздарга_жагат": {
            "keywords": ["кыздарга", "белек", "сюрприз", "эмне алсам", "жагат"],
            "reply": "Кыздар эстетиканы жана назик даамды баалашат! 🍓💖 Биздин 'Premium' топтомубуз (шоколаддагы клубника жана роза гүлдөрү) — бул эң катаал кыздын да жүрөгүн жибите турган белек. Сизге эң коозун тандап берейинби?"
        },


        # --- 6. МАЙРАМДАР ---
        "майрам": {
            "keywords": ["туулган күн", "8-март", "14-февраль", "сюрприз", "кыз узатуу"],
            "reply": "Биз сиздин өзгөчө күнүңүздү унутулгус кылабыз! Романтикалык топтомдор жана майрамдык жасалгалар бар 🎁✨"


        }
    }

    # ✅ 1. ТҮЗ keyword текшерүү (ЭҢ ТЕЗ)
    for category in knowledge_base.values():
        for keyword in category["keywords"]:
            if keyword in user_query:
                return JsonResponse({'reply': category["reply"]})

    # ✅ 2. FUZZY (АКЫЛДУУ)
    best_match = None
    highest_score = 0

    for category in knowledge_base.values():
        for keyword in category["keywords"]:
            score = fuzz.partial_ratio(user_query, keyword)
            if score > highest_score:
                highest_score = score
                best_match = category["reply"]

    # ❗ жооп тандоо
    if highest_score > 50:
        reply = best_match
    else:
        reply = random.choice([
            "Түшүнбөй калдым 🤔 башкача жазып көрүңүз",
            "Кечириңиз, такыраак жазыңыз 😊",
            "Сурооңузду өзгөртүп көрүңүз 🍓"
        ])

    return JsonResponse({'reply': reply})


# 📄 PAGES
def home(request):
    if request.method == "POST":
        user_name = request.POST.get('userName')
        user_phone = request.POST.get('userPhone')
        user_msg = request.POST.get('userMsg')

        send_telegram_message(user_name, user_phone, user_msg)

        messages.success(request, "Заказыңыз кабыл алынды!")
        return redirect('home')

    products = ProductSet.objects.all()
    return render(request, 'shop/index.html', {'products': products})


def about(request):
    return render(request, 'shop/about.html')


def price(request):
    sets = ProductSet.objects.all()
    return render(request, 'shop/price.html', {'sets': sets})


def reviews(request):
    return render(request, 'shop/reviews.html')


def contact(request):
    return render(request, 'shop/contact.html')