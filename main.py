import telebot

bot = telebot.TeleBot('8828680279:AAEsEpHy81gpuHXlFz6Pzwe0rmV7-6sU1E8')

# Здесь временно храним анкеты пользователей
# Формат:
# user_id: {
#     "name": "...",
#     "language": "...",
#     "interests": "...",
#     "course": "...",
#     "institute": "..."
# }
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
    profiles[user_id] = user_data[user_id]
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
    # Проверяем, есть ли анкета
    if user_id not in profiles:
        bot.send_message(
            message.chat.id,
            "У тебя пока нет анкеты.\n"
            "Создать её можно с помощью команды /start"
        )
        return
    profile = profiles[user_id]
    text = (
        "👤 ТВОЯ АНКЕТА\n\n"
        f"Имя: {profile['name']}\n"
        f"Язык программирования: {profile['language']}\n"
        f"Интересы: {profile['interests']}\n"
        f"Курс: {profile['course']}\n"
        f"Институт: {profile['institute']}"
    )
    bot.send_message(message.chat.id, text)


bot.infinity_polling()