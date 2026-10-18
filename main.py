import html
import os

import telebot
from dotenv import load_dotenv
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
    get_candidates,
    create_invitation,
    get_invitation,
    update_invitation_status,
    get_pending_invitations_for,
    delete_profile,
)

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("Переменная окружения BOT_TOKEN не задана")

bot = telebot.TeleBot(BOT_TOKEN)

create_database()

# Состояние диалогов (только в памяти — сбрасывается при рестарте)
user_data = {}
browse_state = {}


# ─────────────────────────────────────────────────────────
#  Вспомогательное
# ─────────────────────────────────────────────────────────

def require_text(handler):
    """Декоратор: пропускает только непустой текст; /cancel отменяет диалог."""
    def wrapper(message):
        if message.text == "/cancel":
            cancel(message)
            return
        if not message.text or not message.text.strip():
            sent = bot.send_message(
                message.chat.id,
                "Пожалуйста, отправь ответ текстом."
            )
            bot.register_next_step_handler(sent, wrapper)
            return
        handler(message)
    return wrapper


def format_profile(profile, title="✨ <b>МОЯ АНКЕТА</b>"):
    (name, interests, course, institute, skills,
     role, goal, free_time, about) = profile
    e = html.escape
    return (
        f"{title}\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"👤 <b>{e(name or 'Без имени')}</b>\n"
        "<i>Участник TeamUp</i>\n\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "🛠 <b>НАВЫКИ</b>\n"
        f"{e(skills or 'Не указаны')}\n\n"
        "🎯 <b>ИНТЕРЕСЫ</b>\n"
        f"{e(interests or 'Не указаны')}\n\n"
        "👥 <b>РОЛЬ В КОМАНДЕ</b>\n"
        f"{e(role or 'Не указана')}\n\n"
        "🚀 <b>ЦЕЛЬ ПОИСКА КОМАНДЫ</b>\n"
        f"{e(goal or 'Не указана')}\n\n"
        "⏰ <b>СВОБОДНОЕ ВРЕМЯ</b>\n"
        f"{e(free_time or 'Не указано')}\n\n"
        "📝 <b>О СЕБЕ</b>\n"
        f"{e(about or 'Не указано')}\n\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "🎓 <b>ОБУЧЕНИЕ</b>\n"
        f"📚 Курс: {e(course or 'Не указан')}\n"
        f"🏛 Институт: {e(institute or 'Не указан')}\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "🚀 <i>Ищем единомышленников и создаём проекты!</i>"
    )


# ─────────────────────────────────────────────────────────
#  Клавиатуры
# ─────────────────────────────────────────────────────────

def registration_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("📝 Зарегистрироваться"))
    return keyboard


def main_menu_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(
        types.KeyboardButton("👤 Моя анкета"),
        types.KeyboardButton("✏️ Изменить анкету")
    )
    keyboard.row(
        types.KeyboardButton("👀 Смотреть анкеты"),
        types.KeyboardButton("📬 Мои приглашения")
    )
    keyboard.add(types.KeyboardButton("🗑 Удалить анкету"))
    return keyboard


# ─────────────────────────────────────────────────────────
#  /start и /cancel
# ─────────────────────────────────────────────────────────

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


@bot.message_handler(commands=["cancel"])
def cancel(message):
    user_id = message.from_user.id

    if user_id in user_data:
        del user_data[user_id]

    if get_profile(user_id) is not None:
        bot.send_message(
            message.chat.id,
            "Действие отменено.",
            reply_markup=main_menu_keyboard()
        )
    else:
        bot.send_message(
            message.chat.id,
            "Действие отменено. Создай анкету, чтобы начать.",
            reply_markup=registration_keyboard()
        )


# ─────────────────────────────────────────────────────────
#  Регистрация
# ─────────────────────────────────────────────────────────

@bot.message_handler(func=lambda m: m.text == "📝 Зарегистрироваться")
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
        "Как тебя зовут?\n\n(в любой момент можно отменить через /cancel)",
        reply_markup=types.ReplyKeyboardRemove()
    )
    bot.register_next_step_handler(sent, get_name)


