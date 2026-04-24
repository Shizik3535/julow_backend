from __future__ import annotations

import uuid

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.application.ports.file_storage.file_storage_port import FileStoragePort
from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.url_vo import Url
from app.context.profile.domain.repositories.user_profile_repository import UserProfileRepository
from app.context.profile.domain.exceptions.profile_exceptions import ProfileNotFoundException


class ChangeAvatarCommand(BaseCommand):
    """
    Команда изменения аватара пользователя.

    Атрибуты:
        user_id: ID пользователя.
        file_data: Содержимое файла аватара (байты).
        content_type: MIME-тип файла (например image/png).
    """

    user_id: str
    file_data: bytes
    content_type: str = "image/png"


class ChangeAvatarHandler(BaseCommandHandler[ChangeAvatarCommand, None]):
    """
    Обработчик изменения аватара.

    Загружает файл в хранилище через FileStoragePort,
    получает URL и вызывает доменный метод change_avatar.
    """

    def __init__(
        self,
        profile_repo: UserProfileRepository,
        file_storage: FileStoragePort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._profile_repo = profile_repo
        self._file_storage = file_storage
        self._event_bus = event_bus

    async def handle(self, command: ChangeAvatarCommand) -> None:
        profile = await self._profile_repo.get_by_user_id(Id.from_string(command.user_id))
        if profile is None:
            raise ProfileNotFoundException(command.user_id)

        key = f"avatars/{command.user_id}/{uuid.uuid4()}"
        await self._file_storage.upload(
            key=key,
            data=command.file_data,
            content_type=command.content_type,
        )
        url_str = await self._file_storage.get_url(key=key)

        profile.change_avatar(Url(url_str))
        await self._profile_repo.update(profile)

        await self._event_bus.publish_all(profile.clear_domain_events())
