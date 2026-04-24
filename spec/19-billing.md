# 19. Billing — Биллинг и оплата

## Обзор

Контекст биллинга управляет тарифными планами, подписками, оплатой, счетами и уведомлениями по платежам. Интегрируется с российскими и международными платёжными системами.

---

## Принципы расширяемости

1. **SubscriptionStatus — расширяемый enum** — `TRIALING`, `ACTIVE`, `PAUSED`, `PAST_DUE`, `CANCELLED`, `EXPIRED`. Жизненный цикл подписки.
2. **PaymentProvider — enum** — `YUKASSA`, `SBER`, `TBANK`, `STRIPE`. Новый провайдер = значение enum + adapter.
3. **Subscription — AR** — подписка с полным lifecycle (trial, active, paused, cancelled, grace, expired).
4. **Invoice — AR** — счёт с line items и статусами.
5. **Plan — entity** — тарифный план с лимитами и фичами.
6. **PlanLimits — VO** — типизированные лимиты тарифа.
7. **BillingDetails — VO** — реквизиты для бухгалтерии.

---

## 1. Функциональные требования

### 1.1. Тарифные планы

| Параметр | Free | Start | Business | Enterprise |
|----------|------|-------|----------|------------|
| Цена | $0 | $8–15/user/мес | $20–40/user/мес | По запросу |
| Минимум пользователей | — | 1 | 1 | 10 |
| Макс. пользователей workspace | 10 | 25–50 | 100–500 | ∞ |
| Организации | ❌ | ❌ | ✅ (3) | ✅ (∞) |
| Workspaces | 1 | 5 | 25 | ∞ |
| Проекты/workspace | 5 | 50 | 500 | ∞ |
| Задачи/workspace | 500 | 10 000 | 100 000 | ∞ |
| Хранилище | 1 GB | 10 GB | 100 GB | ∞ |
| Trial | — | 14 дней | 30 дней | — |
| Billing period | — | Monthly / Annual | Monthly / Annual | Custom |
| Annual discount | — | 20% | 20% | Custom |
| Deployment | SaaS | SaaS | SaaS / Self-hosted | All |

### 1.2. Управление подпиской

| Требование | Описание |
|-----------|----------|
| Выбор/смена тарифа | Upgrade / Downgrade |
| Proration | Пропорциональный пересчёт при смене тарифа |
| Trial | 14 или 30 дней полного функционала |
| Продление trial | По запросу (admin action) |
| Приостановка подписки | Пауза до 3 месяцев |
| Отмена подписки | С указанием причины + retention flow |
| Возобновление | После отмены — в течение grace period |
| Grace period | 14 дней после неоплаты |

**Жизненный цикл подписки:**
```
Trial → Active → [Paused] → Active → Cancelled → Grace Period → Expired
                                                              ↓
                                                          Downgrade to Free
```

### 1.3. Оплата

| Метод | Описание |
|-------|----------|
| Банковские карты | Visa, MasterCard, МИР |
| СБП | Система быстрых платежей |
| СберPay | |
| Т-Банк (Тинькофф) | |
| ЮKassa | Агрегатор |
| Банковский перевод | Для Enterprise (invoice-based) |

### 1.4. Управление платёжными данными

- Добавление / удаление карт
- Основная карта для списания
- Обновление платёжной информации
- Хранение токенов карт (не полных данных — PCI DSS compliance)

### 1.5. Счета и история

- Автоматическое формирование счёта (invoice) при каждой оплате
- История всех транзакций
- Скачивание счетов (PDF)
- Данные для бухгалтерии: ИНН, КПП, юр. адрес, VAT ID
- Акт выполненных работ (для российских юрлиц)

### 1.6. Уведомления по биллингу

| Тип | Канал |
|-----|-------|
| Успешная оплата | Email |
| Неудачная оплата (+ retry) | In-app, Email |
| Предупреждение об истечении карты (за 30 дней) | In-app, Email |
| Предстоящее списание (за 3 дня) | In-app, Email |
| Приближение лимитов тарифа | In-app |
| Окончание trial (за 7 дней, 3 дня, 1 день) | In-app, Email |
| Grace period начался | In-app, Email |
| Grace period заканчивается (за 3 дня) | In-app, Email |
| Подписка истекла | In-app, Email |

