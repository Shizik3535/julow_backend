# 02. System Roles — Системные роли

## Обзор

Системные роли определяют глобальные права пользователя на уровне всей платформы. Они отделены от ролей организации, workspace и проекта. Системные роли управляются только Super Admin и Admin.

---

## Принципы расширяемости

1. **SystemRole — enum** — `SUPER_ADMIN`, `ADMIN`, `SUPPORTER`, `USER`. Стабильное множество, новые роли = значение enum + permission mapping.
2. **Permission — VO** — (resource, action) pair. Новые пермишены = добавление в справочную таблицу.
3. **SystemRoleAssignment — entity** — назначение роли пользователю с историей.
4. **Системная роль — атрибут User** — не отдельный агрегат, но отдельная таблица для гибкости.

---

## 1. Функциональные требования

### Роли

| Роль | Описание | Назначение |
|------|----------|-----------|
| **Super Admin** | Полный контроль над платформой | Создатель системы, техническая команда |
| **Admin** | Управление пользователями и контентом | Администраторы платформы |
| **Supporter** | Просмотр данных для поддержки пользователей | Служба поддержки |
| **User** | Стандартный пользователь | Все зарегистрированные пользователи |

### Матрица прав

| Действие | Super Admin | Admin | Supporter | User |
|----------|-------------|-------|-----------|------|
| Управление системными ролями | ✅ | ❌ | ❌ | ❌ |
| Создание Admin | ✅ | ❌ | ❌ | ❌ |
| Блокировка/деактивация пользователей | ✅ | ✅ | ❌ | ❌ |
| Просмотр всех пользователей | ✅ | ✅ | ✅ | ❌ |
| Просмотр профиля пользователя | ✅ | ✅ | ✅ | ⚡ (свой) |
| Просмотр audit log | ✅ | ✅ | ⚡ (read-only) | ❌ |
| Управление тарифами | ✅ | ✅ | ❌ | ❌ |
| Управление feature flags | ✅ | ✅ | ❌ | ❌ |
| Управление шаблонами | ✅ | ✅ | ❌ | ❌ |
| Управление интеграциями (глобальные) | ✅ | ✅ | ❌ | ❌ |
| Email-шаблоны | ✅ | ✅ | ❌ | ❌ |
| Maintenance mode | ✅ | ❌ | ❌ | ❌ |
| Просмотр статистики платформы | ✅ | ✅ | ⚡ | ❌ |
| Ответ на тикеты поддержки | ✅ | ✅ | ✅ | ❌ |
| Создание workspace/организации | ✅ | ✅ | ❌ | ✅ |
| Удаление любого workspace/организации | ✅ | ✅ | ❌ | ❌ |
| Импорт данных пользователю | ✅ | ✅ | ✅ | ❌ |
| Сброс 2FA пользователю | ✅ | ✅ | ❌ | ❌ |
| Принудительный сброс пароля | ✅ | ✅ | ❌ | ❌ |
| Просмотр биллинга пользователей | ✅ | ✅ | ⚡ (read-only) | ❌ |

### Правила

1. **Super Admin** — не может быть назначен через UI, только через seed-скрипт или CLI
2. **Super Admin** — минимум 1 в системе, нельзя удалить последнего
3. **Admin** — назначается только Super Admin
4. **Supporter** — назначается Super Admin или Admin
5. **User** — роль по умолчанию при регистрации
6. **Понижение роли** — Super Admin может понизить Admin → User; Admin не может понизить другого Admin
7. **Self-demotion** — запрещено (нельзя понизить самого себя)

---

## 2. Доменная модель

### Value Objects

| VO | Тип | Описание |
|---|---|---|
| `SystemRole` | Enum | `SUPER_ADMIN`, `ADMIN`, `SUPPORTER`, `USER` |
| `Permission` | frozen dataclass | resource: str, action: str |
| `PermissionAction` | Enum | `CREATE`, `READ`, `UPDATE`, `DELETE`, `MANAGE` |

### Entities

| Сущность | Поля | Описание |
|---|---|---|
| `SystemRoleAssignment` | user_id: Id, role: SystemRole, assigned_by: Id \| None, assigned_at, revoked_at \| None, is_active: bool | Назначение роли |

Системная роль — атрибут User, а не отдельный агрегат. Отдельная таблица `system_role_assignments` для гибкости и истории.

Инварианты:
- Каждый пользователь имеет ровно одну активную системную роль
- SUPER_ADMIN не может быть назначен через API
- Нельзя удалить/понизить последнего SUPER_ADMIN
- ADMIN не может управлять ADMIN/SUPER_ADMIN
- Self-demotion запрещено

---

## 3. Бизнес-правила

