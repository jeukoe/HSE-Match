import html
import os

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
    update_about,
    search_profiles,
    get_popular_values
    save_telegram_username,
    get_telegram_username,
    create_contact_request,
    get_contact_request,
    update_contact_request,
    get_accepted_contact_partners
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
        types.KeyboardButton("🔍 Найти участников")
    )
    keyboard.add(
        types.KeyboardButton("🗑 Удалить анкету")
    )
    return keyboard


@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    save_telegram_username(
        user_id,
        message.from_user.username
    )

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


# ---------------------------------------------------------------------------
# Поиск участников и фильтрация
# Все callback_data этого блока начинаются с "search_", чтобы не пересекаться
# с "edit_", "confirm_delete" и "cancel_delete".
# ---------------------------------------------------------------------------

SEARCH_BUTTON = "🔍 Найти участников"

# Тексты кнопок меню: если пользователь нажал их вместо ввода запроса,
# поиск отменяется, а не сохраняет текст кнопки как запрос.
MENU_BUTTONS = {
    "📝 Зарегистрироваться",
    "👤 Моя анкета",
    "✏️ Изменить анкету",
    "🗑 Удалить анкету",
    SEARCH_BUTTON
}

SEARCH_MODES = {
    "search_by_skills": ("skills", "🛠 навыкам", "Python, дизайн"),
    "search_by_interests": ("interests", "🎯 направлениям/интересам", "AI, веб-разработка"),
    "search_by_role": ("role", "👥 роли в команде", "разработчик"),
    "search_by_goal": ("goal", "🚀 цели", "хакатон"),
    "search_by_all": ("all", "🔎 всем полям сразу", "Python, хакатон"),
}

# user_id -> {"results": [...], "field": str, "query": str}
search_state = {}


def search_menu_keyboard():
    keyboard = types.InlineKeyboardMarkup()

    for callback, (_, title, _) in SEARCH_MODES.items():
        keyboard.add(
            types.InlineKeyboardButton(
                f"Искать по {title}",
                callback_data=callback
            )
        )

    keyboard.add(
        types.InlineKeyboardButton(
            "👥 Показать всех участников",
            callback_data="search_everyone"
        )
    )
    return keyboard


def short(text, limit=300):
    text = text or ""
    return text if len(text) <= limit else text[:limit].rstrip() + "…"


def esc(text, default="—"):
    # Текст пользователей вставляется в HTML-сообщение, поэтому экранируем.
    return html.escape(short(text)) if text else default


def format_result(profile, position, total):
    match_line = ""
    if profile["total"]:
        match_line = (
            f"✅ Совпадений: {profile['matched']} из {profile['total']}\n\n"
        )

    return (
        f"🔍 <b>Результат {position + 1} из {total}</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"👤 <b>{esc(profile['name'])}</b>\n"
        f"{match_line}"
        f"🛠 <b>Навыки:</b> {esc(profile['skills'])}\n"
        f"🎯 <b>Интересы:</b> {esc(profile['interests'])}\n"
        f"👥 <b>Роль:</b> {esc(profile['role'])}\n"
        f"🚀 <b>Цель:</b> {esc(profile['goal'])}\n"
        f"⏰ <b>Время:</b> {esc(profile['free_time'])}\n"
        f"🎓 {esc(profile['course'])} курс, {esc(profile['institute'])}\n\n"
        f"📝 {esc(profile['about'])}\n\n"
        "🤝 Чтобы связаться, отправь запрос на контакт "
        "и дождись согласия участника."
    )


def result_keyboard(position, total):
    keyboard = types.InlineKeyboardMarkup()

    nav = []
    if position > 0:
        nav.append(
            types.InlineKeyboardButton(
                "◀️ Назад", callback_data=f"search_page_{position - 1}"
            )
        )
    nav.append(
        types.InlineKeyboardButton(
            f"{position + 1}/{total}", callback_data="search_noop"
        )
    )
    if position < total - 1:
        nav.append(
            types.InlineKeyboardButton(
                "Вперёд ▶️", callback_data=f"search_page_{position + 1}"
            )
        )
    keyboard.row(*nav)
    keyboard.add(
        types.InlineKeyboardButton(
            "🤝 Запросить контакт",
            callback_data=f"contact_request_{position}"
        )
    )
    keyboard.add(
        types.InlineKeyboardButton(
            "🔁 Новый поиск", callback_data="search_menu"
        )
    )
    return keyboard


def require_profile(message):
    """Поиск доступен только тем, у кого есть анкета."""
    if get_profile(message.from_user.id) is None:
        bot.send_message(
            message.chat.id,
            "📝 Чтобы искать участников, сначала создай свою анкету.",
            reply_markup=registration_keyboard()
        )
        return False
    return True