---

## 2. Доменная модель

### Value Objects

| VO | Тип | Описание |
|---|---|---|
| `SubscriptionStatus` | Enum | `TRIALING`, `ACTIVE`, `PAUSED`, `PAST_DUE`, `CANCELLED`, `EXPIRED` |
| `BillingPeriod` | Enum | `MONTHLY`, `ANNUAL`, `CUSTOM` |
| `Currency` | Enum | `RUB`, `USD`, `EUR` |
| `PaymentMethodType` | Enum | `CARD`, `SBP`, `BANK_TRANSFER` |
| `PaymentProvider` | Enum | `YUKASSA`, `SBER`, `TBANK`, `STRIPE` |
| `InvoiceStatus` | Enum | `DRAFT`, `OPEN`, `PAID`, `VOID`, `UNCOLLECTIBLE` |
| `TransactionStatus` | Enum | `PENDING`, `SUCCEEDED`, `FAILED`, `REFUNDED`, `PARTIALLY_REFUNDED` |
| `TransactionType` | Enum | `PAYMENT`, `REFUND`, `CREDIT` |
| `SubscriptionOwnerType` | Enum | `USER`, `ORGANIZATION` |
| `MoneyAmount` | frozen dataclass | cents: int, currency: Currency |

#### VO Groups

```python
class PlanLimits:
    max_workspaces: int | None
    max_projects_per_workspace: int | None
    max_tasks_per_workspace: int | None
    max_members_per_workspace: int | None
    max_organizations: int | None
    max_members_per_organization: int | None
    storage_bytes: int | None
    max_file_size_bytes: int | None
    max_custom_fields: int | None
    max_saved_views: int | None
    max_dashboards: int | None

class BillingDetails:
    company_name: str | None
    inn: str | None  # ИНН (Russian tax ID)
    kpp: str | None  # КПП
    legal_address: str | None
    vat_id: str | None  # для международных
    email: str  # для отправки счетов
    phone: str | None
    country: str
```

### Entities

| Сущность | Поля | Описание |
|---|---|---|
| `Plan` | name, slug, description, features: list[str], limits: PlanLimits, monthly_price_cents, annual_price_cents, currency: Currency, is_public, is_custom, trial_days \| None, position | Тарифный план |
| `PaymentMethod` | owner_type: SubscriptionOwnerType, owner_id: Id, type: PaymentMethodType, provider: PaymentProvider, provider_payment_method_id: str, card_last_four \| None, card_brand \| None, card_exp_month \| None, card_exp_year \| None, is_default | Платёжный метод |
| `InvoiceLineItem` | description, quantity, unit_price_cents, amount_cents | Строка счёта |
| `Transaction` | subscription_id: Id \| None, invoice_id: Id \| None, owner_type, owner_id, type: TransactionType, amount: MoneyAmount, status: TransactionStatus, provider: PaymentProvider, provider_transaction_id, payment_method_id \| None, failure_reason \| None, retry_count, next_retry_at \| None, metadata: dict | Транзакция |

### Aggregates

#### Subscription (Aggregate Root)

Поля:
- owner_type: SubscriptionOwnerType
- owner_id: Id (opaque — user_id или organization_id)
- plan_id: Id
- status: SubscriptionStatus
- billing_period: BillingPeriod
- current_period_start: date
- current_period_end: date
- trial_start: date | None
- trial_end: date | None
- quantity: int
- unit_price_cents: int
- currency: Currency
- discount_percentage: int | None
- paused_at: datetime | None
- pause_ends_at: datetime | None
- cancelled_at: datetime | None
- cancellation_reason: str | None
- grace_period_end: date | None
- payment_method_id: Id | None
- billing_details: BillingDetails | None
- created_at: datetime
- updated_at: datetime