@require_text
def get_name(message):
    user_id = message.from_user.id
    user_data[user_id]["name"] = message.text.strip()

    sent = bot.send_message(
        message.chat.id,
        "Отлично! Теперь напиши, какими навыками ты обладаешь.\n"
        "Например: Python, C++, HTML, CSS, дизайн."
    )
    bot.register_next_step_handler(sent, get_skills)


@require_text
def get_skills(message):
    user_id = message.from_user.id
    user_data[user_id]["skills"] = message.text.strip()

    sent = bot.send_message(
        message.chat.id,
        "Какие у тебя интересы?\n"
        "Например: AI, Data Science, игры, веб-разработка."
    )
    bot.register_next_step_handler(sent, get_interests)


@require_text
def get_interests(message):
    user_id = message.from_user.id
    user_data[user_id]["interests"] = message.text.strip()

    sent = bot.send_message(message.chat.id, "На каком ты курсе?")
    bot.register_next_step_handler(sent, get_course)


@require_text
def get_course(message):
    user_id = message.from_user.id
    user_data[user_id]["course"] = message.text.strip()

    sent = bot.send_message(
        message.chat.id,
        "В каком институте / университете ты учишься?"
    )
    bot.register_next_step_handler(sent, get_institute)


@require_text
def get_institute(message):
    user_id = message.from_user.id
    user_data[user_id]["institute"] = message.text.strip()

    sent = bot.send_message(
        message.chat.id,
        "Какую роль ты хочешь выполнять в команде?\n"
        "Например: разработчик, дизайнер, аналитик."
    )
    bot.register_next_step_handler(sent, get_role)


@require_text
def get_role(message):
    user_id = message.from_user.id
    user_data[user_id]["role"] = message.text.strip()

    sent = bot.send_message(
        message.chat.id,
        "Для чего ты ищешь команду?\n"
        "Например: хакатон, учебный проект, стартап."
    )
    bot.register_next_step_handler(sent, get_goal)


@require_text
def get_goal(message):
    user_id = message.from_user.id
    user_data[user_id]["goal"] = message.text.strip()

    sent = bot.send_message(
        message.chat.id,
        "Сколько времени ты готов(а) уделять проекту?\n"
        "Например: несколько часов в неделю."
    )
    bot.register_next_step_handler(sent, get_free_time)


@require_text
def get_free_time(message):
    user_id = message.from_user.id
    user_data[user_id]["free_time"] = message.text.strip()

    sent = bot.send_message(
        message.chat.id,
        "Расскажи немного о себе. Что тебе интересно "
        "и чему ты хочешь научиться?"
    )
    bot.register_next_step_handler(sent, get_about)


@require_text
def get_about(message):
    user_id = message.from_user.id
    user_data[user_id]["about"] = message.text.strip()

    profile = user_data.pop(user_id)

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

    bot.send_message(
        message.chat.id,
        "✅ Анкета создана!\n\nВыбери действие:",
        reply_markup=main_menu_keyboard()
    )


# ─────────────────────────────────────────────────────────
#  Моя анкета
# ─────────────────────────────────────────────────────────

@bot.message_handler(func=lambda m: m.text == "👤 Моя анкета")
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

    bot.send_message(
        message.chat.id,
        format_profile(profile),
        parse_mode="HTML",
        reply_markup=main_menu_keyboard()
    )


# ─────────────────────────────────────────────────────────
#  Изменение анкеты
# ─────────────────────────────────────────────────────────

