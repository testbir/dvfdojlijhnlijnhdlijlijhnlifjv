# id_service/services/email_service.py

import logging
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any
from jinja2 import Template

from core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails"""
    
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.smtp_tls = settings.SMTP_TLS
        self.from_email = settings.EMAIL_FROM
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """Send email using SMTP"""
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["From"] = self.from_email
            message["To"] = to_email
            message["Subject"] = subject
            
            # Add text and HTML parts
            if text_content:
                text_part = MIMEText(text_content, "plain")
                message.attach(text_part)
            
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)
            
            # Send email
            async with aiosmtplib.SMTP(
                hostname=self.smtp_host,
                port=self.smtp_port,
                use_tls=False
            ) as smtp:
                if self.smtp_tls:
                    await smtp.starttls()
                await smtp.login(self.smtp_user, self.smtp_password)
                await smtp.send_message(message)

            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False
    
    async def send_verification_code(
        self,
        to_email: str,
        username: str,
        code: str,
        purpose: str = "registration"
    ) -> bool:
        """Send verification code email"""
        
        subject_map = {
            "registration": "Подтверждение регистрации на Asynq",
            "reset": "Сброс пароля на Asynq",
            "change_email": "Подтверждение смены email на Asynq"
        }
        
        subject = subject_map.get(purpose, "Код подтверждения Asynq")
        
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px 10px 0 0; }
                .content { background: #f7f7f7; padding: 30px; border-radius: 0 0 10px 10px; }
                .code-box { background: white; border: 2px solid #667eea; border-radius: 8px; padding: 20px; text-align: center; margin: 20px 0; }
                .code { font-size: 32px; font-weight: bold; letter-spacing: 8px; color: #667eea; }
                .footer { margin-top: 30px; padding-top: 20px; border-top: 1px solid #e0e0e0; font-size: 12px; color: #666; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 style="margin: 0;">Asynq ID</h1>
                </div>
                <div class="content">
                    <h2>Здравствуйте, {{ username }}!</h2>
                    
                    {% if purpose == 'registration' %}
                        <p>Спасибо за регистрацию на платформе Asynq! Для завершения регистрации введите код подтверждения:</p>
                    {% elif purpose == 'reset' %}
                        <p>Вы запросили сброс пароля. Используйте этот код для подтверждения:</p>
                    {% elif purpose == 'change_email' %}
                        <p>Вы запросили смену email адреса. Используйте этот код для подтверждения нового адреса:</p>
                    {% endif %}
                    
                    <div class="code-box">
                        <div class="code">{{ code }}</div>
                    </div>
                    
                    <p>Код действителен в течение 5 минут.</p>
                    
                    <p style="color: #666; font-size: 14px;">
                        Если вы не запрашивали этот код, просто проигнорируйте это письмо.
                    </p>
                    
                    <div class="footer">
                        <p>С уважением,<br>Команда Asynq</p>
                        <p>Это автоматическое сообщение, пожалуйста, не отвечайте на него.</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_template = """
        Здравствуйте, {{ username }}!
        
        {% if purpose == 'registration' %}
        Спасибо за регистрацию на платформе Asynq! Для завершения регистрации введите код подтверждения:
        {% elif purpose == 'reset' %}
        Вы запросили сброс пароля. Используйте этот код для подтверждения:
        {% elif purpose == 'change_email' %}
        Вы запросили смену email адреса. Используйте этот код для подтверждения нового адреса:
        {% endif %}
        
        Код: {{ code }}
        
        Код действителен в течение 5 минут.
        
        Если вы не запрашивали этот код, просто проигнорируйте это письмо.
        
        С уважением,
        Команда Asynq
        """
        
        # Render templates
        html_content = Template(html_template).render(
            username=username,
            code=code,
            purpose=purpose
        )
        
        text_content = Template(text_template).render(
            username=username,
            code=code,
            purpose=purpose
        )
        
        return await self.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )
    
    async def send_password_changed_notification(
        self,
        to_email: str,
        username: str
    ) -> bool:
        """Send notification about password change"""
        
        subject = "Ваш пароль был изменен"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f7f7f7; padding: 30px; border-radius: 0 0 10px 10px; }}
                .alert {{ background: #fff3cd; border: 1px solid #ffc107; border-radius: 8px; padding: 15px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 style="margin: 0;">Asynq ID</h1>
                </div>
                <div class="content">
                    <h2>Здравствуйте, {username}!</h2>
                    
                    <div class="alert">
                        <strong>⚠️ Важное уведомление о безопасности</strong>
                        <p>Ваш пароль был успешно изменен.</p>
                    </div>
                    
                    <p>Если вы не меняли пароль, немедленно свяжитесь с нашей службой поддержки.</p>
                    
                    <p>Для вашей безопасности все активные сессии были завершены. Вам потребуется войти заново на всех устройствах.</p>
                    
                    <div class="footer" style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e0e0e0; font-size: 12px; color: #666;">
                        <p>С уважением,<br>Команда Asynq</p>
                        <p>Это автоматическое сообщение, пожалуйста, не отвечайте на него.</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Здравствуйте, {username}!
        
        Важное уведомление о безопасности:
        Ваш пароль был успешно изменен.
        
        Если вы не меняли пароль, немедленно свяжитесь с нашей службой поддержки.
        
        Для вашей безопасности все активные сессии были завершены. Вам потребуется войти заново на всех устройствах.
        
        С уважением,
        Команда Asynq
        """
        
        return await self.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )


email_service = EmailService()