Методы:
- `create(owner_type, owner_id, plan_id, billing_period, quantity, payment_method_id)` → `Subscription` (factory, status=ACTIVE)
- `start_trial(plan_id, trial_days)` → status=TRIALING
- `activate()` → status=ACTIVE
- `upgrade(new_plan_id, proration_amount)` / `downgrade(new_plan_id, effective_date)`
- `change_quantity(new_quantity)`
- `cancel(reason)` → status=CANCELLED
- `resume()` → status=ACTIVE (из grace period)
- `pause(pause_until)` → status=PAUSED / `unpause()` → status=ACTIVE
- `renew(new_period_start, new_period_end)`
- `enter_grace_period(grace_end)` → status=PAST_DUE
- `expire()` → status=EXPIRED
- `update_billing_details(details)`

Инварианты:
- Один active subscription на owner (user/org)
- Trial → Active при оплате; Trial → Free если не оплачено
- Grace period = 14 дней после неудачной оплаты
- Pause максимум 3 месяца
- Cancellation reason обязательна
- Downgrade применяется с начала следующего billing period

#### Invoice (Aggregate Root)

Поля:
- invoice_number: str (auto-generated)
- subscription_id: Id
- owner_type: SubscriptionOwnerType
- owner_id: Id
- status: InvoiceStatus
- amount_cents: int
- tax_cents: int
- total_cents: int
- currency: Currency
- period_start: date
- period_end: date
- line_items: list[InvoiceLineItem]
- billing_details: BillingDetails
- pdf_url: str | None
- due_date: date
- paid_at: datetime | None
- created_at: datetime

Методы:
- `create(subscription_id, owner, period, line_items, billing_details)` → `Invoice` (factory, status=DRAFT)
- `finalize()` → status=OPEN
- `mark_paid(transaction_id)` → status=PAID
- `void()` → status=VOID
- `mark_uncollectible()` → status=UNCOLLECTIBLE
- `add_line_item(description, quantity, unit_price_cents)`
- `set_pdf_url(url)`

Инварианты:
- invoice_number глобально уникален, monotonically increasing
- Нельзя изменять PAID/VOID invoices
- total_cents = amount_cents + tax_cents

---

## 3. Бизнес-правила

### Подписки
1. **Free → Paid**: immediate upgrade, начинается billing period
2. **Paid → Higher Paid**: proration — оставшиеся дни текущего плана конвертируются в credit
3. **Paid → Lower Paid**: downgrade применяется с начала следующего billing period
4. **Paid → Free**: downgrade; если лимиты превышены — уведомление, данные не удаляются, но создание нового блокируется
5. **Trial**: полный функционал выбранного тарифа; по окончании → Free если не оплачено
6. **Grace period**: 14 дней после неудачной оплаты; данные read-only после истечения
7. **Pause**: максимум 3 месяца; billing stop; после паузы — автоматическое возобновление
8. **Cancellation**: причина обязательна; retention flow (предложение скидки)

### Оплата
9. **Retry logic**: при неудачной оплате — 3 retry: через 1 день, 3 дня, 7 дней
10. **Card expiry**: уведомление за 30 дней до истечения карты
11. **PCI DSS**: полные данные карт не хранятся — только токены от провайдера
12. **Refund**: возможен в течение 14 дней после оплаты; пропорциональный
13. **Invoice number**: monotonically increasing, unique globally

### Лимиты
14. При приближении к лимиту (80%) — уведомление
15. При достижении лимита — создание нового блокируется, существующие данные доступны
16. Enterprise: лимиты настраиваемые (через custom plan)

---

## 4. API Endpoints

### 4.1. Планы

```
GET /api/v1/billing/plans
```

**Response (200):**
```json
{
  "plans": [
    {
      "id": "uuid",
      "name": "Free",
      "slug": "free",
      "monthly_price_cents": 0,
      "annual_price_cents": 0,
      "currency": "RUB",
      "limits": {
        "max_workspaces": 1,
        "max_projects_per_workspace": 5,
        "max_tasks_per_workspace": 500,
        "max_members_per_workspace": 10,
        "storage_bytes": 1073741824
      },
      "features": ["kanban", "list_view", "basic_filters"],
      "trial_days": null
    }
  ]
}
```

