

from celery import Celery
from config import settings
from services.email import EmailService

celery_app = Celery("novelsia", broker=settings.REDIS_URL)

@celery_app.task
def send_verification_email(user_id: int, email: str, token: str):
    """
    Отправка email для подтверждения адреса.
    """
    return EmailService.send_verification_email(user_id, email, token)

@celery_app.task
def send_password_reset_email(user_id: int, email: str, token: str):
    """
    Отправка email для сброса пароля.
    """
    return EmailService.send_password_reset_email(user_id, email, token)

@celery_app.task
def send_welcome_email(user_id: int, email: str):
    """
    Отправка приветственного email.
    """
    return EmailService.send_welcome_email(user_id, email)

@celery_app.task
def send_notification_email(user_id: int, subject: str, message: str):
    """
    Отправка уведомления пользователю.
    """
    return EmailService.send_notification_email(user_id, subject, message)