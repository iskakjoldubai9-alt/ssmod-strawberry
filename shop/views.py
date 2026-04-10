import json
import time
import requests
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.conf import settings
from .models import ProductSet, BackgroundMusic, Review
from fuzzywuzzy import fuzz


# ====================== ❤️ ЛАЙК СИСТЕМАСЫ (SESSION МЕНЕН) ======================

# --- ТОПТОМДОР ҮЧҮН ЛАЙК (Home/Price баракчалары үчүн) ---
def toggle_like(request, set_id):
    """
    Бир колдонуучу (сессия) бир топтомго бир эле жолу лайк баса алат.
    Кайра басса - лайк алынат.
    """
    if request.method == "POST":
        product = get_object_or_404(ProductSet, id=set_id)
        # Сессиядан лайк басылган топтомдордун ID тизмесин алабыз
        liked_sets = request.session.get('liked_sets', [])

        if set_id not in liked_sets:
            # Эгер тизмеде жок болсо - кошулат (Лайк)
            liked_sets.append(set_id)
            product.likes += 1
            is_liked = True
        else:
            # Эгер тизмеде бар болсо - өчүрүлөт (Анлайк)
            liked_sets.remove(set_id)
            if product.likes > 0:
                product.likes -= 1
            is_liked = False

        product.save()
        request.session['liked_sets'] = liked_sets
        request.session.modified = True

        # total_likes - бул JavaScript тараптан келген суроого так жооп
        return JsonResponse({
            'status': 'success',
            'total_likes': product.likes,
            'is_liked': is_liked
        })
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


# --- ПИКИРЛЕР ҮЧҮН ЛАЙК (Reviews баракчасы үчүн) ---
def toggle_review_like(request, review_id):
    """
    Пикирлер үчүн өзүнчө сессия тизмеси колдонулат.
    """
    if request.method == "POST":
        review = get_object_or_404(Review, id=review_id)
        liked_reviews = request.session.get('liked_reviews', [])

        if review_id not in liked_reviews:
            liked_reviews.append(review_id)
            review.likes += 1
            is_liked = True
        else:
            liked_reviews.remove(review_id)
            if review.likes > 0:
                review.likes -= 1
            is_liked = False

        review.save()
        request.session['liked_reviews'] = liked_reviews
        request.session.modified = True

        return JsonResponse({
            'status': 'success',
            'total_likes': review.likes,
            'is_liked': is_liked
        })
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


# ====================== 📩 TELEGRAM БИЛДИРҮҮ ЖӨНӨТҮҮ ======================

def send_telegram_message(chat_id, name, phone, message, title="🍓 ЖАҢЫ ЗАКАЗ (SSMOD)"):
    token = settings.TELEGRAM_BOT_TOKEN
    url = f"https://api.telegram.org/bot{token}/sendMessage"

    text = (
        f"*{title}*\n"
        f"━━━━━━━━━━━━━━━\n"
        f"👤 *Кардар:* {name}\n"
        f"📞 *Телефон:* {phone}\n"
        f"━━━━━━━━━━━━━━━\n"
        f"📝 *МААЛЫМАТ:*\n{message}\n"
        f"━━━━━━━━━━━━━━━\n"
        f"⏰ *Убактысы:* {time.strftime('%d.%m.%Y %H:%M:%S')}"
    )

    payload = {'chat_id': chat_id, 'text': text, 'parse_mode': 'Markdown'}

    try:
        response = requests.post(url, data=payload)
        return response.status_code == 200
    except Exception as e:
        print(f"Telegram Message Error: {e}")
        return False


# ====================== 📥 ЗАКАЗ КАБЫЛ АЛУУ ======================

