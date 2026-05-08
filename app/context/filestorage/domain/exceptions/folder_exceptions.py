from __future__ import annotations

from app.shared.domain.exceptions import BusinessRuleViolationException, EntityNotFoundException


class FolderNotFoundException(EntityNotFoundException):
    """Папка не найдена."""

    def __init__(self, id: object) -> None:
        super().__init__(entity_type="Folder", id=id)


class FolderNotEmptyException(BusinessRuleViolationException):
    """Папка не пуста, нельзя удалить."""

    def __init__(self) -> None:
        super().__init__(
            rule="FolderMustBeEmpty",
            message="Папка не пуста, нельзя удалить",
        )


class CircularFolderReferenceException(BusinessRuleViolationException):
    """Циклическая ссылка при перемещении папки."""

    def __init__(self) -> None:
        super().__init__(
            rule="NoCircularFolderReference",
            message="Циклическая ссылка при перемещении папки",
        )


class MaxFolderDepthExceededException(BusinessRuleViolationException):
    """Превышена максимальная глубина вложенности папок."""

    def __init__(self, max_depth: int = 0) -> None:
        super().__init__(
            rule="MaxFolderDepth",
            message=f"Превышена максимальная глубина вложенности папок{f' (макс: {max_depth})' if max_depth else ''}",
        )


class SystemFolderModifyException(BusinessRuleViolationException):
    """Системную папку нельзя изменять."""

    def __init__(self) -> None:
        super().__init__(
            rule="SystemFolderImmutable",
            message="Системную папку нельзя изменять",
        )


class FolderPermissionTargetRequiredException(BusinessRuleViolationException):
    """Хотя бы один из user_id/team_id должен быть заполнен."""

    def __init__(self) -> None:
        super().__init__(
            rule="PermissionTargetRequired",
            message="Хотя бы один из user_id/team_id должен быть заполнен",
        )
