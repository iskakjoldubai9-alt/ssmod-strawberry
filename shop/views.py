import json
import time
import requests
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.conf import settings
from .models import ProductSet, BackgroundMusic, Review
from fuzzywuzzy import fuzz


# ====================== ❤️ ЛАЙК СИСТЕМАСЫ (SESSION МЕНЕН) ======================

def toggle_like(request, set_id):
    """ Бир колдонуучу бир топтомго бир эле жолу лайк баса алат. """
    if request.method == "POST":
        product = get_object_or_404(ProductSet, id=set_id)
        liked_sets = request.session.get('liked_sets', [])

        if set_id not in liked_sets:
            liked_sets.append(set_id)
            product.likes += 1
            is_liked = True
        else:
            liked_sets.remove(set_id)
            if product.likes > 0:
                product.likes -= 1
            is_liked = False

        product.save()
        request.session['liked_sets'] = liked_sets
        request.session.modified = True

        return JsonResponse({
            'status': 'success',
            'total_likes': product.likes,
            'is_liked': is_liked
        })
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


def toggle_review_like(request, review_id):
    """ Пикирлер үчүн өзүнчө сессия тизмеси колдонулат. """
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


def send_telegram_photo(chat_id, photo, caption):
    """ Сүрөт менен бирге пикирди Telegram'га жөнөтүү """
    token = settings.TELEGRAM_BOT_TOKEN
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    try:
        files = {'photo': photo}
        data = {'chat_id': chat_id, 'caption': caption, 'parse_mode': 'Markdown'}
        requests.post(url, files=files, data=data)
    except Exception as e:
        print(f"Telegram Photo Error: {e}")


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

            send_telegram_message(settings.TELEGRAM_CHAT_ID, name, phone, admin_details)

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


# ====================== 💬 ПИКИРЛЕРДИ БАШКАРУУ (ӨЗҮНҮКҮН ГАНА ӨЧҮРҮҮ) ======================

def reviews(request):
    if request.method == "POST":
        try:
            name = request.POST.get('userName')
            message = request.POST.get('userMsg')
            stars = request.POST.get('stars', 5)
            image = request.FILES.get('reviewImage')

            if name and message:
                # 1. Жаңы пикирди базага сактоо
                new_review = Review.objects.create(
                    name=name,
                    message=message,
                    stars=int(stars),
                    image=image
                )

                # 2. Сессияга бул пикирдин IDсин кошуу (өчүрө алуу үчүн)
                my_reviews = request.session.get('my_reviews', [])
                my_reviews.append(new_review.id)
                request.session['my_reviews'] = my_reviews
                request.session.modified = True

                # 3. Telegram билдирүү
                tg_msg = f"💬 *ЖАҢЫ ПИКИР*\n👤 *Кардар:* {name}\n⭐ *Рейтинг:* {stars} жылдыз\n📝 *Текст:* {message}"
                if image:
                    send_telegram_photo(settings.TELEGRAM_CHAT_ID, image, tg_msg)
                else:
                    send_telegram_message(settings.TELEGRAM_CHAT_ID, name, "Пикир калтырды", tg_msg,
                                          title="💬 ЖАҢЫ ПИКИР")

                return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    # Бетти жүктөөдө маалыматтарды алуу
    all_reviews = Review.objects.all().order_by('-created_at')
    active_music = BackgroundMusic.objects.filter(is_active=True).first()

    # Сессиядан өзүнүн пикирлеринин жана лайктарынын тизмесин алуу
    my_reviews = request.session.get('my_reviews', [])
    liked_reviews = request.session.get('liked_reviews', [])

    return render(request, 'shop/reviews.html', {
        'reviews': all_reviews,
        'active_music': active_music,
        'my_reviews': my_reviews,
        'liked_reviews': liked_reviews
    })


def delete_review(request, review_id):
    if request.method == "POST":
        # Сессиядан текшерүү: бул пикир чын эле ушул кишиникиби?
        my_reviews = request.session.get('my_reviews', [])

        if review_id in my_reviews:
            review = get_object_or_404(Review, id=review_id)
            review.delete()
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)

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

    reply = best_match if highest_score > 65 else "Кечириңиз, түшүнбөй калдым. Операторго жазып көрүңүзчү 😊"
    return JsonResponse({'reply': reply})


# ====================== 📄 БАРАКЧАЛАР ======================

def home(request):
    active_music = BackgroundMusic.objects.filter(is_active=True).first()
    products = ProductSet.objects.all().order_by('-likes', '-id')[:6]
    liked_sets = request.session.get('liked_sets', [])

    return render(request, 'shop/index.html', {
        'products': products,
        'active_music': active_music,
        'liked_sets': liked_sets
    })


def price(request):
    active_music = BackgroundMusic.objects.filter(is_active=True).first()
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


# ====================== ⚠️ КАТА БАРАКЧАЛАРЫ ======================

def custom_page_not_found(request, exception):
    """ 404 катасы (бет табылган жок) """
    active_music = BackgroundMusic.objects.filter(is_active=True).first()
    return render(request, 'shop/404.html', {'active_music': active_music}, status=404)


def custom_server_error(request):
    """ 500 катасы (сервердик ката) """
    return render(request, 'shop/500.html', status=500)


# ====================== 🛒 КОРЗИНА ЛОГИКАСЫ ======================

# ====================== 🛒 КОРЗИНА ЛОГИКАСЫ ======================

# Башка импорттордун жанына кошуңуз
from django.contrib.auth.decorators import login_required

def cart_add(request, product_id):
    # 1. Сөзсүз түрдө эң башында текшеребиз:
    if not request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'must_login',
                'message': 'Товар кошуу үчүн алгач катталыңыз! 🍓'
            })
        return redirect('login')

    # 2. Эгер колдонуучу кирген болсо, төмөнкү код иштейт:
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)

    if product_id_str in cart:
        cart[product_id_str] += 1
    else:
        cart[product_id_str] = 1

    request.session['cart'] = cart
    request.session.modified = True

    # AJAX суроосу үчүн жооп
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'ok', 'cart_count': sum(cart.values())})

    # Жөнөкөй баскыч болсо
    return redirect(request.META.get('HTTP_REFERER', 'price'))

def cart_detail(request):
    """ Корзинадагы товарлардын тизмесин көрсөтүү """
    active_music = BackgroundMusic.objects.filter(is_active=True).first()
    cart = request.session.get('cart', {})

    cart_items = []
    total_price = 0

    # Сессиядагы IDлер боюнча базадан товарларды алуу
    for product_id, quantity in cart.items():
        try:
            product = get_object_or_404(ProductSet, id=int(product_id))
            item_total = product.price * quantity
            total_price += item_total
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'item_total': item_total,
            })
        except:
            # Эгер товар базадан өчүп кетсе, сессиядан да тазалап коюу үчүн
            continue

    return render(request, 'shop/cart_detail.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'active_music': active_music,
    })


def cart_remove(request, product_id):
    """ Товарды корзинадан өчүрүү """
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)

    if product_id_str in cart:
        del cart[product_id_str]
        request.session['cart'] = cart
        request.session.modified = True

    # Өчүргөндөн кийин кайра корзина барагына кайтат
    return redirect('cart_detail')

