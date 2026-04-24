# 08. File Management — Файлы и документы

## Обзор

Контекст управления файлами отвечает за загрузку, хранение, превью и доступ к файлам. Файлы привязываются к задачам, комментариям и сообщениям. Хранилище — S3-совместимое (встроенное или пользовательское для Business/Enterprise).

---

## Принципы расширяемости

1. **StorageOwnerType — enum** — `WORKSPACE`, `ORGANIZATION`. Новые типы владельцев = значение enum.
2. **FileType — расширяемый enum** — `IMAGE`, `VIDEO`, `PDF`, `OFFICE`, `ARCHIVE`, `AUDIO`, `CODE`, `FONT`, `SPREADSHEET`, `PRESENTATION`, `3D_MODEL`, `OTHER`. По MIME-type на app-слое.
3. **FilePermissionEntry — entity** — разрешение на файл/папку к конкретному пользователю/команде.
4. **StorageConfig — VO group** — типизированные настройки провайдера. Credentials по ref, не открытым текстом.
5. **Папки — entity** — иерархия через `parent_folder_id`. `FolderType`: `REGULAR`, `PROJECT`, `SHARED`, `SYSTEM`.
6. **PublicShareLink — entity** — токен, пароль, expires, max_uses.
7. **FileLock — entity** — блокировка для совместного редактирования.

---

## 1. Функциональные требования

### 1.1. Управление файлами

| Требование | Free | Start | Business | Enterprise |
|-----------|------|-------|----------|------------|
| Хранилище | 1 GB | 10 GB | 100 GB | ∞ (свой S3) |
| Макс. размер файла | 25 MB | 100 MB | 500 MB | Настраиваемый |
| Загрузка (drag-n-drop) | ✅ | ✅ | ✅ | ✅ |
| Превью файлов | ✅ | ✅ | ✅ | ✅ |
| Скачивание | ✅ | ✅ | ✅ | ✅ |
| Совместный доступ | ✅ | ✅ | ✅ | ✅ |
| Ограничения типов файлов | ❌ | ❌ | ✅ | ✅ |
| Сканирование на вирусы | ❌ | ❌ | ✅ | ✅ |
| Версионирование файлов | ❌ | ❌ | ✅ | ✅ |
| Квоты на хранилище | ✅ | ✅ | ✅ | Настраиваемый |

### Поддерживаемые форматы превью

| Категория | Форматы |
|-----------|---------|
| Изображения | PNG, JPG, JPEG, GIF, WEBP, SVG, BMP, ICO |
| Документы | PDF |
| Офис | DOCX, XLSX, PPTX (через LibreOffice/конвертация) |
| Видео | MP4, WEBM (первый кадр как thumbnail) |
| Аудио | MP3, WAV, OGG (waveform preview) |
| Код | TXT, MD, JSON, XML, YAML, CSV |
| Архивы | ZIP, TAR.GZ (список содержимого) |

### Запрещённые типы (по умолчанию, настраиваемо)

- Исполняемые: .exe, .bat, .cmd, .sh, .msi, .dll
- Скрипты: .js, .vbs, .ps1 (настраиваемо для Enterprise)

---

## 2. Доменная модель

### Value Objects

| VO | Тип | Описание |
|---|---|---|
| `FileType` | Enum | `IMAGE`, `VIDEO`, `PDF`, `OFFICE`, `ARCHIVE`, `AUDIO`, `CODE`, `FONT`, `SPREADSHEET`, `PRESENTATION`, `3D_MODEL`, `OTHER` |
| `FileStatus` | Enum | `ACTIVE`, `TRASHED`, `DELETED` |
| `FileSize` | frozen dataclass | value: int (≥0, bytes) |
| `VirusScanStatus` | Enum | `PENDING`, `CLEAN`, `INFECTED`, `SKIPPED`, `ERROR` |
| `FileAccessLevel` | Enum | `VIEW`, `COMMENT`, `EDIT`, `ADMIN`, `OWNER` |
| `StorageProvider` | Enum | `S3`, `LOCAL`, `MINIO`, `GCS`, `AZURE_BLOB` |
| `StorageOwnerType` | Enum | `WORKSPACE`, `ORGANIZATION` |
| `FolderType` | Enum | `REGULAR`, `PROJECT`, `SHARED`, `SYSTEM` |
| `AccentColor` | frozen dataclass | hex: str (validated `#RRGGBB`) |

