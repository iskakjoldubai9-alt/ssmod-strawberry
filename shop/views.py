import time
import json
import random
import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from .models import ProductSet, BackgroundMusic
from fuzzywuzzy import fuzz

# --- ❤️ ЛАЙК БАСУУ ФУНКЦИЯСЫ (ОҢДОЛГОН) ---
import json


def toggle_like(request, set_id):
    if request.method == "POST":
        try:
            # JavaScript'тен келген JSON маалыматты окуйбуз (is_active: true/false)
            data = json.loads(request.body)
            is_active = data.get('is_active', True)

            product = get_object_or_404(ProductSet, id=set_id)

            if is_active:
                # Эгер колдонуучу лайк басса - кошобуз
                product.likes += 1
            else:
                # Эгер колдонуучу лайкты кайра алса - азайтабыз (бирок 0дон төмөн түшүрбөйбүз)
                if product.likes > 0:
                    product.likes -= 1

            product.save()

            return JsonResponse({
                'status': 'success',
                'total_likes': product.likes
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


# --- 📩 TELEGRAM БИЛДИРҮҮ ЖӨНӨТҮҮ ФУНКЦИЯСЫ ---
def send_telegram_message(chat_id, name, phone, message, title="🍓 ЖАҢЫ ЗАКАЗ (SSMOD)"):
    token = settings.TELEGRAM_BOT_TOKEN
    url = f"https://api.telegram.org/bot{token}/sendMessage"

    # Текстти кооздоо жана калыпка салуу
    text = (
        f"*{title}*\n"
        f"━━━━━━━━━━━━━━━\n"
        f"👤 *Кардар:* {name}\n"
        f"📞 *Телефон:* {phone}\n"
        f"━━━━━━━━━━━━━━━\n"
        f"📝 *ЗАКАЗДЫН МАНЫЗЫ:*\n{message}\n"
        f"━━━━━━━━━━━━━━━\n"
        f"⏰ *Убактысы:* {time.strftime('%d.%m.%Y %H:%M:%S')}"
    )

    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'Markdown'
    }

    try:
        response = requests.post(url, data=payload)
        return response.status_code == 200
    except Exception as e:
        print(f"Telegram Message Error: {e}")
        return False


# --- 📥 ЗАКАЗДЫ КАБЫЛ АЛУУ (AJAX/FETCH ҮЧҮН) ---
def submit_order(request):
    if request.method == "POST":
        try:
            # JavaScript'тен келген JSON маалыматты окуу
            data = json.loads(request.body)

            # 1. Маалыматтарды алуу
            name = data.get('name', 'Жазылган эмес')
            phone = data.get('phone', 'Жазылган эмес')
            title = data.get('title', 'Белгисиз топтом')
            qty = data.get('qty', 1)
            total = data.get('total', '0 сом')
            delivery_type = data.get('delivery', 'Көрсөтүлгөн эмес')
            extra_info = data.get('extra', 'Маалымат жок')
            payment_method = data.get('payment', 'Накталай')

            # 2. АДМИНГЕ толук маалыматты даярдоо
            admin_details = (
                f"🎁 *Топтом:* {title}\n"
                f"🔢 *Саны:* {qty} даана\n"
                f"💰 *Жалпы сумма:* {total}\n"
                f"💳 *Төлөм ыкмасы:* {payment_method}\n"
                f"🚚 *Жеткирүү:* {delivery_type}\n"
                f"🏠 *Дарек/Убакыт:* {extra_info}"
            )

            # Негизги админдин чатына билдирүү жөнөтүү
            send_telegram_message(settings.TELEGRAM_CHAT_ID, name, phone, admin_details)

            # 3. КУРЬЕРГЕ ЖӨНӨТҮҮ
            if delivery_type == "Доставка":
                courier_id = getattr(settings, 'DELIVERY_USER_CHAT_ID', None)
                if courier_id:
                    courier_details = (
                        f"📦 *Заказ:* {title} ({qty} шт)\n"
                        f"📍 *Дареги:* {extra_info}\n"
                        f"📱 *Кардардын телефону:* {phone}\n"
                        f"💰 *Алынуучу сумма:* {total}"
                    )
                    send_telegram_message(
                        courier_id,
                        name,
                        phone,
                        courier_details,
                        title="🚚 КУРЬЕРГЕ ТАПШЫРМА"
                    )

            return JsonResponse({
                'status': 'success',
                'message': 'Заказыңыз кабыл алынды! 🍓 Чекти WhatsApp аркылуу жөнөтүүнү унутпаңыз.'
            })

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Маалымат форматында ката бар!'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Системалык ката: {str(e)}'}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Жараксыз сурам (Invalid request)'}, status=400)


