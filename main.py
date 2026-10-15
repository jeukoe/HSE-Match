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
bot = telebot.TeleBot("8828680279:AAEsEpHy81gpuHXlFz6Pzwe0rmV7-6sU1E8")

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
    keyboard.row(
        types.KeyboardButton("👤 Моя анкета"),
        types.KeyboardButton("✏️ Изменить анкету")
    )
    keyboard.add(
        types.KeyboardButton("🗑 Удалить анкету")
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


@bot.message_handler(
    func=lambda message:
    message.text == "✏️ Изменить анкету"
)
def edit_button(message):
    if get_profile(message.from_user.id) is None:
        bot.send_message(
            message.chat.id,
            "Сначала создай анкету через /start."
        )
        return

    edit_profile(message)



@bot.message_handler(commands=["edit"])
def edit_profile(message):
    keyboard = types.InlineKeyboardMarkup(row_width=2)

    buttons = [
        types.InlineKeyboardButton("👤 Имя", callback_data="edit_name"),
        types.InlineKeyboardButton("🛠 Навыки", callback_data="edit_skills"),
        types.InlineKeyboardButton("🎯 Интересы", callback_data="edit_interests"),
        types.InlineKeyboardButton("🎓 Курс", callback_data="edit_course"),
        types.InlineKeyboardButton("🏫 Институт", callback_data="edit_institute"),
        types.InlineKeyboardButton("👥 Роль в команде", callback_data="edit_role"),
        types.InlineKeyboardButton("🚀 Цель поиска команды", callback_data="edit_goal"),
        types.InlineKeyboardButton("⏰ Свободное время", callback_data="edit_free_time"),
        types.InlineKeyboardButton("📝 О себе", callback_data="edit_about")
    ]

    keyboard.add(*buttons)

    bot.send_message(
        message.chat.id,
        "✏️ Что ты хочешь изменить?",
        reply_markup=keyboard
    )


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("edit_")
)
def edit_callback(call):
    bot.answer_callback_query(call.id)

    fields = {
        "edit_name": (
            "Напиши новое имя:",
            change_name
        ),
        "edit_skills": (
            "Напиши новые навыки:",
            change_skills
        ),
        "edit_interests": (
            "Напиши свои новые интересы:",
            change_interests
        ),
        "edit_course": (
            "Напиши свой курс:",
            change_course
        ),
        "edit_institute": (
            "Напиши свой институт:",
            change_institute
        ),
        "edit_role": (
            "Напиши новую роль в команде:",
            change_role
        ),
        "edit_goal": (
            "Напиши новую цель поиска команды:",
            change_goal
        ),
        "edit_free_time": (
            "Напиши, сколько времени готов(а) уделять проекту:",
            change_free_time
        ),
        "edit_about": (
            "Напиши новую информацию о себе:",
            change_about
        )
    }

    field = fields.get(call.data)

    if field:
        prompt, handler = field

        sent = bot.send_message(
            call.message.chat.id,
            prompt,
            reply_markup=types.ReplyKeyboardRemove()
        )
        bot.register_next_step_handler(sent, handler)


def change_name(message):
    new_value = message.text
    update_name(message.from_user.id, new_value)

    bot.send_message(
        message.chat.id,
        f"✅ Имя изменено на: {new_value}",
        reply_markup=main_menu_keyboard()
    )


def change_skills(message):
    new_value = message.text
    update_skills(message.from_user.id, new_value)

    bot.send_message(
        message.chat.id,
        f"✅ Навыки изменены: {new_value}",
        reply_markup=main_menu_keyboard()
    )


def change_interests(message):
    new_value = message.text
    update_interests(message.from_user.id, new_value)

    bot.send_message(
        message.chat.id,
        f"✅ Интересы изменены на: {new_value}",
        reply_markup=main_menu_keyboard()
    )


def change_course(message):
    new_value = message.text
    update_course(message.from_user.id, new_value)

    bot.send_message(
        message.chat.id,
        f"✅ Курс изменён на: {new_value}",
        reply_markup=main_menu_keyboard()
    )


def change_institute(message):
    new_value = message.text
    update_institute(message.from_user.id, new_value)

    bot.send_message(
        message.chat.id,
        f"✅ Институт изменён на: {new_value}",
        reply_markup=main_menu_keyboard()
    )


def change_role(message):
    new_value = message.text
    update_role(message.from_user.id, new_value)

    bot.send_message(
        message.chat.id,
        f"✅ Роль в команде изменена на: {new_value}",
        reply_markup=main_menu_keyboard()
    )


def change_goal(message):
    new_value = message.text
    update_goal(message.from_user.id, new_value)

    bot.send_message(
        message.chat.id,
        f"✅ Цель поиска команды изменена на: {new_value}",
        reply_markup=main_menu_keyboard()
    )


def change_free_time(message):
    new_value = message.text
    update_free_time(message.from_user.id, new_value)

    bot.send_message(
        message.chat.id,
        f"✅ Свободное время изменено на: {new_value}",
        reply_markup=main_menu_keyboard()
    )


def change_about(message):
    new_value = message.text
    update_about(message.from_user.id, new_value)

    bot.send_message(
        message.chat.id,
        "✅ Информация о себе обновлена.",
        reply_markup=main_menu_keyboard()
    )


@bot.message_handler(
    func=lambda message:
    message.text == "🗑 Удалить анкету"
)
def delete_profile_button(message):
    if get_profile(message.from_user.id) is None:
        bot.send_message(
            message.chat.id,
            "У тебя нет анкеты для удаления.",
            reply_markup=main_menu_keyboard()
        )
        return

    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(
        types.InlineKeyboardButton(
            "✅ Да, удалить",
            callback_data="confirm_delete"
        ),
        types.InlineKeyboardButton(
            "❌ Отмена",
            callback_data="cancel_delete"
        )
    )

    bot.send_message(
        message.chat.id,
        "⚠️ <b>Удалить анкету?</b>\n\n"
        "Все данные анкеты будут удалены. "
        "Это действие нельзя отменить.",
        parse_mode="HTML",
        reply_markup=keyboard
    )


@bot.callback_query_handler(
    func=lambda call: call.data in [
        "confirm_delete",
        "cancel_delete"
    ]
)
def delete_profile_callback(call):
    bot.answer_callback_query(call.id)

    if call.data == "cancel_delete":
        bot.send_message(
            call.message.chat.id,
            "Удаление отменено. Твоя анкета сохранена.",
            reply_markup=main_menu_keyboard()
        )
        return

    user_id = call.from_user.id

    import sqlite3

    connection = sqlite3.connect("profiles.db")
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM profiles WHERE user_id = ?",
        (user_id,)
    )

    connection.commit()
    connection.close()

    user_data.pop(user_id, None)

    bot.send_message(
        call.message.chat.id,
        "🗑 Анкета удалена.\n\n"
        "Если захочешь вернуться, создай новую анкету!",
        reply_markup=registration_keyboard()
    )


bot.infinity_polling()