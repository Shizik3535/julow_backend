"""Command-handlers FileStorage BC."""
from app.context.filestorage.application.commands.upload_file import (
    UploadFileCommand,
    UploadFileHandler,
)
from app.context.filestorage.application.commands.update_file import (
    RenameFileCommand,
    RenameFileHandler,
    MoveFileCommand,
    MoveFileHandler,
    UpdateFileDescriptionCommand,
    UpdateFileDescriptionHandler,
)
from app.context.filestorage.application.commands.lifecycle_file import (
    TrashFileCommand,
    TrashFileHandler,
    RestoreFileCommand,
    RestoreFileHandler,
    DeleteFileCommand,
    DeleteFileHandler,
)
from app.context.filestorage.application.commands.add_file_version import (
    AddFileVersionCommand,
    AddFileVersionHandler,
)
from app.context.filestorage.application.commands.manage_file_permission import (
    GrantFilePermissionCommand,
    GrantFilePermissionHandler,
    RevokeFilePermissionCommand,
    RevokeFilePermissionHandler,
)
from app.context.filestorage.application.commands.lock_file import (
    LockFileCommand,
    LockFileHandler,
    UnlockFileCommand,
    UnlockFileHandler,
)
from app.context.filestorage.application.commands.manage_file_tag import (
    AddFileTagCommand,
    AddFileTagHandler,
    RemoveFileTagCommand,
    RemoveFileTagHandler,
)
from app.context.filestorage.application.commands.manage_share_link import (
    CreateShareLinkCommand,
    CreateShareLinkHandler,
    RevokeShareLinkCommand,
    RevokeShareLinkHandler,
    AccessShareLinkCommand,
    AccessShareLinkHandler,
)
from app.context.filestorage.application.commands.virus_scan import (
    MarkScanCleanCommand,
    MarkScanCleanHandler,
    MarkScanInfectedCommand,
    MarkScanInfectedHandler,
)
from app.context.filestorage.application.commands.create_folder import (
    CreateFolderCommand,
    CreateFolderHandler,
)
from app.context.filestorage.application.commands.update_folder import (
    RenameFolderCommand,
    RenameFolderHandler,
    MoveFolderCommand,
    MoveFolderHandler,
    UpdateFolderDescriptionCommand,
    UpdateFolderDescriptionHandler,
    PinFolderCommand,
    PinFolderHandler,
    UnpinFolderCommand,
    UnpinFolderHandler,
)
from app.context.filestorage.application.commands.delete_folder import (
    DeleteFolderCommand,
    DeleteFolderHandler,
)
from app.context.filestorage.application.commands.create_storage import (
    CreateStorageCommand,
    CreateStorageHandler,
)
from app.context.filestorage.application.commands.update_storage import (
    UpdateStorageConfigCommand,
    UpdateStorageConfigHandler,
    UpdateStorageQuotaCommand,
    UpdateStorageQuotaHandler,
    SetStorageAllowedFileTypesCommand,
    SetStorageAllowedFileTypesHandler,
    SetStorageMaxFileSizeCommand,
    SetStorageMaxFileSizeHandler,
)

__all__ = [
    "UploadFileCommand",
    "UploadFileHandler",
    "RenameFileCommand",
    "RenameFileHandler",
    "MoveFileCommand",
    "MoveFileHandler",
    "UpdateFileDescriptionCommand",
    "UpdateFileDescriptionHandler",
    "TrashFileCommand",
    "TrashFileHandler",
    "RestoreFileCommand",
    "RestoreFileHandler",
    "DeleteFileCommand",
    "DeleteFileHandler",
    "AddFileVersionCommand",
    "AddFileVersionHandler",
    "GrantFilePermissionCommand",
    "GrantFilePermissionHandler",
    "RevokeFilePermissionCommand",
    "RevokeFilePermissionHandler",
    "LockFileCommand",
    "LockFileHandler",
    "UnlockFileCommand",
    "UnlockFileHandler",
    "AddFileTagCommand",
    "AddFileTagHandler",
    "RemoveFileTagCommand",
    "RemoveFileTagHandler",
    "CreateShareLinkCommand",
    "CreateShareLinkHandler",
    "RevokeShareLinkCommand",
    "RevokeShareLinkHandler",
    "AccessShareLinkCommand",
    "AccessShareLinkHandler",
    "MarkScanCleanCommand",
    "MarkScanCleanHandler",
    "MarkScanInfectedCommand",
    "MarkScanInfectedHandler",
    "CreateFolderCommand",
    "CreateFolderHandler",
    "RenameFolderCommand",
    "RenameFolderHandler",
    "MoveFolderCommand",
    "MoveFolderHandler",
    "UpdateFolderDescriptionCommand",
    "UpdateFolderDescriptionHandler",
    "PinFolderCommand",
    "PinFolderHandler",
    "UnpinFolderCommand",
    "UnpinFolderHandler",
    "DeleteFolderCommand",
    "DeleteFolderHandler",
    "CreateStorageCommand",
    "CreateStorageHandler",
    "UpdateStorageConfigCommand",
    "UpdateStorageConfigHandler",
    "UpdateStorageQuotaCommand",
    "UpdateStorageQuotaHandler",
    "SetStorageAllowedFileTypesCommand",
    "SetStorageAllowedFileTypesHandler",
    "SetStorageMaxFileSizeCommand",
    "SetStorageMaxFileSizeHandler",
]
