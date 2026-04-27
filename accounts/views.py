import random
import requests
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
# Товарлар моделиңизди импорттоңуз
from shop.models import ProductSet

User = get_user_model()

def login_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        code = request.POST.get('code')

        # 1-КАДАМ: Аты жана номери келгенде код жөнөтүү
        if name and phone and not code:
            generated_code = str(random.randint(100000, 999999))
            request.session['verification_code'] = generated_code
            request.session['user_phone'] = phone
            request.session['user_name'] = name  # Атын сессияга сактап турабыз

            # Telegram'га жөнөтүү
            token = settings.TELEGRAM_BOT_TOKEN
            chat_id = settings.TELEGRAM_CHAT_ID
            message = f"🍓 ЖАҢЫ КИРҮҮ\n👤 Аты: {name}\n📞 Номер: {phone}\n🔐 КОД: {generated_code}"
            url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message}"

            try:
                # timeout кошулду, сайт катып калбашы үчүн
                requests.get(url, timeout=5)
            except:
                pass

            return JsonResponse({'status': 'code_sent'})

        # 2-КАДАМ: Кодду текшерүү жана каттоо/кирүү
        elif code:
            saved_code = request.session.get('verification_code')
            phone = request.session.get('user_phone')
            name = request.session.get('user_name')

            if code == saved_code:
                # Колдонуучу жок болсо түзөт, бар болсо атын жаңылайт
                user, created = User.objects.get_or_create(username=phone)
                user.first_name = name
                user.save()

                login(request, user)
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Код туура эмес!'})

    return render(request, 'accounts/login.html')

@login_required
def profile_view(request):
    """
    Кардардын жеке кабинети: Аты-жөнү, номери жана тандаган товарлары (корзинасы)
    """
    # Сессиядагы корзинаны алуу
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0

    # Корзинадагы товарларды базадан алуу
    for product_id, quantity in cart.items():
        try:
            product = ProductSet.objects.get(id=int(product_id))
            item_total = product.price * quantity
            total_price += item_total
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'item_total': item_total,
            })
        except ProductSet.DoesNotExist:
            continue

    context = {
        'user': request.user,
        'cart_items': cart_items,
        'total_price': total_price,
        'items_count': len(cart_items),
    }
    return render(request, 'accounts/profile.html', context)

def logout_view(request):
    logout(request)
    return redirect('login')