def submit_order(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            name = data.get('name', 'Жазылган эмес')
            phone = data.get('phone', 'Жазылган эмес')
            product_title = data.get('product', 'Белгисиз топтом')
            total = data.get('total', '0 сом')
            address = data.get('address', 'Маалымат жок')
            payment_method = data.get('payment_method', 'Накталай')
            is_delivery = data.get('is_delivery', True)
            note = data.get('note', '')

            admin_details = (
                f"🎁 *Топтом:* {product_title}\n"
                f"💰 *Жалпы сумма:* {total}\n"
                f"💳 *Төлөм ыкмасы:* {payment_method}\n"
                f"🚚 *Жеткирүү:* {'Доставка' if is_delivery else 'Өзүм келем'}\n"
                f"📍 *Дарек/Убакыт:* {address}\n"
                f"📝 *Кошумча:* {note}"
            )

            # Админге жөнөтүү
            send_telegram_message(settings.TELEGRAM_CHAT_ID, name, phone, admin_details)

            # Эгер доставка болсо, курьерге жөнөтүү
            if is_delivery:
                courier_id = getattr(settings, 'DELIVERY_USER_CHAT_ID', None)
                if courier_id:
                    courier_details = (
                        f"📦 *Заказ:* {product_title}\n"
                        f"📍 *Дареги:* {address}\n"
                        f"📱 *Кардар телефону:* {phone}\n"
                        f"💰 *Алынуучу сумма:* {total}"
                    )
                    send_telegram_message(courier_id, name, phone, courier_details, title="🚚 КУРЬЕРГЕ ТАПШЫРМА")

            return JsonResponse({'status': 'success', 'message': 'Заказыңыз кабыл алынды! 🍓'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


# ====================== 💬 ПИКИРЛЕРДИ БАШКАРУУ ======================

def reviews(request):
    if request.method == "POST":
        try:
            name = request.POST.get('userName')
            message = request.POST.get('userMsg')
            stars = request.POST.get('stars', 5)

            if name and message:
                Review.objects.create(name=name, message=message, stars=int(stars))
                return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    all_reviews = Review.objects.all().order_by('-created_at')
    active_music = BackgroundMusic.objects.filter(is_active=True).first()

    # ПИКИРЛЕР үчүн лайк басылган IDлерди сессиядан алабыз
    liked_reviews = request.session.get('liked_reviews', [])

    return render(request, 'shop/reviews.html', {
        'reviews': all_reviews,
        'active_music': active_music,
        'liked_reviews': liked_reviews
    })


def delete_review(request, review_id):
    if request.method == "POST":
        review = get_object_or_404(Review, id=review_id)
        review.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)


# ====================== 🤖 AI ЧАТ ======================

def strawberry_chat_api(request):
    user_query = request.GET.get('message') or request.POST.get('message', '')
    user_query = user_query.lower().strip()

    if not user_query:
        return JsonResponse({'reply': "Салам! 🍓 Мен SSMOD жардамчысымын."})

    knowledge_base = {
        "саламдашуу": {"keywords": ["салам", "привет", "hello", "саламатсызбы"],
                       "reply": "Саламатсызбы! 😊 Сизге жардам керекпи?"},
        "баалар": {"keywords": ["баа", "канча", "сом", "цена"], "reply": "Топтомдор 800 сомдон башталат. 💸"},
        "жеткирүү": {"keywords": ["жеткирүү", "доставка", "курьер"],
                     "reply": "Ош шаары ичинде жеткирүү бар. 🚚 Акысы 100-150 сом."},
        "дарек": {"keywords": ["кайда", "адрес", "локация"],
                  "reply": "Биз Ош шаарындабыз. 📍 Так дарек 'Байланыш' бөлүмүндө."}
    }

    # Түз дал келүү (Direct match)
    for category in knowledge_base.values():
        for keyword in category["keywords"]:
            if keyword in user_query:
                return JsonResponse({'reply': category["reply"]})

    # Окшоштукту текшерүү (Fuzzy match)
    best_match = None
    highest_score = 0
    for category in knowledge_base.values():
        for keyword in category["keywords"]:
            score = fuzz.partial_ratio(user_query, keyword)
            if score > highest_score:
                highest_score = score
                best_match = category["reply"]

    reply = best_match if highest_score > 65 else "Кечириңиз, түшүнбөй калдым. Операторго жазып көрүңүзчү 😊"
    return JsonResponse({'reply': reply})


# ====================== 📄 БАРАКЧАЛАР ======================

def home(request):
    active_music = BackgroundMusic.objects.filter(is_active=True).first()
    # Эң көп лайк алган 6 топтомду чыгаруу
    products = ProductSet.objects.all().order_by('-likes', '-id')[:6]
    liked_sets = request.session.get('liked_sets', [])

    return render(request, 'shop/index.html', {
        'products': products,
        'active_music': active_music,
        'liked_sets': liked_sets
    })


def price(request):
    active_music = BackgroundMusic.objects.filter(is_active=True).first()
    # Баардык топтомдорду баасы боюнча иреттөө
    sets = ProductSet.objects.all().order_by('-likes', 'price')
    liked_sets = request.session.get('liked_sets', [])

    return render(request, 'shop/price.html', {
        'sets': sets,
        'active_music': active_music,
        'liked_sets': liked_sets
    })


def about(request):
    active_music = BackgroundMusic.objects.filter(is_active=True).first()
    return render(request, 'shop/about.html', {'active_music': active_music})


def contact(request):
    active_music = BackgroundMusic.objects.filter(is_active=True).first()
    return render(request, 'shop/contact.html', {'active_music': active_music})


def page_not_found(request, exception):
    return render(request, 'shop/404.html', status=404)