EDIT_FIELDS = {
    "edit_name": (
        "Напиши новое имя:",
        update_name,
        "✅ Имя изменено на: <b>{}</b>"
    ),
    "edit_skills": (
        "Напиши новые навыки:",
        update_skills,
        "✅ Навыки изменены: <b>{}</b>"
    ),
    "edit_interests": (
        "Напиши свои новые интересы:",
        update_interests,
        "✅ Интересы изменены на: <b>{}</b>"
    ),
    "edit_course": (
        "Напиши свой курс:",
        update_course,
        "✅ Курс изменён на: <b>{}</b>"
    ),
    "edit_institute": (
        "Напиши свой институт:",
        update_institute,
        "✅ Институт изменён на: <b>{}</b>"
    ),
    "edit_role": (
        "Напиши новую роль в команде:",
        update_role,
        "✅ Роль в команде изменена на: <b>{}</b>"
    ),
    "edit_goal": (
        "Напиши новую цель поиска команды:",
        update_goal,
        "✅ Цель изменена на: <b>{}</b>"
    ),
    "edit_free_time": (
        "Напиши, сколько времени готов(а) уделять проекту:",
        update_free_time,
        "✅ Свободное время: <b>{}</b>"
    ),
    "edit_about": (
        "Напиши новую информацию о себе:",
        update_about,
        "✅ Информация о себе обновлена: <b>{}</b>"
    ),
}


@bot.message_handler(func=lambda m: m.text == "✏️ Изменить анкету")
@bot.message_handler(commands=["edit"])
def edit_profile(message):
    if get_profile(message.from_user.id) is None:
        bot.send_message(
            message.chat.id,
            "Сначала создай анкету через /start."
        )
        return

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton("👤 Имя", callback_data="edit_name"),
        types.InlineKeyboardButton("🛠 Навыки", callback_data="edit_skills"),
        types.InlineKeyboardButton("🎯 Интересы", callback_data="edit_interests"),
        types.InlineKeyboardButton("🎓 Курс", callback_data="edit_course"),
        types.InlineKeyboardButton("🏫 Институт", callback_data="edit_institute"),
        types.InlineKeyboardButton("👥 Роль", callback_data="edit_role"),
        types.InlineKeyboardButton("🚀 Цель", callback_data="edit_goal"),
        types.InlineKeyboardButton("⏰ Время", callback_data="edit_free_time"),
        types.InlineKeyboardButton("📝 О себе", callback_data="edit_about"),
    )

    bot.send_message(
        message.chat.id,
        "✏️ Что ты хочешь изменить?",
        reply_markup=keyboard
    )


@bot.callback_query_handler(
    func=lambda c: c.data and c.data in EDIT_FIELDS
)
def edit_callback(call):
    bot.answer_callback_query(call.id)

    if get_profile(call.from_user.id) is None:
        bot.send_message(
            call.message.chat.id,
            "Анкеты больше нет. Создай новую через /start."
        )
        return

    prompt, update_fn, template = EDIT_FIELDS[call.data]

    sent = bot.send_message(
        call.message.chat.id,
        prompt,
        reply_markup=types.ReplyKeyboardRemove()
    )
    bot.register_next_step_handler(
        sent, make_change_handler(update_fn, template)
    )


def make_change_handler(update_fn, template):
    @require_text
    def handler(message):
        value = message.text.strip()
        update_fn(message.from_user.id, value)
        bot.send_message(
            message.chat.id,
            template.format(html.escape(value)),
            parse_mode="HTML",
            reply_markup=main_menu_keyboard()
        )
    return handler


# ─────────────────────────────────────────────────────────
#  Удаление анкеты
# ─────────────────────────────────────────────────────────