> **`FileType`** — по MIME-type на app-слое. `OTHER` — fallback.
>
> **`FileStatus`** — `TRASHED` = корзина (soft delete), `DELETED` = окончательно. Файл из корзины можно восстановить.
>
> **`FolderType`** — `PROJECT` = auto-created при создании проекта, `SYSTEM` = не удаляется.

#### VO Groups

```python
class StorageConfig:
    endpoint: str | None
    bucket: str | None
    region: str | None
    access_key_ref: str | None   # ссылка на секрет в vault
    secret_key_ref: str | None   # ссылка на секрет в vault
    custom_params: dict[str, str] | None
```

> Credentials хранятся по ссылкам (ref), не в открытом виде. App-слой разрешает ссылки при подключении.

### Entities

| Сущность | Поля | Описание |
|---|---|---|
| `FileVersion` | version_number, storage_path, size_bytes, uploader_id, change_summary: str \| None, uploaded_at | Версия файла |
| `FilePermissionEntry` | user_id: Id \| None, team_id: Id \| None (opaque), access_level: FileAccessLevel, granted_by, granted_at | Разрешение на файл/папку |
| `Folder` | id, name, folder_type: FolderType, parent_folder_id: Id \| None, color: AccentColor \| None, description, owner_id, workspace_id, project_id: Id \| None, is_pinned, is_shared, permissions: list[FilePermissionEntry] | Папка/директория |
| `PublicShareLink` | id, token, password_hash: str \| None, expires_at \| None, access_level: FileAccessLevel, allow_download, max_uses: int \| None, current_uses, created_by | Публичная ссылка |
| `FileLock` | id, locked_by, locked_at, expires_at \| None, reason: str \| None | Блокировка файла |
| `FileTag` | id, name, color: AccentColor \| None | Тег файла |

> **`FilePermissionEntry`** — хотя бы один из user_id/team_id заполнен. `granted_by` — аудит.
>
> **`PublicShareLink`** — `max_uses` ограничивает скачивания. `password_hash` — опциональный пароль.
>
> **`FileLock`** — `expires_at` для автоснятия. Только locker/owner/admin может снять.

### Aggregates

#### File (Aggregate Root)

Поля:
- name: str
- original_name: str
- file_type: FileType
- size: FileSize
- mime_type: str
- storage_id: Id (opaque, ссылка на Storage AR)
- storage_path: str
- folder_id: Id | None (ссылка на Folder)
- uploader_id: Id
- workspace_id: Id (opaque)
- owner_id: Id
- description: str | None
- scan_status: VirusScanStatus
- status: FileStatus
- permissions: list[FilePermissionEntry]
- versions: list[FileVersion]
- lock: FileLock | None
- tags: list[FileTag]
- share_links: list[PublicShareLink]
- preview_path: str | None
- is_shared: bool
- metadata: dict — exif, dimensions, duration
- created_at: datetime
- updated_at: datetime

Методы:
- `create(name, original_name, file_type, size, mime_type, storage_id, storage_path, uploader_id, workspace_id, folder_id=None)` → `File`
- `rename(new_name)` / `move(new_folder_id)` / `update_description(description)`
- `trash(trashed_by)` / `restore(restored_by)` / `delete_permanently()`
- `mark_scan_clean()` / `mark_scan_infected()` / `mark_scan_error()`
- `add_version(storage_path, size_bytes, uploader_id, change_summary=None)`
- `grant_permission(user_id, team_id, access_level, granted_by)` / `revoke_permission(user_id, team_id)`
- `lock(locked_by, reason, expires_at)` / `unlock(unlocked_by)`
- `add_tag(tag)` / `remove_tag(tag_name)`
- `create_share_link(access_level, created_by, password, expires_at, max_uses)` / `revoke_share_link(link_id)`
- `access_share_link(token, password)` — инкремент current_uses
- `set_preview(preview_path)`

Инварианты:
- Размер > 0
- `INFECTED` — недоступен для скачивания
- `TRASHED` — нельзя редактировать, только restore или delete
- Заблокированный — нельзя редактировать (кроме locker)
- `FilePermissionEntry` — хотя бы один из user_id/team_id
- `PublicShareLink`: current_uses ≤ max_uses, expires_at
- Теги уникальны по имени в рамках файла