# --- 🤖 AI ЧАТ (АКЫЛДУУ ЖАРДАМЧЫ) ---
def strawberry_chat_api(request):
    user_query = request.GET.get('message') or request.POST.get('message', '')
    user_query = user_query.lower().strip()

    if not user_query:
        return JsonResponse({'reply': "Салам! 🍓 Мен SSMOD жардамчысымын. Сизге кантип жардам бере алам?"})

    knowledge_base = {
        "саламдашуу": {
            "keywords": ["салам", "привет", "hello", "амансызбы", "кандай", "кеч жарык", "саламатсызбы"],
            "reply": "Саламатсызбы! 😊 Сизге эң таттуу белектерди тандоого жардам берем. Биздин менюну көрдүңүзбү?"
        },
        "ыраазычылык": {
            "keywords": ["рахмат", "спасибо", "чоң рахмат", "ыраазы", "жакшы", "ок", "макул"],
            "reply": "Ар дайым кызматыңыздабыз! Таттуу маанай каалайм ✨"
        },
        "клубника": {
            "keywords": ["клубника", "кулпунай", "шоколад", "белек", "набор", "коробка"],
            "reply": "Биздин кулпунайлар чыныгы Бельгия шоколады менен капталат. 🍫🍓 Жаңы жана өтө таттуу! 'Меню' бөлүмүнөн тандасаңыз болот."
        },
        "торттор": {
            "keywords": ["торт", "вупи пай", "красный бархат", "молочная девочка", "заказ торт", "бисквит"],
            "reply": "Тортторду 24-48 саат мурун заказ кылууну сунуштайбыз. 🍰 Ар бир торт жаңы бышырылат!"
        },
        "баалар": {
            "keywords": ["баа", "канча", "сом", "цена", "прайс", "арзан", "стоимость"],
            "reply": "Топтомдор 800 сомдон башталат. Ичиндеги кулпунайдын санына жана шоколаддын түрүнө жараша өзгөрөт. 💸"
        },
        "жеткирүү": {
            "keywords": ["жеткирүү", "доставка", "курьер", "алып келүү", "акысы"],
            "reply": "Ош шаары ичинде жеткирүү бар. 🚚 Акысы аралыкка жараша 100-150 сом. 1500 сомдон жогору заказ кылсаңыз, кээде акциялар болот!"
        },
        "дарек": {
            "keywords": ["кайда", "адрес", "жер", "ориентир", "локация", "офис"],
            "reply": "Биз Ош шаарында жайгашканбыз. 📍 Так даректи 'Байланыш' (Contact) бөлүмүнөн карта аркылуу көрө аласыз."
        },
        "иштөө_убактысы": {
            "keywords": ["качан", "убакыт", "саат канча", "иштейсиз", "график"],
            "reply": "Биз күн сайын саат 09:00дөн 21:00гө чейин заказдарды кабыл алабыз. 🕘"
        }
    }

    for category in knowledge_base.values():
        for keyword in category["keywords"]:
            if keyword in user_query:
                return JsonResponse({'reply': category["reply"]})

    best_match = None
    highest_score = 0
    for category in knowledge_base.values():
        for keyword in category["keywords"]:
            score = fuzz.partial_ratio(user_query, keyword)
            if score > highest_score:
                highest_score = score
                best_match = category["reply"]

    if highest_score > 65:
        reply = best_match
    else:
        reply = random.choice([
            "Кечириңиз, сурооңузду толук түшүнбөй калдым 🤔",
            "Бул суроо боюнча оператор менен байланышып көрүңүз же менюну карап чыгыңыз 🍓",
            "Мен азырынча үйрөнүп жатам, сурооңузду кыскараак берип көрүңүзчү 😊"
        ])

    return JsonResponse({'reply': reply})


# --- 📄 БААРДЫК БАТТАР (PAGES) ---

def home(request):
    active_music = BackgroundMusic.objects.filter(is_active=True).first()
    # Башкы бетте эң көп лайк алгандар жана эң жаңылары "Рек" катары чыгат
    products = ProductSet.objects.all().order_by('-likes', '-id')[:6]
    return render(request, 'shop/index.html', {
        'products': products,
        'active_music': active_music
    })


def price(request):
    """
    Бул жерде 'Рек' системасы ишке ашат.
    Лайкы эң көп топтомдор тизменин башына чыгат.
    """
    active_music = BackgroundMusic.objects.filter(is_active=True).first()

    # Сиз сурагандай: Лайкы эң көптөрү биринчи чыгат (Рекке)
    # '-likes' эң көп лайктан азга карай тизет
    sets = ProductSet.objects.all().order_by('-likes', 'price')

    return render(request, 'shop/price.html', {
        'sets': sets,
        'active_music': active_music
    })


def about(request):
    active_music = BackgroundMusic.objects.filter(is_active=True).first()
    return render(request, 'shop/about.html', {
        'active_music': active_music
    })


def reviews(request):
    active_music = BackgroundMusic.objects.filter(is_active=True).first()
    return render(request, 'shop/reviews.html', {
        'active_music': active_music
    })


def contact(request):
    active_music = BackgroundMusic.objects.filter(is_active=True).first()
    return render(request, 'shop/contact.html', {
        'active_music': active_music
    })