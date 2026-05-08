from app.core.config.app_settings import AppSettings
from app.core.config.auth_settings import AuthSettings
from app.core.config.celery_settings import CelerySettings
from app.core.config.clamav_settings import ClamAvSettings
from app.core.config.cors_settings import CorsSettings
from app.core.config.encryption_settings import EncryptionSettings
from app.core.config.database_settings import DatabaseSettings
from app.core.config.kafka_settings import KafkaSettings
from app.core.config.ntfy_settings import NtfySettings
from app.core.config.oauth_settings import OAuthSettings
from app.core.config.redis_settings import RedisSettings
from app.core.config.s3_settings import S3Settings
from app.core.config.smtp_settings import SmtpSettings


class Settings:
    def __init__(self) -> None:
        self.app = AppSettings()
        self.db = DatabaseSettings()
        self.auth = AuthSettings()
        self.cors = CorsSettings()
        self.encryption = EncryptionSettings()
        self.redis = RedisSettings()
        self.s3 = S3Settings()
        self.kafka = KafkaSettings()
        self.smtp = SmtpSettings()
        self.celery = CelerySettings()
        self.ntfy = NtfySettings()
        self.oauth = OAuthSettings()
        self.clamav = ClamAvSettings()


settings = Settings()