#### Storage (Aggregate Root)

Поля:
- owner_type: StorageOwnerType
- owner_id: Id (opaque)
- provider: StorageProvider
- config: StorageConfig
- max_bytes: int
- used_bytes: int
- allowed_file_types: list[FileType] | None — None = все
- max_file_size_bytes: int | None
- is_encrypted: bool
- created_at: datetime
- updated_at: datetime

Методы:
- `create(owner_type, owner_id, provider, config, max_bytes)` → `Storage`
- `add_usage(bytes_count)` — квота, событие при ≥90%
- `remove_usage(bytes_count)`
- `update_config(config)` / `update_quota(max_bytes)`
- `set_allowed_file_types(file_types)` / `set_max_file_size(max_size_bytes)`
- `enable_encryption()` / `disable_encryption()`

Инварианты:
- `used_bytes` ≤ `max_bytes`
- При ≥90% — `StorageQuotaApproaching`
- `allowed_file_types` — загрузка других типов отклоняется

#### Folder (Aggregate Root)

Поля:
- name: str
- folder_type: FolderType
- parent_folder_id: Id | None (null = корень)
- color: AccentColor | None
- description: str | None
- icon: str | None
- owner_id: Id
- workspace_id: Id (opaque)
- project_id: Id | None (для PROJECT)
- is_pinned: bool
- is_shared: bool
- permissions: list[FilePermissionEntry]
- created_at: datetime
- updated_at: datetime

Методы:
- `create(name, workspace_id, owner_id, folder_type=REGULAR, parent_folder_id=None)` → `Folder`
- `create_project_folder(name, workspace_id, project_id, owner_id)` → `Folder` (PROJECT)
- `rename(new_name)` / `move(new_parent_folder_id)` / `update_description(description)`
- `pin()` / `unpin()` / `share()` / `unshare()`
- `grant_permission(...)` / `revoke_permission(...)`
- `delete()` — только если пустая

Инварианты:
- `SYSTEM` нельзя удалить/переименовать
- `PROJECT` привязана к project_id, auto-created
- Циклы в иерархии — проверка на app-слое
- Глубина вложенности ограничена (макс. 10 уровней)
- Удаление только пустой папки

---

## 3. Бизнес-правила

1. **Квоты**: при превышении квоты workspace — загрузка блокируется
2. **Макс. размер файла**: зависит от тарифа; при превышении — 413 Payload Too Large
3. **Запрещённые типы**: проверка расширения и MIME-type
4. **Вирусы**: файл доступен для скачивания только после прохождения проверки (Business/Enterprise)
5. **Вирусы infected**: файл удаляется автоматически, уведомление загрузившему
6. **Thumbnail**: генерируется асинхронно для изображений и PDF
7. **Превью**: доступен для поддерживаемых форматов; для остальных — только скачивание
8. **Версионирование**: при загрузке новой версии — старая сохраняется; parent_file_id ссылается на предыдущую
9. **Soft-delete**: файл помечается удалённым, физически удаляется через 30 дней
10. **Pre-signed URL**: для скачивания — генерируется pre-signed URL с TTL 15 минут
11. **Загрузка**: multipart upload для файлов > 5 MB
12. **Storage routing**: для organizational workspace с custom storage — файлы сохраняются в S3 организации
13. **Имя файла**: sanitize (убрать спецсимволы), UTF-8, максимум 255 символов

---

## 4. API Endpoints

### 4.1. Загрузка

```
POST /api/v1/workspaces/{ws_id}/files/upload
```

**Request (multipart/form-data):**
- `file` — бинарные данные файла
- `context_type` — task / comment / message / project
- `context_id` — UUID сущности

**Response (201):**
```json
{
  "id": "uuid",
  "name": "screenshot.png",
  "mime_type": "image/png",
  "size": 254320,
  "extension": "png",
  "category": "image",
  "preview_available": true,
  "thumbnail_url": "https://cdn.taskflow.com/thumb/...",
  "virus_scan_status": "pending",
  "version": 1,
  "created_at": "2025-01-15T10:00:00Z"
}
```

---

