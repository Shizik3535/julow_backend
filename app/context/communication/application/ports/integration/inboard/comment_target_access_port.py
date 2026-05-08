from __future__ import annotations

from abc import ABC, abstractmethod

from app.context.communication.domain.value_objects.comment_target_type import (
    CommentTargetType,
)


class CommentTargetAccessPort(ABC):
    """
    Inboard-порт: проверка доступа пользователя к комментируемой сущности.

    Communication BC не является источником истины для авторизации над
    задачами/проектами/эпиками/спринтами и т.д. — каждый ``target_type``
    принадлежит своему BC, у которого свой ``PermissionProvider``.

    Этот порт абстрагирует проверку: «может ли пользователь читать
    или комментировать сущность ``target_id`` типа ``target_type``».
    Адаптер в infrastructure-слое разрешает ``target_id`` в
    соответствующий ``project_id`` и делегирует
    ``ProjectPermissionProvider`` (либо иной пермишн-провайдер).

    Реализация поднимает ``CommentTargetForbiddenException``,
    если доступа нет.
    """

    @abstractmethod
    async def require_access(
        self,
        user_id: str,
        target_type: CommentTargetType,
        target_id: str,
    ) -> None:
        """
        Проверить, что у пользователя есть доступ к комментариям
        указанной сущности. Поднимает исключение, если доступа нет.

        Аргументы:
            user_id: Идентификатор пользователя.
            target_type: Тип комментируемой сущности.
            target_id: Идентификатор сущности (opaque, из соответствующего BC).
        """

    @abstractmethod
    async def resolve_workspace_id(
        self,
        target_type: CommentTargetType,
        target_id: str,
    ) -> str | None:
        """
        Найти ``workspace_id``, к которому относится комментируемая сущность.

        Используется для делегирования загрузки вложений в FileStorage BC,
        где квота и хранилище привязаны к workspace.

        Возвращает ``None``, если резолвинг невозможен (тип не поддержан
        или сущность не найдена).
        """