### 4.2. Подписка

```
GET /api/v1/billing/subscription
```

**Response (200):**
```json
{
  "id": "uuid",
  "plan": {"id": "uuid", "name": "Start", "slug": "start"},
  "status": "active",
  "billing_period": "monthly",
  "quantity": 10,
  "unit_price_cents": 80000,
  "currency": "RUB",
  "current_period_start": "2025-02-01",
  "current_period_end": "2025-03-01",
  "next_invoice_amount_cents": 800000,
  "payment_method": {
    "id": "uuid",
    "type": "card",
    "card_last_four": "4242",
    "card_brand": "Visa"
  },
  "usage": {
    "members": {"used": 7, "limit": 25, "percentage": 28},
    "storage": {"used_bytes": 524288000, "limit_bytes": 10737418240, "percentage": 5}
  }
}
```

---

```
POST /api/v1/billing/subscription
```
*Создание подписки (upgrade from Free)*

**Request:**
```json
{
  "plan_id": "plan_uuid",
  "billing_period": "monthly",
  "quantity": 10,
  "payment_method_id": "pm_uuid"
}
```

---

```
PATCH /api/v1/billing/subscription
```
*Изменение подписки (upgrade/downgrade, change quantity)*

**Request:**
```json
{
  "plan_id": "new_plan_uuid",
  "quantity": 25
}
```

---

```
POST /api/v1/billing/subscription/cancel
```

**Request:**
```json
{
  "reason": "too_expensive",
  "feedback": "Would use if cheaper"
}
```

---

```
POST /api/v1/billing/subscription/resume
```
*Возобновление после отмены (в течение grace period)*

---

```
POST /api/v1/billing/subscription/pause
```

**Request:**
```json
{
  "pause_until": "2025-05-01"
}
```

---

```
POST /api/v1/billing/subscription/unpause
```

### 4.3. Trial

```
POST /api/v1/billing/trial/start
```

**Request:**
```json
{
  "plan_id": "plan_uuid"
}
```

---

```
POST /api/v1/admin/billing/trial/{subscription_id}/extend
```
*Admin: продление trial*

**Request:**
```json
{
  "days": 14
}
```

### 4.4. Платёжные методы

```
GET /api/v1/billing/payment-methods
```

---

```
POST /api/v1/billing/payment-methods
```

**Request:**
```json
{
  "type": "card",
  "provider": "yukassa",
  "provider_payment_method_id": "pm_token_from_provider",
  "is_default": true
}
```

---

```
DELETE /api/v1/billing/payment-methods/{pm_id}
```

---

```
PUT /api/v1/billing/payment-methods/{pm_id}/default
```

### 4.5. Счета и история

```
GET /api/v1/billing/invoices
```

**Query params:** `status`, `from`, `to`, `page`, `limit`

---

```
GET /api/v1/billing/invoices/{invoice_id}
```

---

```
GET /api/v1/billing/invoices/{invoice_id}/pdf
```

**Response (302):** Redirect to PDF download URL

---

```
GET /api/v1/billing/transactions
```

**Query params:** `type`, `status`, `from`, `to`, `page`, `limit`

### 4.6. Billing Details

```
GET /api/v1/billing/details
```

---

```
PUT /api/v1/billing/details
```

**Request:**
```json
{
  "company_name": "ООО «Ромашка»",
  "inn": "7707123456",
  "kpp": "770701001",
  "legal_address": "г. Москва, ул. Примерная, д. 1",
  "email": "billing@romashka.ru",
  "phone": "+74951234567"
}
```

### 4.7. Usage / Limits

```
GET /api/v1/billing/usage
```

**Response (200):**
```json
{
  "plan": "start",
  "limits": {
    "workspaces": {"used": 3, "limit": 5},
    "projects": {"used": 22, "limit": 50},
    "tasks": {"used": 3500, "limit": 10000},
    "members": {"used": 15, "limit": 25},
    "storage": {"used_bytes": 2147483648, "limit_bytes": 10737418240}
  },
  "warnings": [
    {"resource": "members", "percentage": 60, "threshold": 80, "triggered": false}
  ]
}
```