```
POST /api/v1/workspaces/{ws_id}/files/upload/multipart/init
```
*Инициализация multipart upload*

**Request:**
```json
{
  "name": "large-video.mp4",
  "mime_type": "video/mp4",
  "size": 104857600,
  "context_type": "task",
  "context_id": "task_uuid"
}
```

**Response (200):**
```json
{
  "upload_id": "multipart_upload_id",
  "file_id": "uuid",
  "parts": [
    {"part_number": 1, "upload_url": "https://s3.../part1?..."},
    {"part_number": 2, "upload_url": "https://s3.../part2?..."}
  ]
}
```

---

```
POST /api/v1/workspaces/{ws_id}/files/upload/multipart/complete
```

**Request:**
```json
{
  "upload_id": "multipart_upload_id",
  "file_id": "uuid",
  "parts": [
    {"part_number": 1, "etag": "etag1"},
    {"part_number": 2, "etag": "etag2"}
  ]
}
```

### 4.2. Скачивание и превью

```
GET /api/v1/workspaces/{ws_id}/files/{file_id}/download
```

**Response (302):** Redirect to pre-signed URL

---

```
GET /api/v1/workspaces/{ws_id}/files/{file_id}/preview
```

**Response (200):** Pre-signed URL или inline content (для текстовых файлов)

---

```
GET /api/v1/workspaces/{ws_id}/files/{file_id}/thumbnail
```

**Response (302):** Redirect to thumbnail pre-signed URL

### 4.3. Управление

```
GET /api/v1/workspaces/{ws_id}/files
```

**Query params:** `context_type`, `context_id`, `category`, `search`, `page`, `limit`, `sort_by`

---

```
GET /api/v1/workspaces/{ws_id}/files/{file_id}
```

---

```
DELETE /api/v1/workspaces/{ws_id}/files/{file_id}
```

---

```
POST /api/v1/workspaces/{ws_id}/files/{file_id}/new-version
```
*Загрузка новой версии (multipart/form-data)*

---

```
GET /api/v1/workspaces/{ws_id}/files/{file_id}/versions
```

### 4.4. Квоты

```
GET /api/v1/workspaces/{ws_id}/storage/quota
```

**Response (200):**
```json
{
  "used_bytes": 524288000,
  "total_bytes": 1073741824,
  "percentage": 48.8,
  "files_count": 342,
  "breakdown": {
    "image": {"count": 200, "size": 300000000},
    "document": {"count": 100, "size": 150000000},
    "video": {"count": 10, "size": 50000000},
    "other": {"count": 32, "size": 24288000}
  }
}
```

---

## 5. Схема БД

### Таблица: `files`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| id | UUID | PK | |
| workspace_id | UUID | FK → workspaces.id, NOT NULL | |
| uploader_id | UUID | FK → users.id, NOT NULL | |
| name | VARCHAR(255) | NOT NULL | Sanitized original name |
| storage_key | VARCHAR(500) | NOT NULL | Path in S3 |
| storage_integration_id | UUID | FK → storage_integrations.id, NULLABLE | |
| mime_type | VARCHAR(100) | NOT NULL | |
| size | BIGINT | NOT NULL | Bytes |
| extension | VARCHAR(20) | NOT NULL | |
| category | VARCHAR(20) | NOT NULL | |
| thumbnail_key | VARCHAR(500) | NULLABLE | |
| preview_available | BOOLEAN | NOT NULL, DEFAULT FALSE | |
| virus_scan_status | VARCHAR(20) | NOT NULL, DEFAULT 'skipped' | |
| virus_scan_at | TIMESTAMPTZ | NULLABLE | |
| version | INTEGER | NOT NULL, DEFAULT 1 | |
| parent_file_id | UUID | FK → files.id, NULLABLE | Previous version |
| metadata | JSONB | NOT NULL, DEFAULT '{}' | Dimensions, duration, etc. |
| context_type | VARCHAR(20) | NOT NULL | |
| context_id | UUID | NOT NULL | |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

**Индексы:**
- `idx_file_ws` — на `workspace_id`
- `idx_file_context` — на `(context_type, context_id)`
- `idx_file_uploader` — на `uploader_id`
- `idx_file_category` — на `(workspace_id, category)`
- `idx_file_parent` — на `parent_file_id`
- `idx_file_scan` — на `virus_scan_status` WHERE `virus_scan_status = 'pending'`

