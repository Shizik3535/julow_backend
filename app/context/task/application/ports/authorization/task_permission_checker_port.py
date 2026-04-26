from __future__ import annotations

from abc import ABC, abstractmethod


class TaskPermissionCheckerPort(ABC):
    """
    Порт проверки разрешений пользователя в контексте задачи (Task BC).

    Task BC не содержит собственного агрегата ролей. Проверка делегируется
    в Project BC (`ProjectPermissionProvider`), который инкапсулирует каскад
    ProjectRole → WorkspaceRole → OrgRole.

    Используемое permission-пространство:
        - `tasks.*` — полный доступ к задачам проекта
        - `tasks.create` / `tasks.read` / `tasks.update` / `tasks.delete`
          / `tasks.assign` / `tasks.watch` — конкретные действия
        - `tasks.update_own` — обновление информации своей задачи (assignee)
        - `tasks.update_status` — смена статуса своей задачи (assignee)
        - `tasks.templates.manage` — управление шаблонами задач

    Покрытие разрешений:
        - `tasks.update` покрывает `tasks.update_own` и `tasks.update_status`

    Каскад (реализован в Project/Workspace/Org BC):
        Task BC  : `tasks.<action>` на `project_id`
        Project  : `tasks.<action>` или `project.*`
        Workspace: `projects.tasks.<action>` / `projects.*` / `ws.*`
        Org      : `workspaces.projects.tasks.<action>` /
                   `workspaces.projects.*` / `workspaces.*` / `org.*`
    """

    @abstractmethod
    async def has_permission(self, user_id: str, project_id: str, permission: str) -> bool:
        """
        Проверяет, есть ли у пользователя указанное разрешение на уровне задач
        проекта (с учётом каскада project/workspace/org).

        Аргументы:
            user_id: Идентификатор пользователя.
            project_id: Идентификатор проекта, к задачам которого
                относится проверка.
            permission: Требуемое разрешение (например «tasks.read»).

        Возвращает:
            True, если разрешение есть, иначе False.
        """

    @abstractmethod
    async def require_permission(self, user_id: str, project_id: str, permission: str) -> None:
        """
        Проверяет разрешение и выбрасывает `InsufficientTaskPermissionsException`
        при отсутствии.
        """