@bot.message_handler(commands=["search"])
@bot.message_handler(func=lambda message: message.text == SEARCH_BUTTON)
def search_menu(message):
    # Если пользователь был посреди другого ввода - сбрасываем его.
    bot.clear_step_handler_by_chat_id(message.chat.id)
    user_data.pop(message.from_user.id, None)

    if not require_profile(message):
        return

    bot.send_message(
        message.chat.id,
        "🔍 <b>Поиск участников</b>\n\nВыбери, как искать:",
        parse_mode="HTML",
        reply_markup=search_menu_keyboard()
    )


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("search_")
)
def search_callback(call):
    bot.answer_callback_query(call.id)
    data = call.data
    user_id = call.from_user.id
    chat_id = call.message.chat.id

    if data == "search_noop":
        return

    if data == "search_menu":
        bot.send_message(
            chat_id,
            "🔍 <b>Поиск участников</b>\n\nВыбери, как искать:",
            parse_mode="HTML",
            reply_markup=search_menu_keyboard()
        )
        return

    if get_profile(user_id) is None:
        bot.send_message(
            chat_id,
            "📝 Сначала создай свою анкету.",
            reply_markup=registration_keyboard()
        )
        return

    if data == "search_everyone":
        run_search(chat_id, user_id, "all", "")
        return

    if data in SEARCH_MODES:
        field, title, example = SEARCH_MODES[data]

        text = (
            f"Введи, что искать по {title}.\n"
            f"Можно несколько значений через запятую, "
            f"например: {example}"
        )

        if field != "all":
            popular = get_popular_values(field, exclude_user_id=user_id)
            if popular:
                text += "\n\n📊 Популярное сейчас: " + ", ".join(
                    f"{value} ({count})" for value, count in popular
                )

        text += "\n\nДля отмены отправь /cancel"

        sent = bot.send_message(
            chat_id,
            text,
            reply_markup=types.ReplyKeyboardRemove()
        )
        bot.register_next_step_handler(sent, process_search_query, field)
        return

    if data.startswith("search_page_"):
        show_result_page(call, data[len("search_page_"):])


def process_search_query(message, field):
    text = (message.text or "").strip()

    if text.startswith("/") or text in MENU_BUTTONS or not text:
        bot.send_message(
            message.chat.id,
            "Поиск отменён.",
            reply_markup=main_menu_keyboard()
        )
        return

    run_search(message.chat.id, message.from_user.id, field, text)


def run_search(chat_id, user_id, field, query):
    results = search_profiles(user_id, query, field)

    if not results:
        bot.send_message(
            chat_id,
            "😕 Никого не нашлось. Попробуй другой запрос "
            "или поиск по всем полям.",
            reply_markup=search_menu_keyboard()
        )
        return

    search_state[user_id] = {
        "results": results,
        "field": field,
        "query": query
    }

    bot.send_message(
        chat_id,
        format_result(results[0], 0, len(results)),
        parse_mode="HTML",
        reply_markup=result_keyboard(0, len(results))
    )


def show_result_page(call, raw_position):
    state = search_state.get(call.from_user.id)

    if state is None:
        bot.send_message(
            call.message.chat.id,
            "Результаты устарели. Запусти поиск заново.",
            reply_markup=search_menu_keyboard()
        )
        return

    try:
        position = int(raw_position)
    except ValueError:
        return

    results = state["results"]
    if not 0 <= position < len(results):
        return

    try:
        bot.edit_message_text(
            format_result(results[position], position, len(results)),
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML",
            reply_markup=result_keyboard(position, len(results))
        )
    except telebot.apihelper.ApiTelegramException:
        # например, "message is not modified" - можно игнорировать
        pass


