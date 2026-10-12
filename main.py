import telebot
from telebot import types

from database import (
    create_database,
    save_profile,
    get_profile,
    update_name,
    update_skills,
    update_interests,
    update_course,
    update_institute,
    update_role,
    update_goal,
    update_free_time,
    update_about
)
bot = telebot.TeleBot("8828680279:AAEsEpHy81gpuHXlFz6Pzwe0rmV7-6sU1E8'")

create_database()

user_data = {}


def registration_keyboard():
    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )
    keyboard.add(
        types.KeyboardButton("📝 Зарегистрироваться")
    )
    return keyboard


def main_menu_keyboard():
    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )
    keyboard.add(
        types.KeyboardButton("👤 Моя анкета")
    )
    return keyboard


@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id

    if get_profile(user_id) is not None:
        bot.send_message(
            message.chat.id,
            "С возвращением! Выбери действие:",
            reply_markup=main_menu_keyboard()
        )
    else:
        bot.send_message(
            message.chat.id,
            "👋 Привет! Добро пожаловать в TeamUp!\n\n"
            "🤝 Этот бот поможет тебе найти единомышленников "
            "для учебных и IT-проектов.\n\n"
            "📝 Создай свою анкету, укажи навыки, интересы "
            "и направление обучения.\n\n"
            "✏️ Ты сможешь просматривать и изменять анкету.\n\n"
            "Нажми кнопку ниже, чтобы начать!",
            reply_markup=registration_keyboard()
        )


@bot.message_handler(
    func=lambda message:
    message.text == "📝 Зарегистрироваться"
)
def registration_button(message):
    user_id = message.from_user.id

    if get_profile(user_id) is not None:
        bot.send_message(
            message.chat.id,
            "У тебя уже есть анкета.",
            reply_markup=main_menu_keyboard()
        )
        return

    user_data[user_id] = {}

    sent = bot.send_message(
        message.chat.id,
        "Как тебя зовут?",
        reply_markup=types.ReplyKeyboardRemove()
    )
    bot.register_next_step_handler(sent, get_name)


def get_name(message):
    user_id = message.from_user.id
    user_data[user_id]["name"] = message.text

    sent = bot.send_message(
        message.chat.id,
        "Отлично! Теперь напиши, какими навыками ты обладаешь.\n"
        "Например: Python, C++, HTML, CSS, дизайн."
    )
    bot.register_next_step_handler(sent, get_skills)


def get_skills(message):
    user_id = message.from_user.id
    user_data[user_id]["skills"] = message.text

    sent = bot.send_message(
        message.chat.id,
        "Какие у тебя интересы?\n"
        "Например: AI, Data Science, игры, веб-разработка."
    )
    bot.register_next_step_handler(sent, get_interests)


def get_interests(message):
    user_id = message.from_user.id
    user_data[user_id]["interests"] = message.text

    sent = bot.send_message(
        message.chat.id,
        "На каком ты курсе?"
    )
    bot.register_next_step_handler(sent, get_course)


def get_course(message):
    user_id = message.from_user.id
    user_data[user_id]["course"] = message.text

    sent = bot.send_message(
        message.chat.id,
        "В каком институте / университете ты учишься?"
    )
    bot.register_next_step_handler(sent, get_institute)


def get_institute(message):
    user_id = message.from_user.id
    user_data[user_id]["institute"] = message.text

    sent = bot.send_message(
        message.chat.id,
        "Какую роль ты хочешь выполнять в команде?\n"
        "Например: разработчик, дизайнер, аналитик."
    )
    bot.register_next_step_handler(sent, get_role)


def get_role(message):
    user_id = message.from_user.id
    user_data[user_id]["role"] = message.text

    sent = bot.send_message(
        message.chat.id,
        "Для чего ты ищешь команду?\n"
        "Например: хакатон, учебный проект, стартап."
    )
    bot.register_next_step_handler(sent, get_goal)


def get_goal(message):
    user_id = message.from_user.id
    user_data[user_id]["goal"] = message.text

    sent = bot.send_message(
        message.chat.id,
        "Сколько времени ты готов(а) уделять проекту?\n"
        "Например: несколько часов в неделю."
    )
    bot.register_next_step_handler(sent, get_free_time)


def get_free_time(message):
    user_id = message.from_user.id
    user_data[user_id]["free_time"] = message.text

    sent = bot.send_message(
        message.chat.id,
        "Расскажи немного о себе. Что тебе интересно "
        "и чему ты хочешь научиться?"
    )
    bot.register_next_step_handler(sent, get_about)


def get_about(message):
    user_id = message.from_user.id
    user_data[user_id]["about"] = message.text

    profile = user_data[user_id]

    save_profile(
        user_id,
        profile["name"],
        profile["interests"],
        profile["course"],
        profile["institute"],
        profile["skills"],
        profile["role"],
        profile["goal"],
        profile["free_time"],
        profile["about"]
    )

    del user_data[user_id]

    bot.send_message(
        message.chat.id,
        "✅ Анкета создана!\n\nВыбери действие:",
        reply_markup=main_menu_keyboard()
    )


@bot.message_handler(
    func=lambda message: message.text == "👤 Моя анкета"
)
def profile_button(message):
    show_profile(message)


@bot.message_handler(commands=["profile"])
def show_profile(message):
    user_id = message.from_user.id
    profile = get_profile(user_id)

    if profile is None:
        bot.send_message(
            message.chat.id,
            "📝 У тебя пока нет анкеты.\n"
            "Создай её через главное меню.",
            reply_markup=registration_keyboard()
        )
        return

    (
        name, interests, course, institute, skills,
        role, goal, free_time, about
    ) = profile

    text = (
        "✨ <b>МОЯ АНКЕТА</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"👤 <b>{name}</b>\n"
        "<i>Участник TeamUp</i>\n\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "🛠 <b>НАВЫКИ</b>\n"
        f"{skills or 'Не указаны'}\n\n"
        "🎯 <b>ИНТЕРЕСЫ</b>\n"
        f"{interests or 'Не указаны'}\n\n"
        "👥 <b>РОЛЬ В КОМАНДЕ</b>\n"
        f"{role or 'Не указана'}\n\n"
        "🚀 <b>ЦЕЛЬ ПОИСКА КОМАНДЫ</b>\n"
        f"{goal or 'Не указана'}\n\n"
        "⏰ <b>СВОБОДНОЕ ВРЕМЯ</b>\n"
        f"{free_time or 'Не указано'}\n\n"
        "📝 <b>О СЕБЕ</b>\n"
        f"{about or 'Не указано'}\n\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "🎓 <b>ОБУЧЕНИЕ</b>\n"
        f"📚 Курс: {course or 'Не указан'}\n"
        f"🏛 Институт: {institute or 'Не указан'}\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "🚀 <i>Ищем единомышленников и создаём проекты!</i>"
    )

    bot.send_message(
        message.chat.id,
        text,
        parse_mode="HTML",
        reply_markup=main_menu_keyboard()
    )


bot.infinity_polling()

