from __future__ import annotations

from app.shared.domain.base_exceptions import DomainException
from app.shared.domain.exceptions import BusinessRuleViolationException, EntityNotFoundException


class FileNotFoundException(EntityNotFoundException):
    """Файл не найден."""

    def __init__(self, id: object) -> None:
        super().__init__(entity_type="File", id=id)


class FileTrashedException(DomainException):
    """Файл в корзине."""

    def __init__(self) -> None:
        super().__init__("Файл в корзине, действие невозможно")


class FileLockedException(DomainException):
    """Файл заблокирован другим пользователем."""

    def __init__(self) -> None:
        super().__init__("Файл заблокирован другим пользователем")


class FileTooLargeException(BusinessRuleViolationException):
    """Файл превышает лимит размера."""

    def __init__(self, max_size: int = 0, actual_size: int = 0) -> None:
        super().__init__(
            rule="MaxFileSize",
            message=f"Файл превышает лимит размера{f' (макс: {max_size}, факт: {actual_size})' if max_size else ''}",
        )


class FileTypeNotAllowedException(BusinessRuleViolationException):
    """Тип файла не разрешён."""

    def __init__(self, file_type: str = "") -> None:
        super().__init__(
            rule="AllowedFileTypes",
            message=f"Тип файла не разрешён{f': {file_type}' if file_type else ''}",
        )


class VirusDetectedException(BusinessRuleViolationException):
    """В файле обнаружен вирус."""

    def __init__(self, virus_name: str = "") -> None:
        super().__init__(
            rule="VirusFree",
            message=f"В файле обнаружен вирус{f': {virus_name}' if virus_name else ''}",
        )


class FilePermissionDeniedException(DomainException):
    """Нет доступа к файлу."""

    def __init__(self) -> None:
        super().__init__("Нет доступа к файлу")


class PublicShareLinkNotFoundException(EntityNotFoundException):
    """Публичная ссылка не найдена."""

    def __init__(self, id: object) -> None:
        super().__init__(entity_type="PublicShareLink", id=id)


class PublicShareLinkExpiredException(DomainException):
    """Срок действия ссылки истёк."""

    def __init__(self) -> None:
        super().__init__("Срок действия публичной ссылки истёк")


class PublicShareLinkMaxUsesExceededException(DomainException):
    """Превышен лимит использований ссылки."""

    def __init__(self) -> None:
        super().__init__("Превышен лимит использований публичной ссылки")


class InvalidSharePasswordException(DomainException):
    """Неверный пароль ссылки."""

    def __init__(self) -> None:
        super().__init__("Неверный пароль публичной ссылки")


class DuplicateFileTagException(BusinessRuleViolationException):
    """Тег с таким именем уже существует."""

    def __init__(self, name: str = "") -> None:
        super().__init__(
            rule="UniqueFileTag",
            message=f"Тег с таким именем уже существует{f': {name}' if name else ''}",
        )


class CannotLockFileException(BusinessRuleViolationException):
    """Нельзя заблокировать файл."""

    def __init__(self, reason: str = "") -> None:
        super().__init__(
            rule="CanLockFile",
            message=f"Нельзя заблокировать файл{f': {reason}' if reason else ''}",
        )


class CannotUnlockFileException(BusinessRuleViolationException):
    """Нельзя разблокировать чужую блокировку."""

    def __init__(self) -> None:
        super().__init__(
            rule="CanUnlockFile",
            message="Нельзя разблокировать чужую блокировку",
        )
