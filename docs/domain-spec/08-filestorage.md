# FileStorage BC — Спецификация

> Путь: `app/context/filestorage/domain`
> Исходные требования: §8 (Файлы и документы)

## Контекст

FileStorage BC отвечает за загрузку, хранение, скачивание файлов, папки, квоты, сканирование на вирусы, совместный доступ, публичные ссылки, блокировки и версионирование. Хранилище привязывается к workspace или организации. Файлы могут быть привязаны к задачам, проектам и другим сущностям через opaque ID.

---

## Принципы расширяемости

1. **StorageOwnerType — enum** — вместо магической строки `owner_type: str`. Новые типы владельцев = значение enum.
2. **FileType — расширяемый enum** — новые типы файлов (CODE, AUDIO, FONT, 3D_MODEL) = значение enum. Определяется по MIME-типу на app-слое.
3. **FilePermission — entity** — вместо enum. Привязка разрешения к конкретному пользователю/роли. Новые уровни доступа = расширение.
4. **StorageConfig — VO group** — вместо нетипизированного `config: dict`. Типизированные настройки провайдера. Новые провайдеры = новая конфигурация.
5. **Папки — entity** — иерархия файлов через `parent_folder_id`. Новые типы контейнеров (проект, пространство) = расширение.
6. **Публичные ссылки — entity** — `PublicShareLink` с токеном и настройками. Новые режимы шеринга = расширение.
7. **Блокировки — entity** — `FileLock` для совместного редактирования. Новые типы блокировок = расширение.

---

## Value Objects

