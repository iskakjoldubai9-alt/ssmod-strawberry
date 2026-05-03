import json
import random
import requests
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from shop.models import ProductSet, Review

User = get_user_model()


# ====================== 🛠 УНИВЕРСАЛДУУ ФУНКЦИЯ ======================

def send_telegram_message(token, chat_id, name, phone, message, title="🍓 БИЛДИРҮҮ"):
    """ Текстти тиешелүү ботко жөнөтүүчү функция """
    if not token or not chat_id:
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    text = (
        f"*{title}*\n"
        f"━━━━━━━━━━━━━━━\n"
        f"👤 Аты: {name}\n"
        f"📞 Тел: {phone}\n"
        f"━━━━━━━━━━━━━━━\n"
        f"{message}"
    )
    try:
        response = requests.post(url, data={'chat_id': chat_id, 'text': text, 'parse_mode': 'Markdown'}, timeout=5)
        return response.ok
    except Exception as e:
        print(f"Telegram Error: {e}")
        return False


# ====================== 🔐 КИРҮҮ ЖАНА КАТТАЛУУ ======================

def login_view(request):
    """ SUPPORT_BOT аркылуу тастыктоо кодун жөнөтүү жана кирүү """
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        code = request.POST.get('code')

        # 1-КАДАМ: Кодду жаратуу жана жөнөтүү
        if name and phone and not code:
            generated_code = str(random.randint(100000, 999999))
            request.session['verification_code'] = generated_code
            request.session['user_phone'] = phone
            request.session['user_name'] = name

            msg = f"🔑 Сиздин кирүү кодуңуз: `{generated_code}`"
            send_telegram_message(
                settings.SUPPORT_BOT_TOKEN,
                settings.SUPPORT_CHAT_ID,
                name, phone, msg,
                title="🔐 SSMOD ТАСТЫКТОО"
            )
            return JsonResponse({'status': 'code_sent'})

        # 2-КАДАМ: Кодду текшерүү
        elif code:
            if code == request.session.get('verification_code'):
                # Колдонуучуну телефон номери аркылуу табуу же түзүү
                user, created = User.objects.get_or_create(username=request.session.get('user_phone'))
                if created or not user.first_name:
                    user.first_name = request.session.get('user_name')
                    user.save()

                login(request, user)
                # Сессияны тазалоо
                request.session.pop('verification_code', None)
                return JsonResponse({'status': 'success'})

            return JsonResponse({'status': 'error', 'message': 'Код туура эмес!'})

    return render(request, 'accounts/login.html')


def logout_view(request):
    """ Системадан чыгуу """
    logout(request)
    return redirect('home')


# ====================== 👤 ПРОФИЛЬ (СЕБЕТ МЕНЕН) ======================

@login_required
def profile_view(request):
    """ Колдонуучунун жеке кабинети жана себеттеги товарлары """
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0

    for p_id, qty in cart.items():
        try:
            product = ProductSet.objects.get(id=int(p_id))
            item_total = product.price * qty
            total_price += item_total
            cart_items.append({
                'product': product,
                'quantity': qty,
                'item_total': item_total
            })
        except ProductSet.DoesNotExist:
            continue

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
    }
    return render(request, 'accounts/profile.html', context)


# ====================== 📥 ЗАКАЗ ЖӨНӨТҮҮ ======================

def submit_order(request):
    """ Заказды Админге жана Курьерге жөнөтүү """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            name = data.get('name', 'Аты жок')
            phone = data.get('phone', 'Тел жок')
            product_title = data.get('product', 'Топтом белгисиз')
            total = data.get('total', '0 сом')
            address = data.get('address', 'Дарек жок')
            is_delivery = data.get('is_delivery', True)

            details = f"🎁 Топтом: {product_title}\n💰 Сумма: {total}\n📍 Дарек: {address}"

            # 1. Админге жөнөтүү
            send_telegram_message(
                settings.ADMIN_BOT_TOKEN,
                settings.ADMIN_CHAT_ID,
                name, phone, details,
                title="🍓 ЖАҢЫ ЗАКАЗ"
            )

            # 2. Курьерге жөнөтүү (эгер доставка болсо)
            if is_delivery:
                send_telegram_message(
                    settings.DELIVERY_BOT_TOKEN,
                    settings.DELIVERY_CHAT_ID,
                    name, phone, details,
                    title="🚚 КУРЬЕРГЕ ТАПШЫРМА"
                )

            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


# ====================== 💬 ПИКИРЛЕР ======================

def reviews(request):
    """ Пикирлерди кабыл алуу жана Админге билдирүү """
    if request.method == "POST":
        name = request.POST.get('userName')
        message = request.POST.get('userMsg')
        stars = request.POST.get('stars', 5)

        if name and message:
            Review.objects.create(name=name, message=message, stars=int(stars))

            # Пикирди админ гана көрөт
            review_text = f"⭐ Жылдыз: {stars}\n📝 Пикир: {message}"
            send_telegram_message(
                settings.ADMIN_BOT_TOKEN,
                settings.ADMIN_CHAT_ID,
                name, "Жаңы пикир",
                review_text,
                title="💬 ПИКИР КАЛТЫРЫЛДЫ"
            )
            return JsonResponse({'status': 'success'})

    all_reviews = Review.objects.all().order_by('-created_at')
    return render(request, 'shop/reviews.html', {'reviews': all_reviews})