@bot.message_handler(func=lambda m: m.text == "🗑 Удалить анкету")
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
            "✅ Да, удалить", callback_data="confirm_delete"
        ),
        types.InlineKeyboardButton(
            "❌ Отмена", callback_data="cancel_delete"
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
    func=lambda c: c.data in ("confirm_delete", "cancel_delete")
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
    delete_profile(user_id)
    user_data.pop(user_id, None)
    browse_state.pop(user_id, None)

    bot.send_message(
        call.message.chat.id,
        "🗑 Анкета удалена.\n\n"
        "Если захочешь вернуться, создай новую анкету!",
        reply_markup=registration_keyboard()
    )


# ─────────────────────────────────────────────────────────
#  Просмотр анкет (лайки)
# ─────────────────────────────────────────────────────────

@bot.message_handler(func=lambda m: m.text == "👀 Смотреть анкеты")
def browse_profiles(message):
    user_id = message.from_user.id

    if get_profile(user_id) is None:
        bot.send_message(
            message.chat.id,
            "Сначала создай анкету через /start.",
            reply_markup=registration_keyboard()
        )
        return

    candidates = get_candidates(user_id)
    if not candidates:
        bot.send_message(
            message.chat.id,
            "😔 Пока нет других анкет для просмотра.\n"
            "Загляни позже!",
            reply_markup=main_menu_keyboard()
        )
        return

    browse_state[user_id] = {"candidates": candidates, "index": 0}
    show_candidate(message.chat.id, user_id)


def show_candidate(chat_id, user_id):
    state = browse_state.get(user_id)
    if not state:
        return

    while state["index"] < len(state["candidates"]):
        candidate_id = state["candidates"][state["index"]]
        profile = get_profile(candidate_id)
        if profile is None:
            state["index"] += 1
            continue

        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(
            types.InlineKeyboardButton(
                "❤️ Хочу в команду",
                callback_data=f"invite_{candidate_id}"
            ),
            types.InlineKeyboardButton(
                "➡️ Следующий",
                callback_data="next_profile"
            )
        )

        bot.send_message(
            chat_id,
            format_profile(profile, title="✨ <b>АНКЕТА УЧАСТНИКА</b>"),
            parse_mode="HTML",
            reply_markup=keyboard
        )
        return

    bot.send_message(
        chat_id,
        "😔 Больше анкет пока нет.",
        reply_markup=main_menu_keyboard()
    )
    browse_state.pop(user_id, None)


@bot.callback_query_handler(func=lambda c: c.data == "next_profile")
def next_profile(call):
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id

    if user_id not in browse_state:
        bot.send_message(
            call.message.chat.id,
            "Начни просмотр заново.",
            reply_markup=main_menu_keyboard()
        )
        return

    browse_state[user_id]["index"] += 1

    try:
        bot.edit_message_reply_markup(
            call.message.chat.id,
            call.message.message_id,
            reply_markup=None
        )
    except Exception:
        pass

    show_candidate(call.message.chat.id, user_id)


@bot.callback_query_handler(
    func=lambda c: c.data and c.data.startswith("invite_")
)
def invite_user(call):
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id

    if get_profile(user_id) is None:
        bot.send_message(
            call.message.chat.id,
            "Сначала создай анкету.",
            reply_markup=registration_keyboard()
        )
        return

    try:
        to_user_id = int(call.data.split("_", 1)[1])
    except (IndexError, ValueError):
        return

    if to_user_id == user_id:
        bot.answer_callback_query(
            call.id, "Это твоя анкета 😅", show_alert=True
        )
        return

    invitation_id = create_invitation(user_id, to_user_id)

    if invitation_id is None:
        bot.send_message(
            call.message.chat.id,
            "Ты уже отправил(а) приглашение этому участнику — ждём ответа."
        )
    else:
        bot.send_message(call.message.chat.id, "✅ Приглашение отправлено!")

        sender_profile = get_profile(user_id)
        sender_name = (sender_profile[0] if sender_profile else "Участник")

        notif_keyboard = types.InlineKeyboardMarkup()
        notif_keyboard.add(
            types.InlineKeyboardButton(
                "✅ Принять", callback_data=f"accept_{invitation_id}"
            ),
            types.InlineKeyboardButton(
                "❌ Отклонить", callback_data=f"reject_{invitation_id}"
            )
        )

        header = (
            format_profile(
                sender_profile,
                title="📬 <b>ПРИГЛАШЕНИЕ В КОМАНДУ</b>"
            )
            if sender_profile
            else f"👤 {html.escape(sender_name)}"
        )

        try:
            bot.send_message(
                to_user_id,
                f"{header}\n\n"
                "━━━━━━━━━━━━━━━━━━\n"
                f"👤 <b>{html.escape(sender_name)}</b> "
                "приглашает тебя в команду!",
                parse_mode="HTML",
                reply_markup=notif_keyboard
            )
        except Exception:
            bot.send_message(
                call.message.chat.id,
                "⚠️ Не удалось доставить приглашение получателю "
                "(возможно, он заблокировал бота)."
            )

    if user_id in browse_state:
        browse_state[user_id]["index"] += 1

    try:
        bot.edit_message_reply_markup(
            call.message.chat.id,
            call.message.message_id,
            reply_markup=None
        )
    except Exception:
        pass

    show_candidate(call.message.chat.id, user_id)


# ─────────────────────────────────────────────────────────
#  Принятие / отклонение приглашений
# ─────────────────────────────────────────────────────────

@bot.callback_query_handler(
    func=lambda c: c.data and (
        c.data.startswith("accept_") or c.data.startswith("reject_")
    )
)
def handle_invitation_response(call):
    bot.answer_callback_query(call.id)

    action, _, raw_id = call.data.partition("_")
    try:
        invitation_id = int(raw_id)
    except ValueError:
        return

    invitation = get_invitation(invitation_id)
    if invitation is None:
        bot.edit_message_text(
            "⚠️ Приглашение не найдено.",
            call.message.chat.id,
            call.message.message_id
        )
        return

    from_id, to_id, status = invitation

    if to_id != call.from_user.id:
        bot.answer_callback_query(
            call.id, "Это не твоё приглашение.", show_alert=True
        )
        return

    if status != "pending":
        bot.edit_message_text(
            "Это приглашение уже обработано.",
            call.message.chat.id,
            call.message.message_id
        )
        return

    new_status = "accepted" if action == "accept" else "rejected"
    update_invitation_status(invitation_id, new_status)

    label = (
        "✅ Ты принял(а) приглашение."
        if action == "accept"
        else "❌ Ты отклонил(а) приглашение."
    )
    bot.edit_message_text(
        label,
        call.message.chat.id,
        call.message.message_id
    )

    responder_profile = get_profile(call.from_user.id)
    responder_name = (
        responder_profile[0] if responder_profile else "Участник"
    )
    responder_link = (
        f'<a href="tg://user?id={call.from_user.id}">'
        f'{html.escape(responder_name)}</a>'
    )

    try:
        if action == "accept":
            bot.send_message(
                from_id,
                "🎉 <b>Приглашение принято!</b>\n\n"
                f"👤 {responder_link} принял(а) твоё приглашение.\n\n"
                "Напиши ему/ей, чтобы обсудить детали проекта.",
                parse_mode="HTML"
            )
        else:
            bot.send_message(
                from_id,
                "😔 <b>Приглашение отклонено</b>\n\n"
                f"👤 {responder_link} отклонил(а) твоё приглашение.\n\n"
                "Не расстраивайся — впереди ещё много анкет!",
                parse_mode="HTML"
            )
    except Exception:
        pass


# ─────────────────────────────────────────────────────────
#  Список входящих приглашений
# ─────────────────────────────────────────────────────────

@bot.message_handler(func=lambda m: m.text == "📬 Мои приглашения")
@bot.message_handler(commands=["invitations"])
def show_invitations(message):
    user_id = message.from_user.id
    pending = get_pending_invitations_for(user_id)

    if not pending:
        bot.send_message(
            message.chat.id,
            "📭 У тебя нет новых приглашений.",
            reply_markup=main_menu_keyboard()
        )
        return

    bot.send_message(
        message.chat.id,
        f"📬 У тебя {len(pending)} приглашени(й).",
        reply_markup=main_menu_keyboard()
    )

    for invitation_id, from_user_id in pending:
        from_profile = get_profile(from_user_id)
        if from_profile is None:
            continue

        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(
            types.InlineKeyboardButton(
                "✅ Принять", callback_data=f"accept_{invitation_id}"
            ),
            types.InlineKeyboardButton(
                "❌ Отклонить", callback_data=f"reject_{invitation_id}"
            )
        )

        bot.send_message(
            message.chat.id,
            format_profile(
                from_profile,
                title="📬 <b>ПРИГЛАШЕНИЕ В КОМАНДУ</b>"
            ),
            parse_mode="HTML",
            reply_markup=keyboard
        )


# ─────────────────────────────────────────────────────────

bot.infinity_polling()