@bot.message_handler(commands=["cancel"])
def cancel(message):
    bot.clear_step_handler_by_chat_id(message.chat.id)
    user_data.pop(message.from_user.id, None)

    bot.send_message(
        message.chat.id,
        "Действие отменено.",
        reply_markup=(
            main_menu_keyboard()
            if get_profile(message.from_user.id) is not None
            else registration_keyboard()
        )
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
    search_state.pop(user_id, None)

    bot.send_message(
        call.message.chat.id,
        "🗑 Анкета удалена.\n\n"
        "Если захочешь вернуться, создай новую анкету!",
        reply_markup=registration_keyboard()
    )

#Связь между участниками с согласия обеих сторон
def contact_decision_keyboard(requester_id):
    keyboard = types.InlineKeyboardMarkup()

    keyboard.row(
        types.InlineKeyboardButton(
            "✅ Принять",
            callback_data=f"contact_accept_{requester_id}"
        ),
        types.InlineKeyboardButton(
            "❌ Отклонить",
            callback_data=f"contact_reject_{requester_id}"
        )
    )

    return keyboard


def contact_share_keyboard():
    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        one_time_keyboard=True
    )

    keyboard.add(
        types.KeyboardButton(
            "📱 Поделиться контактом",
            request_contact=True
        )
    )

    return keyboard


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("contact_request_")
)
def request_contact_callback(call):
    bot.answer_callback_query(call.id)

    requester_id = call.from_user.id

    try:
        position = int(call.data.rsplit("_", 1)[1])
    except ValueError:
        return

    state = search_state.get(requester_id)

    if state is None:
        bot.send_message(
            call.message.chat.id,
            "Результаты поиска устарели. Запусти поиск заново."
        )
        return

    results = state["results"]

    if not 0 <= position < len(results):
        return

    target_id = results[position]["user_id"]

    if requester_id == target_id:
        return

    if get_profile(target_id) is None:
        bot.send_message(
            call.message.chat.id,
            "Эта анкета больше недоступна."
        )
        return

    created = create_contact_request(requester_id, target_id)

    if not created:
        bot.send_message(
            call.message.chat.id,
            "Запрос уже отправлен или контакт уже согласован."
        )
        return

    try:
        bot.send_message(
            target_id,
            "🤝 <b>Запрос на связь в TeamUp</b>\n\n"
            "Другой участник хочет связаться с тобой.\n"
            "Разрешить обмен контактами?",
            parse_mode="HTML",
            reply_markup=contact_decision_keyboard(requester_id)
        )
    except telebot.apihelper.ApiTelegramException:
        update_contact_request(
            requester_id, target_id, "rejected"
        )
        bot.send_message(
            call.message.chat.id,
            "Не удалось доставить запрос. "
            "Возможно, участник ещё не запускал бота."
        )
        return

    bot.send_message(
        call.message.chat.id,
        "✅ Запрос отправлен! Дождись ответа участника."
    )


@bot.callback_query_handler(
    func=lambda call: (
        call.data.startswith("contact_accept_")
        or call.data.startswith("contact_reject_")
    )
)
def contact_decision_callback(call):
    action, requester_text = call.data.rsplit("_", 1)

    try:
        requester_id = int(requester_text)
    except ValueError:
        bot.answer_callback_query(call.id)
        return

    target_id = call.from_user.id

    status = get_contact_request(requester_id, target_id)

    if status != "pending":
        bot.answer_callback_query(
            call.id,
            "Этот запрос уже обработан."
        )
        return

    if action == "contact_accept":
        updated = update_contact_request(
            requester_id, target_id, "accepted"
        )
    else:
        updated = update_contact_request(
            requester_id, target_id, "rejected"
        )

    if not updated:
        bot.answer_callback_query(
            call.id,
            "Этот запрос уже обработан."
        )
        return

    bot.answer_callback_query(call.id)

    try:
        bot.edit_message_reply_markup(
            call.message.chat.id,
            call.message.message_id,
            reply_markup=None
        )
    except telebot.apihelper.ApiTelegramException:
        pass

    if action == "contact_reject":
        bot.send_message(
            target_id,
            "Ты отклонил(а) запрос на связь."
        )
        bot.send_message(
            requester_id,
            "Участник пока не согласился на связь."
        )
        return

    bot.send_message(
        target_id,
        "✅ Ты согласился(ась) на связь!"
    )
    bot.send_message(
        requester_id,
        "🎉 Участник согласился на связь!"
    )

    requester_username = get_telegram_username(requester_id)
    target_username = get_telegram_username(target_id)

    if requester_username:
        requester_contact = "@" + requester_username
    else:
        requester_contact = None

    if target_username:
        target_contact = "@" + target_username
    else:
        target_contact = None

    if requester_contact and target_contact:
        bot.send_message(
            requester_id,
            f"Контакт участника: {target_contact}"
        )
        bot.send_message(
            target_id,
            f"Контакт участника: {requester_contact}"
        )
    else:
        bot.send_message(
            requester_id,
            "У одного из участников не указан username.\n"
            "Если хотите поделиться номером телефона, "
            "используйте кнопку ниже.",
            reply_markup=contact_share_keyboard()
        )
        bot.send_message(
            target_id,
            "У одного из участников не указан username.\n"
            "Если хотите поделиться номером телефона, "
            "используйте кнопку ниже.",
            reply_markup=contact_share_keyboard()
        )
@bot.message_handler(content_types=["contact"])
def receive_shared_contact(message):
    contact = message.contact
    user_id = message.from_user.id

    # Пользователь может поделиться только собственным контактом.
    if contact.user_id != user_id:
        bot.send_message(
            message.chat.id,
            "Пожалуйста, отправь именно свой контакт "
            "через кнопку Telegram."
        )
        return

    partners = get_accepted_contact_partners(user_id)

    if not partners:
        bot.send_message(
            message.chat.id,
            "Нет участников, с которыми согласован обмен контактами."
        )
        return

    delivered = 0

    for partner_id in partners:
        try:
            bot.send_contact(
                partner_id,
                contact.phone_number,
                contact.first_name,
                last_name=contact.last_name or ""
            )
            delivered += 1
        except telebot.apihelper.ApiTelegramException:
            continue

    bot.send_message(
        message.chat.id,
        f"Контакт отправлен участникам: {delivered}."
    )
bot.infinity_polling()