1. Каждый пользователь имеет ровно одну активную системную роль
2. При регистрации назначается роль `USER`
3. `SUPER_ADMIN` не может быть назначен через API — только seed/CLI
4. Нельзя удалить или понизить последнего `SUPER_ADMIN`
5. `ADMIN` не может управлять другими `ADMIN` или `SUPER_ADMIN`
6. `SUPPORTER` имеет только read-доступ к пользовательским данным
7. Изменение роли логируется в audit log
8. При блокировке пользователя — все его сессии завершаются

---

## 4. API Endpoints

```
GET /api/v1/admin/users
```
*Список пользователей (Admin+)*

**Query params:** `page`, `limit`, `search`, `role`, `status`, `sort_by`, `order`

**Response (200):**
```json
{
  "items": [
    {
      "id": "uuid",
      "email": "user@example.com",
      "display_name": "John Doe",
      "status": "active",
      "system_role": "user",
      "created_at": "2025-01-01T00:00:00Z",
      "last_login_at": "2025-01-15T10:00:00Z"
    }
  ],
  "total": 150,
  "page": 1,
  "limit": 20
}
```

---

```
GET /api/v1/admin/users/{user_id}
```

**Response (200):** полная информация о пользователе

---

```
PUT /api/v1/admin/users/{user_id}/role
```
*Изменение системной роли (Super Admin для Admin+, Admin для Supporter/User)*

**Request:**
```json
{
  "role": "supporter"
}
```

**Response (200):**
```json
{
  "user_id": "uuid",
  "previous_role": "user",
  "new_role": "supporter",
  "assigned_by": "admin_uuid",
  "assigned_at": "2025-01-15T10:00:00Z"
}
```

**Errors:**
- `403 Forbidden` — недостаточно прав
- `409 Conflict` — попытка понизить последнего Super Admin
- `422 Unprocessable Entity` — попытка назначить super_admin через API

---

```
POST /api/v1/admin/users/{user_id}/suspend
```

**Request:**
```json
{
  "reason": "Violation of terms of service"
}
```

---

```
POST /api/v1/admin/users/{user_id}/reactivate
```

---

```
POST /api/v1/admin/users/{user_id}/reset-password
```
*Принудительный сброс пароля — отправляет email пользователю*

---

```
POST /api/v1/admin/users/{user_id}/reset-2fa
```
*Сброс 2FA пользователю*

---

```
GET /api/v1/admin/roles/stats
```
*Статистика по ролям*

**Response (200):**
```json
{
  "super_admin": 2,
  "admin": 5,
  "supporter": 10,
  "user": 5000
}
```

---

## 5. Схема БД

### Таблица: `system_role_assignments`

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| id | UUID | PK | |
| user_id | UUID | FK → users.id, NOT NULL | |
| role | VARCHAR(20) | NOT NULL | super_admin/admin/supporter/user |
| assigned_by | UUID | FK → users.id, NULLABLE | NULL для seed |
| assigned_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| revoked_at | TIMESTAMPTZ | NULLABLE | |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE | |

**Индексы:**
- `idx_sra_user_active` — UNIQUE на `(user_id)` WHERE `is_active = TRUE`
- `idx_sra_role` — на `role` WHERE `is_active = TRUE`

### Таблица: `system_permissions` (справочная)

| Колонка | Тип | Constraints | Описание |
|---------|-----|-------------|----------|
| id | UUID | PK | |
| role | VARCHAR(20) | NOT NULL | |
| resource | VARCHAR(50) | NOT NULL | |
| action | VARCHAR(20) | NOT NULL | |

**Индексы:**
- `idx_sp_role` — на `role`
- `idx_sp_unique` — UNIQUE на `(role, resource, action)`

---

## 6. Доменные события

| Событие | Поля | Описание |
|---|---|---|
| `SystemRoleAssigned` | user_id, role, assigned_by, previous_role | Роль назначена |
| `SystemRoleRevoked` | user_id, role, revoked_by | Роль отозвана |
| `UserSuspendedByAdmin` | user_id, reason, suspended_by | Пользователь заблокирован |
| `UserReactivatedByAdmin` | user_id, reactivated_by | Пользователь разблокирован |
| `AdminPasswordResetForUser` | user_id, initiated_by | Сброс пароля |
| `AdminTwoFactorResetForUser` | user_id, initiated_by | Сброс 2FA |

---

## 7. Exceptions

| Исключение | Описание |
|---|---|
| `CannotAssignSuperAdminException` | SUPER_ADMIN нельзя назначить через API |
| `CannotDemoteLastSuperAdminException` | Нельзя понизить последнего SUPER_ADMIN |
| `SelfDemotionNotAllowedException` | Нельзя понизить себя |
| `InsufficientRolePrivilegeException` | Недостаточно прав для назначения |
| `UserAlreadyHasRoleException` | Роль уже назначена |
| `UserNotFoundException` | Пользователь не найден |

---

## 8. Repositories

| Репозиторий | Методы |
|---|---|
| `SystemRoleAssignmentRepository` | `get_active_by_user`, `get_by_role`, `count_by_role`, `get_super_admins` |
