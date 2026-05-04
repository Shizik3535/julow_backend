# События FileStorage BC

## События, которые отдаёт FileStorage BC

### File Events

| Событие | Описание | Поля |
|---|---|---|
| `FileUploaded` | Файл загружен | `file_id`, `uploader_id`, `workspace_id`, `file_type`, `size_bytes` |
| `FileDownloaded` | Файл скачан | `file_id`, `downloader_id` |
| `FileTrashed` | Файл перемещён в корзину | `file_id`, `trashed_by` |
| `FileRestored` | Файл восстановлен из корзины | `file_id`, `restored_by` |
| `FileDeleted` | Файл окончательно удалён | `file_id` |
| `FileMoved` | Файл перемещён | `file_id`, `old_folder_id`, `new_folder_id` |
| `FileRenamed` | Файл переименован | `file_id`, `old_name`, `new_name` |
| `FilePermissionGranted` | Разрешение на файл выдано | `file_id`, `user_id`, `team_id`, `access_level` |
| `FilePermissionRevoked` | Разрешение на файл отозвано | `file_id`, `user_id`, `team_id` |
| `FileVersionCreated` | Новая версия файла | `file_id`, `version_number`, `uploader_id` |
| `FileLocked` | Файл заблокирован | `file_id`, `locked_by` |
| `FileUnlocked` | Файл разблокирован | `file_id`, `unlocked_by` |
| `PublicShareLinkCreated` | Публичная ссылка создана | `file_id`, `link_id` |
| `PublicShareLinkRevoked` | Публичная ссылка отозвана | `file_id`, `link_id` |
| `PublicShareLinkAccessed` | Переход по публичной ссылке | `file_id`, `link_id` |
| `FileTagAdded` | Тег добавлен | `file_id`, `tag_name` |
| `FileTagRemoved` | Тег удалён | `file_id`, `tag_name` |
| `VirusDetected` | Вирус обнаружен | `file_id`, `virus_name` |
| `VirusScanCompleted` | Сканирование завершено | `file_id`, `scan_status` |

### Folder Events

| Событие | Описание | Поля |
|---|---|---|
| `FolderCreated` | Папка создана | `folder_id`, `workspace_id`, `folder_type` |
| `FolderUpdated` | Папка обновлена | `folder_id`, `changed_fields` |
| `FolderDeleted` | Папка удалена | `folder_id` |
| `FolderMoved` | Папка перемещена | `folder_id`, `old_parent_id`, `new_parent_id` |

### Storage Events

| Событие | Описание | Поля |
|---|---|---|
| `StorageQuotaApproaching` | Квота хранилища приближается (≥90%) | `storage_id`, `used_percent` |
| `StorageQuotaExceeded` | Квота хранилища превышена | `storage_id`, `used_percent` |

**Итого: 25 событий**

---

## События, на которые подписывается FileStorage BC

Нет. FileStorage BC не подписывается на события других BC.
