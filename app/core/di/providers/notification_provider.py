import httpx

from app.core.config.ntfy_settings import NtfySettings
from app.core.config.smtp_settings import SmtpSettings
from app.shared.application.ports.notification.email_port import EmailPort
from app.shared.application.ports.notification.push_port import PushPort
from app.shared.infrastructure.notification.ntfy_push_adapter import NtfyPushAdapter
from app.shared.infrastructure.notification.smtp_email_adapter import SmtpEmailAdapter


def create_email_adapter(settings: SmtpSettings) -> EmailPort:
    """Создать SmtpEmailAdapter с настройками SMTP."""
    return SmtpEmailAdapter(
        host=settings.host,
        port=settings.port,
        username=settings.username or None,
        password=settings.password or None,
        use_tls=settings.use_tls,
        from_email=settings.from_email,
    )


def create_push_adapter(settings: NtfySettings) -> PushPort:
    """Создать NtfyPushAdapter с настройками ntfy."""
    http_client = httpx.AsyncClient()
    return NtfyPushAdapter(
        base_url=settings.base_url,
        http_client=http_client,
    )
