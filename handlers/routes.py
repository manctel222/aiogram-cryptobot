import aiohttp
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup   
    )
from forms.user import Form
from aiogram.fsm.context import FSMContext
from bases.database import save_user, add_alarm

router = Router()

@router.message(Command("start"))
async def start(message: Message, state: FSMContext):
    await message.answer("Давайте начнем заполнять вашу анкету\nСначала введите ваше имя:")
    await state.set_state(Form.name)

@router.message(Command("cancel"))
@router.message(F.text.casefold() == "отмена")
async def cancel_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("Нет активных опросов для отмены.")
        return

    await state.clear()
    await message.answer("Заполнение анкеты отменено.")

@router.message(Form.name, F.text)
async def get_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Хорошо!\nТеперь введите ваш возраст:")
    await state.set_state(Form.age)
    
@router.message(Form.age, F.text)
async def get_age(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Возраст должен быть числом")
        return
    if int(message.text) < 1 or int(message.text) > 100:
        await message.answer("Введите свой настоящий возраст!")
        return

    await state.update_data(age=int(message.text))
    await message.answer("Хорошо!\nТеперь введите вашу почту:")
    await state.set_state(Form.email)

@router.message(Form.email, F.text)
async def get_email(message: Message, state: FSMContext):
    email_text = message.text.strip()
    if "@" not in email_text or email_text.count("@") != 1:
        await message.answer('В почте должен быть один знак "@"!')
        return
    username, domain = email_text.split("@")

    if len(username) == 0 or len(domain) == 0:
        await message.answer("В имени и домене почты символов должно быть больше 0 !")
        return
    
    if " " in username or " " in domain:
        await message.answer("В имени или домене почты не должно быть пробелов!")
        return

    if "." not in domain:
        await message.answer("В домене почты должна быть точка!")
        return
    if domain.startswith(".") or domain.endswith("."):
        await message.answer("Домен почты не должен начинаться или заканчиваться на точку!")
        return
    if ".." in domain:
        await message.answer("В домене не должно быть больше 1 точки!")
        return
    
    domain_parts = domain.split(".")
    domain_zone = domain_parts[-1].lower()

    if domain_zone.isdigit():
        await message.answer("Зона домена не должна состоять из цифр!")
        return
    
    en_letters = "abcdefghijklmnopqrstuvwxyz"
    ru_letters = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"

    is_en_zone = all(char in en_letters for char in domain_zone)
    is_ru_zone = all(char in ru_letters for char in domain_zone) 

    if not (is_en_zone or is_ru_zone):
        await message.answer("В зоне домена должны быть русские или английские буквы!")
        return
    
    if len(domain_zone) < 2 or len(domain_zone) > 24:
        await message.answer("Длина доменной зоны должна быть больше 1 и меньше 24")
        return
    
    allowed_chars = (
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
        "0123456789_.-"
    )
    for char in username:
        if char not in allowed_chars:
            await message.answer("Имя почты не должно состоять из запрещенных символов")
            return 
            
    for char in domain:
        if char not in allowed_chars:
            await message.answer("Домен почты не должен состоять из запрещенных символов")
            return

    await state.update_data(email=email_text.lower())
    user_data = await state.get_data()

    save_user(
        user_id=message.from_user.id,
        name=user_data['name'],
        age=user_data['age'],
        email=user_data['email']
    )

    await message.answer(
        f"Успешно! Ваша анкета заполнена:\n\n"
        f"👤 Имя: {user_data['name']}\n"
        f"🔢 Возраст: {user_data['age']}\n"
        f"📧 Почта: {user_data['email']}\n\n"
        f"А теперь настроим ваш личный крипто-будильник!"
    )

    coin_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="BTC (Bitcoin)", callback_data="set_alarm:BTC"),
            InlineKeyboardButton(text="ETH (Ethereum)", callback_data="set_alarm:ETH")
        ]
    ])
    await message.answer("Какую монету отслеживать?", reply_markup=coin_keyboard)


@router.callback_query(F.data.startswith("set_alarm:"))
async def choose_coin_alarm(callback: CallbackQuery, state: FSMContext):
    coin = callback.data.split(":")[-1]
    await state.update_data(chosen_coin=coin)
    
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.coinbase.com/v2/prices/{coin}-USD/spot") as resp:
            data = await resp.json()
            current_price = float(data["data"]["amount"])

    await callback.message.answer(
        f"Текущая цена {coin}: *${current_price:,.2f}*\n\n"
        f"Введите целевую цену в USD, при достижении которой придет уведомление:",
        parse_mode="Markdown"
    )
    await callback.answer()
    await state.set_state(Form.target_price)


@router.message(Form.target_price, F.text)
async def save_alarm_price(message: Message, state: FSMContext):
    try:
        price = float(message.text.replace(",", "."))
        if price <= 0:
            await message.answer("Цена должна быть больше нуля!")
            return
    except ValueError:
        await message.answer("Пожалуйста, введите корректное число")
        return

    data = await state.get_data()
    coin = data["chosen_coin"]

    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.coinbase.com/v2/prices/{coin}-USD/spot") as resp:
            res = await resp.json()
            current_price = float(res["data"]["amount"])

    condition = "above" if price > current_price else "below"
    condition_text = "поднимется выше" if condition == "above" else "упадет ниже"

    add_alarm(message.from_user.id, coin, price, condition)

    await message.answer(
        f"⏰ Будильник успешно заведен!\n"
        f"Я напишу вам, как только *{coin}* {condition_text} *${price:,.2f}*.",
        parse_mode="Markdown"
    )
    await state.clear()