---

## 6. Доменные события

| Событие | Поля | Описание |
|---|---|---|
| `FileUploaded` | file_id, uploader_id, workspace_id, file_type, size_bytes | Файл загружен |
| `FileDownloaded` | file_id, downloader_id | Файл скачан |
| `FileTrashed` | file_id, trashed_by | В корзину |
| `FileRestored` | file_id, restored_by | Восстановлен |
| `FileDeleted` | file_id | Окончательно удалён |
| `FileMoved` | file_id, old_folder_id, new_folder_id | Перемещён |
| `FileRenamed` | file_id, old_name, new_name | Переименован |
| `FilePermissionGranted` | file_id, user_id \| None, team_id \| None, access_level | Разрешение выдано |
| `FilePermissionRevoked` | file_id, user_id \| None, team_id \| None | Разрешение отозвано |
| `FileVersionCreated` | file_id, version_number, uploader_id | Новая версия |
| `FileLocked` | file_id, locked_by | Заблокирован |
| `FileUnlocked` | file_id, unlocked_by | Разблокирован |
| `PublicShareLinkCreated` | file_id, link_id | Публичная ссылка создана |
| `PublicShareLinkRevoked` | file_id, link_id | Ссылка отозвана |
| `PublicShareLinkAccessed` | file_id, link_id | Переход по ссылке |
| `FileTagAdded` | file_id, tag_name | Тег добавлен |
| `FileTagRemoved` | file_id, tag_name | Тег удалён |
| `FolderCreated` | folder_id, workspace_id, folder_type | Папка создана |
| `FolderUpdated` | folder_id, changed_fields: list[str] | Папка обновлена |
| `FolderDeleted` | folder_id | Папка удалена |
| `FolderMoved` | folder_id, old_parent_id, new_parent_id | Папка перемещена |
| `StorageQuotaApproaching` | storage_id, used_percent | Квота ≥90% |
| `StorageQuotaExceeded` | storage_id, used_percent | Квота превышена |
| `VirusDetected` | file_id, virus_name \| None | Вирус обнаружен |
| `VirusScanCompleted` | file_id, scan_status | Сканирование завершено |

---

## 7. Exceptions

| Исключение | Описание |
|---|---|
| `FileNotFoundException` | Файл не найден |
| `FileTrashedException` | Файл в корзине |
| `FileLockedException` | Файл заблокирован другим пользователем |
| `FileTooLargeException` | Превышен лимит размера |
| `FileTypeNotAllowedException` | Тип файла не разрешён |
| `StorageQuotaExceededException` | Квота превышена |
| `VirusDetectedException` | Вирус обнаружен |
| `FilePermissionDeniedException` | Нет доступа |
| `StorageNotFoundException` | Хранилище не найдено |
| `FolderNotFoundException` | Папка не найдена |
| `FolderNotEmptyException` | Папка не пуста |
| `CircularFolderReferenceException` | Циклическая ссылка |
| `PublicShareLinkNotFoundException` | Ссылка не найдена |
| `PublicShareLinkExpiredException` | Срок действия истёк |
| `PublicShareLinkMaxUsesExceededException` | Лимит использований |
| `InvalidSharePasswordException` | Неверный пароль |
| `DuplicateFileTagException` | Тег уже существует |
| `CannotLockFileException` | Нельзя заблокировать |
| `CannotUnlockFileException` | Нельзя разблокировать чужую блокировку |
| `MaxFolderDepthExceededException` | Макс. глубина вложенности |

---

## 8. Repositories

| Репозиторий | Методы |
|---|---|
| `FileRepository` | `get_by_id`, `get_by_workspace`, `get_by_folder`, `get_by_uploader`, `get_by_owner`, `get_trashed_by_workspace`, `search_by_name`, `get_by_tag`, `get_by_type`, `count_by_workspace`, `sum_size_by_workspace` |
| `FolderRepository` | `get_by_id`, `get_by_workspace`, `get_by_parent`, `get_root_folders`, `get_by_project`, `get_by_type`, `search` |
| `StorageRepository` | `get_by_id`, `get_by_owner`, `get_by_owner_type` |