---

## 5. Схема БД

### Таблица: `plans`

| Колонка | Тип | Constraints |
|---------|-----|-------------|
| id | UUID | PK |
| name | VARCHAR(50) | NOT NULL |
| slug | VARCHAR(50) | UNIQUE, NOT NULL |
| description | TEXT | NOT NULL |
| features | JSONB | NOT NULL, DEFAULT '[]' |
| limits | JSONB | NOT NULL | |
| monthly_price_cents | INTEGER | NOT NULL |
| annual_price_cents | INTEGER | NOT NULL |
| currency | VARCHAR(3) | NOT NULL, DEFAULT 'RUB' |
| is_public | BOOLEAN | NOT NULL, DEFAULT TRUE |
| is_custom | BOOLEAN | NOT NULL, DEFAULT FALSE |
| trial_days | INTEGER | NULLABLE |
| position | INTEGER | NOT NULL, DEFAULT 0 |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |

### Таблица: `subscriptions`

| Колонка | Тип | Constraints |
|---------|-----|-------------|
| id | UUID | PK |
| owner_type | VARCHAR(20) | NOT NULL | user/organization |
| owner_id | UUID | NOT NULL |
| plan_id | UUID | FK → plans.id, NOT NULL |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'trialing' |
| billing_period | VARCHAR(10) | NOT NULL |
| current_period_start | DATE | NOT NULL |
| current_period_end | DATE | NOT NULL |
| trial_start | DATE | NULLABLE |
| trial_end | DATE | NULLABLE |
| quantity | INTEGER | NOT NULL, DEFAULT 1 |
| unit_price_cents | INTEGER | NOT NULL |
| currency | VARCHAR(3) | NOT NULL |
| discount_percentage | INTEGER | NULLABLE |
| paused_at | TIMESTAMPTZ | NULLABLE |
| pause_ends_at | TIMESTAMPTZ | NULLABLE |
| cancelled_at | TIMESTAMPTZ | NULLABLE |
| cancellation_reason | TEXT | NULLABLE |
| grace_period_end | DATE | NULLABLE |
| payment_method_id | UUID | FK → payment_methods.id, NULLABLE |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |

**Индексы:**
- `idx_sub_owner` — UNIQUE на `(owner_type, owner_id)` WHERE `status NOT IN ('expired', 'cancelled')`
- `idx_sub_status` — на `status`
- `idx_sub_plan` — на `plan_id`
- `idx_sub_period_end` — на `current_period_end`
- `idx_sub_grace` — на `grace_period_end` WHERE `status = 'past_due'`

### Таблица: `payment_methods`

| Колонка | Тип | Constraints |
|---------|-----|-------------|
| id | UUID | PK |
| owner_type | VARCHAR(20) | NOT NULL |
| owner_id | UUID | NOT NULL |
| type | VARCHAR(20) | NOT NULL |
| provider | VARCHAR(20) | NOT NULL |
| provider_payment_method_id | VARCHAR(200) | NOT NULL |
| card_last_four | VARCHAR(4) | NULLABLE |
| card_brand | VARCHAR(20) | NULLABLE |
| card_exp_month | INTEGER | NULLABLE |
| card_exp_year | INTEGER | NULLABLE |
| is_default | BOOLEAN | NOT NULL, DEFAULT FALSE |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |

**Индексы:**
- `idx_pm_owner` — на `(owner_type, owner_id)`
- `idx_pm_owner_default` — UNIQUE на `(owner_type, owner_id)` WHERE `is_default = TRUE`

### Таблица: `invoices`

| Колонка | Тип | Constraints |
|---------|-----|-------------|
| id | UUID | PK |
| invoice_number | VARCHAR(30) | UNIQUE, NOT NULL |
| subscription_id | UUID | FK → subscriptions.id, NOT NULL |
| owner_type | VARCHAR(20) | NOT NULL |
| owner_id | UUID | NOT NULL |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'draft' |
| amount_cents | INTEGER | NOT NULL |
| tax_cents | INTEGER | NOT NULL, DEFAULT 0 |
| total_cents | INTEGER | NOT NULL |
| currency | VARCHAR(3) | NOT NULL |
| period_start | DATE | NOT NULL |
| period_end | DATE | NOT NULL |
| billing_details | JSONB | NOT NULL, DEFAULT '{}' |
| pdf_url | VARCHAR(500) | NULLABLE |
| due_date | DATE | NOT NULL |
| paid_at | TIMESTAMPTZ | NULLABLE |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |

**Индексы:**
- `idx_inv_number` — UNIQUE на `invoice_number`
- `idx_inv_owner` — на `(owner_type, owner_id)`
- `idx_inv_subscription` — на `subscription_id`
- `idx_inv_status` — на `status`

### Таблица: `invoice_line_items`

| Колонка | Тип | Constraints |
|---------|-----|-------------|
| id | UUID | PK |
| invoice_id | UUID | FK → invoices.id, NOT NULL |
| description | VARCHAR(200) | NOT NULL |
| quantity | INTEGER | NOT NULL |
| unit_price_cents | INTEGER | NOT NULL |
| amount_cents | INTEGER | NOT NULL |

### Таблица: `transactions`

| Колонка | Тип | Constraints |
|---------|-----|-------------|
| id | UUID | PK |
| subscription_id | UUID | FK → subscriptions.id, NULLABLE |
| invoice_id | UUID | FK → invoices.id, NULLABLE |
| owner_type | VARCHAR(20) | NOT NULL |
| owner_id | UUID | NOT NULL |
| type | VARCHAR(20) | NOT NULL |
| amount_cents | INTEGER | NOT NULL |
| currency | VARCHAR(3) | NOT NULL |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'pending' |
| provider | VARCHAR(20) | NOT NULL |
| provider_transaction_id | VARCHAR(200) | NOT NULL |
| payment_method_id | UUID | FK → payment_methods.id, NULLABLE |
| failure_reason | TEXT | NULLABLE |
| retry_count | INTEGER | NOT NULL, DEFAULT 0 |
| next_retry_at | TIMESTAMPTZ | NULLABLE |
| metadata | JSONB | NOT NULL, DEFAULT '{}' |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |

**Индексы:**
- `idx_txn_owner` — на `(owner_type, owner_id)`
- `idx_txn_subscription` — на `subscription_id`
- `idx_txn_invoice` — на `invoice_id`
- `idx_txn_status` — на `status`
- `idx_txn_provider` — на `(provider, provider_transaction_id)`
- `idx_txn_retry` — на `next_retry_at` WHERE `status = 'failed' AND next_retry_at IS NOT NULL`

### Таблица: `billing_details`

| Колонка | Тип | Constraints |
|---------|-----|-------------|
| owner_type | VARCHAR(20) | NOT NULL |
| owner_id | UUID | NOT NULL |
| company_name | VARCHAR(200) | NULLABLE |
| inn | VARCHAR(12) | NULLABLE |
| kpp | VARCHAR(9) | NULLABLE |
| legal_address | TEXT | NULLABLE |
| vat_id | VARCHAR(20) | NULLABLE |
| email | VARCHAR(255) | NOT NULL |
| phone | VARCHAR(20) | NULLABLE |
| country | VARCHAR(2) | NOT NULL, DEFAULT 'RU' |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |

**Индексы:**
- `idx_bd_pk` — PRIMARY KEY на `(owner_type, owner_id)`

---

## 6. Доменные события

