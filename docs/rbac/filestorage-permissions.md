# Проверки разрешений в FileStorage Context

## Обзор механизма авторизации

FileStorage BC использует workspace-уровневую авторизацию через порт `WorkspacePermissionCheckerPort`, который делегирует в `WorkspaceMembershipProvider.has_permission` (outboard Workspace BC).

Каждое разрешение FileStorage имеет каскад в орг-роль:
`files.<perm>` (workspace) ← `workspaces.files.<perm>` (organization).

Поддерживаются wildcard-разрешения:
- `files.*` — полный доступ к файлам/папкам в workspace
- `storage.*` — управление хранилищем workspace
- `files.read` / `files.write` / `files.share` / `files.delete` / `files.admin` — конкретные

## Сводная таблица разрешений

### Workspace-разрешения

| Разрешение | Commands | Queries |
|---|---|---|
| `files.read` | — | `GetFile`, `GetFilesByWorkspace`, `GetFilesByFolder`, `GetTrashedFiles`, `SearchFiles`, `GetFileDownloadUrl`, `GetFolder`, `GetFoldersByWorkspace`, `GetSubfolders` |
| `files.write` | `UploadFile`, `RenameFile`, `MoveFile`, `UpdateFileDescription`, `TrashFile`, `RestoreFile`, `AddFileVersion`, `LockFile`, `AddFileTag`, `RemoveFileTag`, `CreateFolder`, `RenameFolder`, `MoveFolder`, `UpdateFolderDescription`, `PinFolder`, `UnpinFolder` | — |
| `files.share` | `GrantFilePermission`, `RevokeFilePermission`, `CreateShareLink`, `RevokeShareLink` | — |
| `files.delete` | `DeleteFile` (окончательно), `DeleteFolder` | — |
| `files.admin` | `MarkScanClean`, `MarkScanInfected`, `UnlockFile` (если caller не locker и не owner) | — |
| `storage.read` | — | `GetStorage`, `GetStorageByOwner` |
| `storage.admin` | `CreateStorage`, `UpdateStorageConfig`, `UpdateStorageQuota`, `SetStorageAllowedFileTypes`, `SetStorageMaxFileSize` | — |

### Кросс-BC (Organization) разрешения

| Разрешение | Покрывает в FileStorage |
|---|---|
| `workspaces.files.*` | Все `files.*` в workspace |
| `workspaces.files.read` | `files.read` |
| `workspaces.files.write` | `files.write` |
| `workspaces.files.share` | `files.share` |
| `workspaces.storage.*` | Все `storage.*` |

### Без проверки разрешений

| Endpoint | Описание |
|---|---|
| `POST /share-links/access/{token}` | Переход по публичной ссылке. Доступ контролируется через `password_hash`, `expires_at`, `max_uses` на entity `PublicShareLink`. |

## Системные роли (после seed)

| Роль | Разрешения FileStorage |
|---|---|
| **workspace.owner** | `ws.*` (включает `files.*`, `storage.*` через wildcard) |
| **workspace.admin** | `files.*`, `storage.*` |
| **workspace.manager** | `files.read`, `files.write`, `files.share`, `storage.read` |
| **workspace.member** | `files.read`, `files.write`, `storage.read` |
| **org.owner** | `org.*` + `workspaces.*` (cascade) |
| **org.admin** | `workspaces.files.*`, `workspaces.storage.*` |
| **org.moderator** | `workspaces.files.read`, `workspaces.files.write`, `workspaces.files.share`, `workspaces.storage.read` |
| **org.member** | `workspaces.files.read` |