| VO | Тип | Описание | Исходное требование |
|---|---|---|---|
| `FileType` | Enum | `IMAGE`, `VIDEO`, `PDF`, `OFFICE`, `ARCHIVE`, `AUDIO`, `CODE`, `FONT`, `SPREADSHEET`, `PRESENTATION`, `3D_MODEL`, `OTHER` | §8.1 |
| `FileSize` | frozen dataclass | value: int (≥0, bytes) | §8.1 |
| `VirusScanStatus` | Enum | `PENDING`, `CLEAN`, `INFECTED`, `SKIPPED`, `ERROR` | §8.1 |
| `FileAccessLevel` | Enum | `VIEW`, `COMMENT`, `EDIT`, `ADMIN`, `OWNER` | §8.1 |
| `StorageProvider` | Enum | `S3`, `LOCAL`, `MINIO`, `GCS`, `AZURE_BLOB` | §8.1 |
| `StorageOwnerType` | Enum | `WORKSPACE`, `ORGANIZATION` | §8.1 |
| `FileStatus` | Enum | `ACTIVE`, `TRASHED`, `DELETED` | §8.1 |
| `FolderType` | Enum | `REGULAR`, `PROJECT`, `SHARED`, `SYSTEM` | §8.2 |
| `AccentColor` | frozen dataclass | hex: str (validated #RRGGBB) | §8.2 |
| `RichText` | frozen dataclass | content: str, format: RichTextFormat | §8.2 |
| `RichTextFormat` | Enum | `MARKDOWN`, `WYSIWYG` | §8.2 |

> **`FileType`** — определяется по MIME-типу на app-слое. Новые типы (например, `CAD`, `GIS`, `DATABASE`) = значение enum. `OTHER` — fallback для неизвестных типов.
>
> **`FileAccessLevel`** — замена `FilePermission` enum. `COMMENT` — может комментировать (для документов), `OWNER` — владелец файла. Новые уровни доступа = значение enum.
>
> **`StorageProvider`** — `GCS` (Google Cloud Storage), `AZURE_BLOB` — новые провайдеры = значение enum.
>
> **`StorageOwnerType`** — enum вместо `owner_type: str`. Новые типы владельцев (например, `PROJECT`) = значение enum.
>
> **`FileStatus`** — жизненный цикл файла. `TRASHED` — в корзине (soft delete), `DELETED` — окончательно удалён. Файл в корзине можно восстановить.
>
> **`FolderType`** — `REGULAR` — обычная папка, `PROJECT` — привязана к проекту (auto-created), `SHARED` — расшаренная папка, `SYSTEM` — системная (не удаляется).

### StorageConfig (VO group)

| VO | Тип | Описание | Исходное требование |
|---|---|---|---|
| `StorageConfig` | frozen dataclass | endpoint: str \| None, bucket: str \| None, region: str \| None, access_key_ref: str \| None, secret_key_ref: str \| None, custom_params: dict[str, str] \| None | §8.1 |

> **`StorageConfig`** — типизированная замена `config: dict`. Credentials хранятся по ссылкам (ref), не в открытом виде. `custom_params` — для провайдер-специфичных настроек. Новые провайдеры могут добавлять свои параметры через `custom_params`.
>
> **Безопасность** — `access_key_ref` / `secret_key_ref` — ссылки на секреты в vault (HashiCorp Vault, AWS Secrets Manager), не сами значения. App-слой разрешает ссылки при подключении к провайдеру.

## Entities

| Сущность | Поля | Описание | Исходное требование |
|---|---|---|---|
| `FileVersion` | version_number: int, storage_path: str, size_bytes: int, uploader_id: Id, change_summary: str \| None, uploaded_at: datetime | Версия файла | §8.1 |
| `FilePermissionEntry` | user_id: Id \| None, team_id: Id \| None (opaque), access_level: FileAccessLevel, granted_by: Id, granted_at: datetime | Разрешение на файл/папку | §8.1 |
| `Folder` | id: Id, name: str, folder_type: FolderType, parent_folder_id: Id \| None, color: AccentColor \| None, description: str \| None, owner_id: Id, workspace_id: Id (opaque), is_pinned: bool, created_at: datetime, updated_at: datetime | Папка/директория | §8.2 |
| `PublicShareLink` | id: Id, token: str, password_hash: str \| None, expires_at: datetime \| None, access_level: FileAccessLevel, allow_download: bool, max_uses: int \| None, current_uses: int, created_by: Id, created_at: datetime | Публичная ссылка на файл/папку | §8.1 |
| `FileLock` | id: Id, locked_by: Id, locked_at: datetime, expires_at: datetime \| None, reason: str \| None | Блокировка файла | §8.1 |
| `FileTag` | id: Id, name: str, color: AccentColor \| None | Тег/метка файла | §8.2 |

> **`FileVersion`** — добавлены `uploader_id` (кто загрузил версию), `change_summary` (описание изменений, как commit message). Каждая версия отслеживает автора.
>
> **`FilePermissionEntry`** — entity вместо enum `FilePermission`. Привязка разрешения к конкретному пользователю или команде. `user_id=None` + `team_id` — разрешение для всей команды. `granted_by` — кто выдал разрешение. Новые уровни доступа = значение в `FileAccessLevel` enum.
>
> **`Folder`** — иерархия файлов. `parent_folder_id` — ссылка на родительскую папку (null = корень). `FolderType.PROJECT` — автоматически создаётся при создании проекта (app-layer handler). `FolderType.SYSTEM` — системные папки (например, "Trash").
>
> **`PublicShareLink`** — публичная ссылка с токеном для доступа без авторизации. `password_hash` — опциональный пароль. `expires_at` — срок действия. `max_uses` — ограничение количества скачиваний. Новые режимы шеринга = расширение entity.
>
> **`FileLock`** — блокировка файла для совместного редактирования. `expires_at` — автоснятие блокировки. `reason` — причина блокировки. Только locker может снять блокировку (или admin/owner).
>
> **`FileTag`** — теги для категоризации файлов. Уникальны по имени в рамках workspace. Новые теги = новая запись, не правка домена.

## Domain Events

| Событие | Поля | Описание | Исходное требование |
|---|---|---|---|
| `FileUploaded` | file_id, uploader_id, workspace_id, file_type, size_bytes | Файл загружен | §8.1 |
| `FileDownloaded` | file_id, downloader_id | Файл скачан | §8.1 |
| `FileTrashed` | file_id, trashed_by | Файл перемещён в корзину | §8.1 |
| `FileRestored` | file_id, restored_by | Файл восстановлен из корзины | §8.1 |
| `FileDeleted` | file_id | Файл окончательно удалён | §8.1 |
| `FileMoved` | file_id, old_folder_id, new_folder_id | Файл перемещён | §8.1 |
| `FileRenamed` | file_id, old_name, new_name | Файл переименован | §8.1 |
| `FilePermissionGranted` | file_id, user_id \| None, team_id \| None, access_level | Разрешение выдано | §8.1 |
| `FilePermissionRevoked` | file_id, user_id \| None, team_id \| None | Разрешение отозвано | §8.1 |
| `FileVersionCreated` | file_id, version_number, uploader_id | Новая версия файла | §8.1 |
| `FileLocked` | file_id, locked_by | Файл заблокирован | §8.1 |
| `FileUnlocked` | file_id, unlocked_by | Файл разблокирован | §8.1 |
| `PublicShareLinkCreated` | file_id, link_id | Публичная ссылка создана | §8.1 |
| `PublicShareLinkRevoked` | file_id, link_id | Публичная ссылка отозвана | §8.1 |
| `PublicShareLinkAccessed` | file_id, link_id | Переход по публичной ссылке | §8.1 |
| `FileTagAdded` | file_id, tag_name | Тег добавлен | §8.2 |
| `FileTagRemoved` | file_id, tag_name | Тег удалён | §8.2 |
| `FolderCreated` | folder_id, workspace_id, folder_type | Папка создана | §8.2 |
| `FolderUpdated` | folder_id, changed_fields: list[str] | Папка обновлена | §8.2 |
| `FolderDeleted` | folder_id | Папка удалена | §8.2 |
| `FolderMoved` | folder_id, old_parent_id, new_parent_id | Папка перемещена | §8.2 |
| `StorageQuotaApproaching` | storage_id, used_percent | Квота приближается (≥90%) | §8.1 |
| `StorageQuotaExceeded` | storage_id, used_percent | Квота превышена | §8.1 |
| `VirusDetected` | file_id, virus_name \| None | Вирус обнаружен | §8.1 |
| `VirusScanCompleted` | file_id, scan_status | Сканирование завершено | §8.1 |

> **`FileTrashed`/`FileRestored`** — двухфазное удаление. Сначала в корзину (soft delete), потом окончательное удаление. Файл в корзине не занимает квоту (опционально, настраивается).
>
> **`FileMoved`** — перемещение между папками. Позволяет отслеживать реорганизацию файлов.
>
> **`FilePermissionGranted`/`Revoked`** — детализация шеринга. Позволяет уведомлять пользователя о новом доступе.
>
> **`PublicShareLinkAccessed`** — отслеживание использования публичных ссылок. `current_uses` инкрементируется.
>
> **`VirusDetected.virus_name`** — опциональное имя обнаруженного вируса для информирования администратора.

## Exceptions

| Исключение | Описание |
|---|---|
| `FileNotFoundException` | Файл не найден |
| `FileTrashedException` | Файл в корзине |
| `FileLockedException` | Файл заблокирован другим пользователем |
| `FileTooLargeException` | Файл превышает лимит размера |
| `FileTypeNotAllowedException` | Тип файла не разрешён |
| `StorageQuotaExceededException` | Квота хранилища превышена |
| `VirusDetectedException` | В файле обнаружен вирус |
| `FilePermissionDeniedException` | Нет доступа к файлу |
| `StorageNotFoundException` | Хранилище не найдено |
| `FolderNotFoundException` | Папка не найдена |
| `FolderNotEmptyException` | Папка не пуста, нельзя удалить |
| `CircularFolderReferenceException` | Циклическая ссылка при перемещении папки |
| `PublicShareLinkNotFoundException` | Публичная ссылка не найдена |
| `PublicShareLinkExpiredException` | Срок действия ссылки истёк |
| `PublicShareLinkMaxUsesExceededException` | Превышен лимит использований ссылки |
| `InvalidSharePasswordException` | Неверный пароль ссылки |
| `DuplicateFileTagException` | Тег с таким именем уже существует |
| `CannotLockFileException` | Нельзя заблокировать файл |
| `CannotUnlockFileException` | Нельзя разблокировать чужую блокировку |
| `MaxFolderDepthExceededException` | Превышена максимальная глубина вложенности папок |

## Aggregates

### File (Aggregate Root)

Поля:
- name: str
- original_name: str
- file_type: FileType
- size: FileSize
- mime_type: str
- storage_id: Id (opaque, ссылка на Storage AR)
- storage_path: str
- folder_id: Id | None (opaque, ссылка на Folder entity)
- uploader_id: Id
- workspace_id: Id (opaque, из Workspace BC)
- owner_id: Id
- description: str | None
- scan_status: VirusScanStatus
- status: FileStatus (ACTIVE / TRASHED / DELETED)
- permissions: list[FilePermissionEntry]
- versions: list[FileVersion]
- lock: FileLock | None
- tags: list[FileTag]
- share_links: list[PublicShareLink]
- preview_path: str | None (путь к превью/thumbnail)
- is_shared: bool
- created_at: datetime
- updated_at: datetime

Методы:
- `create(name, original_name, file_type, size, mime_type, storage_id, storage_path, uploader_id, workspace_id, folder_id=None)` → `File` (factory, owner_id=uploader_id)
- `rename(new_name)`
- `move(new_folder_id)`
- `update_description(description)`
- `trash(trashed_by)` — перемещение в корзину (status=TRASHED)
- `restore(restored_by)` — восстановление из корзины (status=ACTIVE)
- `delete_permanently()` — окончательное удаление (status=DELETED)
- `mark_scan_clean()`
- `mark_scan_infected()`
- `mark_scan_error()`
- `add_version(storage_path, size_bytes, uploader_id, change_summary=None)` → `FileVersion`
- `grant_permission(user_id=None, team_id=None, access_level, granted_by)` — хотя бы один из user_id/team_id
- `revoke_permission(user_id=None, team_id=None)`
- `lock(locked_by, reason=None, expires_at=None)`
- `unlock(unlocked_by)` — только locker, owner или admin
- `add_tag(tag: FileTag)`
- `remove_tag(tag_name)`
- `create_share_link(access_level, created_by, password=None, expires_at=None, max_uses=None)` → `PublicShareLink`
- `revoke_share_link(link_id)`
- `access_share_link(token, password=None)` — инкремент current_uses, проверка expires_at и max_uses
- `set_preview(preview_path)`

Инварианты:
- Размер файла > 0
- Файл с `VirusScanStatus.INFECTED` недоступен для скачивания
- Файл с `FileStatus.TRASHED` нельзя редактировать, только восстановить или удалить окончательно
- Заблокированный файл нельзя редактировать (кроме locker)
- `FilePermissionEntry` — хотя бы один из user_id/team_id заполнен
- Публичная ссылка с `max_uses` — `current_uses` ≤ `max_uses`
- Публичная ссылка с `expires_at` — недоступна после истечения
- Ограничения на типы и размеры файлов — из Workspace BC / Organization BC (проверка на app-слое)
- Теги уникальны по имени в рамках файла

### Storage (Aggregate Root)

Поля:
- owner_type: StorageOwnerType
- owner_id: Id (opaque, из Workspace BC или Organization BC)
- provider: StorageProvider
- config: StorageConfig
- max_bytes: int
- used_bytes: int
- allowed_file_types: list[FileType] | None — None = все типы
- max_file_size_bytes: int | None — None = без лимита
- is_encrypted: bool
- created_at: datetime
- updated_at: datetime

Методы:
- `create(owner_type, owner_id, provider, config, max_bytes)` → `Storage` (factory)
- `add_usage(bytes_count)` — проверяет квоту, выпускает `StorageQuotaApproaching` при ≥90%
- `remove_usage(bytes_count)`
- `update_config(config)`
- `update_quota(max_bytes)`
- `set_allowed_file_types(file_types)`
- `set_max_file_size(max_size_bytes)`
- `enable_encryption()`
- `disable_encryption()`

Инварианты:
- `used_bytes` ≤ `max_bytes` (иначе `StorageQuotaExceededException`)
- При достижении 90% квоты — событие `StorageQuotaApproaching`
- При превышении квоты — событие `StorageQuotaExceeded`
- `is_encrypted=True` — все новые файлы шифруются (провайдер-специфично, на infrastructure слое)
- `allowed_file_types` — если задано, загрузка файлов других типов отклоняется

### Folder (Aggregate Root)

Поля:
- name: str
- folder_type: FolderType
- parent_folder_id: Id | None (null = корень workspace)
- color: AccentColor | None
- description: str | None
- icon: str | None
- owner_id: Id
- workspace_id: Id (opaque, из Workspace BC)
- project_id: Id | None (opaque, из Project BC — для FolderType.PROJECT)
- is_pinned: bool
- is_shared: bool
- permissions: list[FilePermissionEntry]
- created_at: datetime
- updated_at: datetime

Методы:
- `create(name, workspace_id, owner_id, folder_type=REGULAR, parent_folder_id=None)` → `Folder` (factory)
- `create_project_folder(name, workspace_id, project_id, owner_id)` → `Folder` (factory, folder_type=PROJECT)
- `rename(new_name)`
- `move(new_parent_folder_id)` — проверка циклов на app-слое
- `update_description(description)`
- `pin()` / `unpin()`
- `share()` / `unshare()`
- `grant_permission(user_id=None, team_id=None, access_level, granted_by)`
- `revoke_permission(user_id=None, team_id=None)`
- `delete()` — только если пустая (проверка на app-слое через repository)

Инварианты:
- `FolderType.SYSTEM` нельзя удалить или переименовать
- `FolderType.PROJECT` привязана к `project_id`, создаётся/удаляется автоматически (app-layer handler)
- Циклы в иерархии папок проверяются на app-слое при `move()`
- Глубина вложенности ограничена (проверка на app-слое, например макс. 10 уровней)
- Папку можно удалить только если она пуста (нет файлов и подпапок)

## Repositories

| Репозиторий | Методы |
|---|---|
| `FileRepository` | `get_by_id`, `get_by_workspace`, `get_by_folder`, `get_by_uploader`, `get_by_owner`, `get_trashed_by_workspace`, `search_by_name`, `get_by_tag`, `get_by_type`, `count_by_workspace`, `sum_size_by_workspace` |
| `FolderRepository` | `get_by_id`, `get_by_workspace`, `get_by_parent`, `get_root_folders`, `get_by_project`, `get_by_type`, `search` |
| `StorageRepository` | `get_by_id`, `get_by_owner`, `get_by_owner_type` |

> **`FileRepository.get_trashed_by_workspace`** — файлы в корзине для отображения и очистки.
>
> **`FileRepository.get_by_tag`** — поиск файлов по тегу.
>
> **`FileRepository.sum_size_by_workspace`** — общий размер файлов для отображения использования хранилища.
>
> **`FolderRepository.get_by_project`** — папка проекта (FolderType.PROJECT) для автоматического создания при создании проекта.
>
> **`StorageRepository.get_by_owner_type`** — все хранилища определённого типа владельца (например, все workspace хранилища).