| Событие | Поля | Описание |
|---|---|---|
| `SubscriptionCreated` | subscription_id, owner_type, owner_id, plan_id, billing_period | Подписка создана |
| `SubscriptionUpgraded` | subscription_id, old_plan_id, new_plan_id, proration_amount | Upgrade |
| `SubscriptionDowngraded` | subscription_id, old_plan_id, new_plan_id, effective_date | Downgrade |
| `SubscriptionCancelled` | subscription_id, reason | Отменена |
| `SubscriptionResumed` | subscription_id | Возобновлена |
| `SubscriptionPaused` | subscription_id, pause_until | Приостановлена |
| `SubscriptionUnpaused` | subscription_id | Снята с паузы |
| `SubscriptionExpired` | subscription_id, owner_type, owner_id | Истекла |
| `SubscriptionRenewed` | subscription_id, new_period_start, new_period_end | Продлена |
| `TrialStarted` | subscription_id, plan_id, trial_end | Trial начат |
| `TrialEnding` | subscription_id, days_remaining | Trial заканчивается |
| `TrialExpired` | subscription_id | Trial истёк |
| `TrialExtended` | subscription_id, new_trial_end | Trial продлён |
| `PaymentSucceeded` | transaction_id, subscription_id, amount_cents, currency | Оплата успешна |
| `PaymentFailed` | transaction_id, subscription_id, amount_cents, reason | Оплата не удалась |
| `PaymentRetryScheduled` | transaction_id, retry_at, retry_count | Повторная попытка |
| `RefundProcessed` | transaction_id, original_transaction_id, amount_cents | Возврат |
| `InvoiceCreated` | invoice_id, subscription_id, total_cents | Счёт создан |
| `InvoicePaid` | invoice_id, transaction_id | Счёт оплачен |
| `InvoicePdfGenerated` | invoice_id, pdf_url | PDF сгенерирован |
| `PaymentMethodAdded` | pm_id, owner_type, owner_id, type | Метод добавлен |
| `PaymentMethodRemoved` | pm_id, owner_type, owner_id | Метод удалён |
| `PaymentMethodSetDefault` | pm_id, owner_type, owner_id | Метод по умолчанию |
| `CardExpiringWarning` | pm_id, exp_month, exp_year | Карта истекает |
| `UsageLimitApproaching` | owner_type, owner_id, resource, percentage | Приближение к лимиту |
| `UsageLimitReached` | owner_type, owner_id, resource, limit | Лимит достигнут |
| `GracePeriodStarted` | subscription_id, grace_end | Grace period начался |
| `GracePeriodEnding` | subscription_id, days_remaining | Grace period заканчивается |
| `GracePeriodExpired` | subscription_id | Grace period истёк |
| `BillingDetailsUpdated` | owner_type, owner_id, changed_fields: list[str] | Реквизиты обновлены |

---

## 7. Exceptions

| Исключение | Описание |
|---|---|
| `SubscriptionNotFoundException` | Подписка не найдена |
| `SubscriptionAlreadyActiveException` | Уже есть активная подписка |
| `SubscriptionNotCancellableException` | Нельзя отменить (expired) |
| `SubscriptionNotPausableException` | Нельзя приостановить |
| `PauseDurationExceededException` | Пауза > 3 месяцев |
| `CancellationReasonRequiredException` | Причина обязательна |
| `PlanNotFoundException` | Тариф не найден |
| `DowngradeNotAllowedException` | Downgrade невозможен (лимиты) |
| `PaymentMethodNotFoundException` | Метод оплаты не найден |
| `PaymentFailedException` | Оплата не удалась |
| `RefundNotAllowedException` | Возврат невозможен (> 14 дней) |
| `InvoiceNotFoundException` | Счёт не найден |
| `InvoiceNotModifiableException` | Нельзя изменять PAID/VOID |
| `UsageLimitReachedException` | Лимит тарифа достигнут |
| `InvalidBillingDetailsException` | Некорректные реквизиты |

---

## 8. Repositories

| Репозиторий | Методы |
|---|---|
| `SubscriptionRepository` | `get_by_id`, `get_by_owner`, `get_active_by_owner`, `get_by_status`, `get_expiring`, `get_in_grace_period` |
| `PlanRepository` | `get_by_id`, `get_by_slug`, `get_public`, `get_all` |
| `InvoiceRepository` | `get_by_id`, `get_by_invoice_number`, `get_by_owner`, `get_by_subscription`, `get_by_status` |
| `TransactionRepository` | `get_by_id`, `get_by_owner`, `get_by_subscription`, `get_by_invoice`, `get_by_status`, `get_pending_retries` |
| `PaymentMethodRepository` | `get_by_id`, `get_by_owner`, `get_default_by_owner` |
