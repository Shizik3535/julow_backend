# События Security BC

## События, которые отдаёт Security BC

### Audit Events

| Событие | Описание | Поля |
|---|---|---|
| `AuditEntryCreated` | Запись аудита создана | `actor_id`, `action`, `resource_type`, `resource_id`, `severity` |

### Backup Events

| Событие | Описание | Поля |
|---|---|---|
| `BackupCreated` | Бэкап создан | `backup_id`, `backup_type`, `size_bytes` |
| `BackupRestored` | Бэкап восстановлен | `backup_id`, `restored_by` |
| `BackupFailed` | Бэкап завершился ошибкой | `backup_id`, `error_message` |
| `EncryptionKeyRotated` | Ключ шифрования ротирован | `encryption_config_id` |
| `IpRuleAdded` | IP-правило добавлено | `rule_id`, `rule_type`, `ip_range` |
| `IpRuleRemoved` | IP-правило удалено | `rule_id` |

### Compliance Events

| Событие | Описание | Поля |
|---|---|---|
| `SecurityPolicyUpdated` | Политика безопасности обновлена | `policy_id`, `changed_fields` |
| `ComplianceViolationDetected` | Нарушение compliance обнаружено | `standard`, `violation_details` |
| `DataSubjectRequestCreated` | Запрос субъекта данных создан | `request_id`, `user_id`, `request_type` |
| `DataSubjectRequestCompleted` | Запрос субъекта данных завершён | `request_id` |
| `DataSubjectRequestRejected` | Запрос субъекта данных отклонён | `request_id`, `reason` |

### Security Events

| Событие | Описание | Поля |
|---|---|---|
| `SuspiciousActivityDetected` | Подозрительная активность обнаружена | `actor_id`, `event_type`, `reason` |
| `SecurityEventOccurred` | Событие безопасности произошло | `event_type`, `severity` |
| `SecurityEventResolved` | Событие безопасности разрешено | `event_id`, `resolved_by` |
| `SecurityIncidentCreated` | Инцидент безопасности создан | `incident_id`, `severity` |
| `SecurityIncidentUpdated` | Инцидент безопасности обновлён | `incident_id`, `changed_fields` |
| `SecurityIncidentResolved` | Инцидент безопасности разрешён | `incident_id`, `resolved_by`, `resolution` |

**Итого: 18 событий**

---

## События, на которые подписывается Security BC

Нет. Security BC не подписывается на события других BC.
