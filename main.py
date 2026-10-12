import telebot
from telebot import types
from database import (
    create_database,
    save_profile,
    get_profile,
    update_name,
    update_language,
    update_interests,
    update_course,
    update_institute
)

bot = telebot.TeleBot("8828680279:AAEsEpHy81gpuHXlFz6Pzwe0rmV7-6sU1E8'")

create_database()

profiles = {}
# Временные данные пользователя во время заполнения анкеты
user_data = {}

@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    # Создаём временное хранилище для пользователя
    user_data[user_id] = {}
    bot.send_message(
        message.chat.id,
        "Привет! 👋\n"
        "Я помогу тебе создать анкету для поиска участников команды.\n\n"
        "Как тебя зовут?"
    )
    bot.register_next_step_handler(message, get_name)

# Получаем имя
def get_name(message):
    user_id = message.from_user.id
    user_data[user_id]["name"] = message.text
    bot.send_message(
        message.chat.id,
        "Отлично! Теперь напиши, какой язык программирования ты знаешь.\n"
        "Например: Python, C++, Java."
    )
    bot.register_next_step_handler(message, get_language)

# Получаем язык программирования
def get_language(message):
    user_id = message.from_user.id
    user_data[user_id]["language"] = message.text
    bot.send_message(
        message.chat.id,
        "Какие у тебя интересы?\n"
        "Например: AI, Data Science, игры, веб-разработка."
    )
    bot.register_next_step_handler(message, get_interests)

# Получаем интересы
def get_interests(message):
    user_id = message.from_user.id
    user_data[user_id]["interests"] = message.text
    bot.send_message(
        message.chat.id,
        "На каком ты курсе?"
    )
    bot.register_next_step_handler(message, get_course)

# Получаем курс
def get_course(message):
    user_id = message.from_user.id
    user_data[user_id]["course"] = message.text
    bot.send_message(
        message.chat.id,
        "В каком институте / университете ты учишься?"
    )
    bot.register_next_step_handler(message, get_institute)

# Получаем институт и создаём анкету
def get_institute(message):
    user_id = message.from_user.id
    user_data[user_id]["institute"] = message.text
    # Сохраняем готовую анкету
    profile = user_data[user_id]
    save_profile(
        user_id,
        profile["name"],
        profile["language"],
        profile["interests"],
        profile["course"],
        profile["institute"]
    )
    # Удаляем временные данные
    del user_data[user_id]
    bot.send_message(
        message.chat.id,
        "✅ Анкета создана!\n\n"
        "Чтобы посмотреть её, используй команду /profile"
    )

@bot.message_handler(commands=["profile"])
def show_profile(message):
    user_id = message.from_user.id
    profile = get_profile(user_id)

    if profile is None:
        bot.send_message(
            message.chat.id,
            "У тебя пока нет анкеты.\n"
            "Создать её можно с помощью команды /start"
        )
        return

    name, language, interests, course, institute = profile

    text = (
        "👤 ТВОЯ АНКЕТА\n\n"
        f"Имя: {name}\n"
        f"Язык программирования: {language}\n"
        f"Интересы: {interests}\n"
        f"Курс: {course}\n"
        f"Институт: {institute}"
    )
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=["edit"])
def edit_profile(message):
    keyboard = types.InlineKeyboardMarkup()
    button_name = types.InlineKeyboardButton(
        "👤 Имя",
        callback_data="edit_name"
    )
    button_language = types.InlineKeyboardButton(
        "💻 Язык программирования",
        callback_data="edit_language"
    )
    button_interests = types.InlineKeyboardButton(
        "🎯 Интересы",
        callback_data="edit_interests"
    )
    button_course = types.InlineKeyboardButton(
        "🎓 Курс",
        callback_data="edit_course"
    )
    button_institute = types.InlineKeyboardButton(
        "🏫 Институт",
        callback_data="edit_institute"
    )
    keyboard.add(button_name)
    keyboard.add(button_language)
    keyboard.add(button_interests)
    keyboard.add(button_course)
    keyboard.add(button_institute)
    bot.send_message(
        message.chat.id,
        "✏️ Что ты хочешь изменить?",
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("edit_"))
def edit_callback(call):
    bot.answer_callback_query(call.id)
    if call.data == "edit_name":
        bot.send_message(
            call.message.chat.id,
            "Напиши новое имя:"
        )
        bot.register_next_step_handler(call.message, change_name)
    elif call.data == "edit_language":
        bot.send_message(
            call.message.chat.id,
            "Напиши новый язык программирования:"
        )
        bot.register_next_step_handler(call.message, change_language)
    elif call.data == "edit_interests":
        bot.send_message(
            call.message.chat.id,
            "Напиши свои новые интересы:"
        )
        bot.register_next_step_handler(call.message, change_interests)
    elif call.data == "edit_course":
        bot.send_message(
            call.message.chat.id,
            "Напиши свой курс:"
        )
        bot.register_next_step_handler(call.message, change_course)
    elif call.data == "edit_institute":
        bot.send_message(
            call.message.chat.id,
            "Напиши свой институт:"
        )
        bot.register_next_step_handler(call.message, change_institute)

def change_name(message):
    user_id = message.from_user.id
    new_name = message.text
    update_name(user_id, new_name)
    bot.send_message(
        message.chat.id,
        f"✅ Имя изменено на: {new_name}"
    )

def change_language(message):
    user_id = message.from_user.id
    new_language = message.text
    update_language(user_id, new_language)
    bot.send_message(
        message.chat.id,
        f"✅ Язык программирования изменён на: {new_language}"
    )

def change_interests(message):
    user_id = message.from_user.id
    new_interests = message.text
    update_interests(user_id, new_interests)
    bot.send_message(
        message.chat.id,
        f"✅ Интересы изменены на: {new_interests}"
    )

def change_course(message):
    user_id = message.from_user.id
    new_course = message.text
    update_course(user_id, new_course)
    bot.send_message(
        message.chat.id,
        f"✅ Курс изменён на: {new_course}"
    )

def change_institute(message):
    user_id = message.from_user.id
    new_institute = message.text
    update_institute(user_id, new_institute)
    bot.send_message(
        message.chat.id,
        f"✅ Институт изменён на: {new_institute}"
    )

bot.infinity_polling()