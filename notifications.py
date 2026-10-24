import logging

import telebot


logger = logging.getLogger(__name__)


class NotificationService:
    """Сервис уведомлений TeamUp."""

    def __init__(self, bot):
        self.bot = bot

    def send_notification(self, user_id, message):
        """Отправляет уведомление пользователю."""

        if not user_id or not message:
            logger.warning(
                "Не указан получатель или текст уведомления."
            )
            return False

        try:
            self.bot.send_message(
                chat_id=user_id,
                text=message
            )
            return True

        except telebot.apihelper.ApiTelegramException:
            logger.exception(
                "Не удалось отправить уведомление пользователю %s",
                user_id
            )
            return False

    def notify_new_invitation(self, user_id, sender_name):
        """Уведомляет о новом приглашении."""

        return self.send_notification(
            user_id,
            f"🔔 Тебя пригласили в команду TeamUp!\n\n"
            f"Отправитель: {sender_name}\n\n"
            "Открой бота, чтобы посмотреть приглашение."
        )

    def notify_invitation_accepted(self, user_id, recipient_name):
        """Уведомляет об принятии приглашения."""

        return self.send_notification(
            user_id,
            f"✅ Отличные новости!\n\n"
            f"{recipient_name} принял(а) твоё приглашение "
            "в команду TeamUp."
        )

    def notify_invitation_rejected(self, user_id, recipient_name):
        """Уведомляет об отклонении приглашения."""

        return self.send_notification(
            user_id,
            f"❌ {recipient_name} отклонил(а) "
            "твоё приглашение в команду."
        )

    def notify_application_response(
        self,
        user_id,
        project_name,
        accepted
    ):
        """Уведомляет об ответе на заявку в проект."""

        if accepted:
            message = (
                f"🎉 Твою заявку в проект «{project_name}» "
                "приняли!\n\n"
                "Поздравляем с новым командным проектом!"
            )
        else:
            message = (
                f"📩 Получен ответ на твою заявку "
                f"в проект «{project_name}».\n\n"
                "К сожалению, заявку не приняли."
            )

        return self.send_notification(user_id, message)

    def notify_participation_status(
        self,
        user_id,
        project_name,
        status
    ):
        """Уведомляет об изменении статуса участия."""

        return self.send_notification(
            user_id,
            f"🔔 Изменение статуса участия\n\n"
            f"Проект: {project_name}\n"
            f"Новый статус: {status}"
        )
