import telebot
from database import create_database, save_profile, get_profile

bot = telebot.TeleBot('8828680279:AAEsEpHy81gpuHXlFz6Pzwe0rmV7-6sU1E8')

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
    # Следующее сообщение пользователя будет его именем
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


bot.infinity_polling()