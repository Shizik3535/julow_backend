# Billing BC — Спецификация

> Путь: `app/context/billing/domain`
> Исходные требования: §19 (Биллинг и оплата)

## Контекст

Billing BC отвечает за тарифные планы (как AR с гибкими лимитами и фичами), подписки, оплату, пробные периоды, счета, скидки и лимиты. Подписка привязывается к workspace или организации через `SubscriptionOwnerType` enum. Тарифный план — отдельный AR, что позволяет добавлять/изменять планы без правки кода.

---

## Принципы расширяемости

1. **Plan — AR вместо enum** — тарифный план как Aggregate Root с гибкими лимитами и фичами. Новый план = запись, не правка enum.
2. **PlanFeature — entity** — вместо `features: list[str]`. Каждая фича — запись с именем и значением. Новые фичи = запись.
3. **PlanLimit — entity** — вместо `PlanLimits` frozen dataclass. Каждый лимит — запись с именем и значением. Новые лимиты = запись.
4. **SubscriptionOwnerType — enum** — вместо магической строки `owner_type: str`.
5. **BillingCycle — enum** — месячная/годовая оплата. Новые циклы = значение enum.
6. **Discount/Coupon — entity** — скидки и промокоды. Новые типы скидок = расширение.
7. **InvoiceLineItem — entity** — детализация счёта. Новые типы строк = расширение.

---

## Value Objects

| VO | Тип | Описание | Исходное требование |
|---|---|---|---|
| `Money` | frozen dataclass | amount: float, currency: str (ISO 4217) | §19.1 |
| `SubscriptionOwnerType` | Enum | `WORKSPACE`, `ORGANIZATION` | §19.2 |
| `SubscriptionStatus` | Enum | `ACTIVE`, `PAST_DUE`, `CANCELED`, `TRIALING`, `PAUSED`, `GRACE_PERIOD`, `EXPIRED` | §19.2 |
| `BillingCycle` | Enum | `MONTHLY`, `YEARLY`, `QUARTERLY` | §19.1 |
| `PaymentStatus` | Enum | `PENDING`, `SUCCEEDED`, `FAILED`, `REFUNDED`, `PARTIALLY_REFUNDED` | §19.5 |
| `RefundStatus` | Enum | `PENDING`, `APPROVED`, `REJECTED`, `PROCESSED` | §19.5 |
| `TrialPeriod` | frozen dataclass | days: int, started_at: datetime \| None, expires_at: datetime \| None | §19.2 |
| `GracePeriod` | frozen dataclass | days: int, started_at: datetime \| None, expires_at: datetime \| None | §19.2 |
| `PaymentProvider` | Enum | `CARD`, `SPB`, `SBER`, `TBANK`, `YUKASSA`, `STRIPE`, `PAYPAL` | §19.3 |
| `TaxInfo` | frozen dataclass | vat_id: str \| None, tax_requisites: str \| None, country: str \| None (ISO 3166) | §19.5 |
| `BillingAddress` | frozen dataclass | country: str, city: str, address_line1: str, address_line2: str \| None, postal_code: str, company_name: str \| None | §19.5 |
| `DiscountType` | Enum | `PERCENTAGE`, `FIXED_AMOUNT`, `FREE_MONTHS` | §19.1 |
| `CouponStatus` | Enum | `ACTIVE`, `EXPIRED`, `EXHAUSTED`, `DISABLED` | §19.1 |

> **`Money`** — типизированное денежное значение. `currency` — ISO 4217 (USD, EUR, RUB). Используется везде вместо `amount: float`.
>
> **`SubscriptionOwnerType`** — enum вместо `owner_type: str`. Новые типы владельцев = значение enum.
>
> **`SubscriptionStatus`** — добавлен `EXPIRED` — подписка истекла (после grace period без оплаты).
>
> **`BillingCycle`** — периодичность оплаты. `QUARTERLY` — поквартальная. Новые циклы = значение enum. Годовая оплата обычно со скидкой.
>
> **`RefundStatus`** — отдельный статус для возвратов. `PARTIALLY_REFUNDED` — частичный возврат.
>
> **`PaymentProvider`** — добавлены `STRIPE`, `PAYPAL` для международных платежей. Новые провайдеры = значение enum.
>
> **`TaxInfo`** — добавлен `country` (ISO 3166) для определения налоговой ставки. Поля опциональны — не все юрисдикции требуют VAT.
>
> **`BillingAddress`** — адрес для выставления счетов. Обязателен для юридических лиц.
>
> **`DiscountType`** — тип скидки. `PERCENTAGE` — процент, `FIXED_AMOUNT` — фиксированная сумма, `FREE_MONTHS` — бесплатные месяцы. Новые типы = значение enum.
>
> **`CouponStatus`** — жизненный цикл купона. `EXHAUSTED` — исчерпан (max_uses достигнут).

## Entities

| Сущность | Поля | Описание | Исходное требование |
|---|---|---|---|
| `PaymentMethod` | id: Id, provider: PaymentProvider, external_id: str, is_default: bool, last4: str \| None, expires_at: datetime \| None, billing_address: BillingAddress \| None | Платёжный метод | §19.4 |
| `Transaction` | id: Id, amount: Money, status: PaymentStatus, external_id: str, provider: PaymentProvider, processed_at: datetime \| None, refund_status: RefundStatus \| None | Транзакция | §19.5 |
| `PlanFeature` | id: Id, name: str, value: str, description: str \| None | Фича тарифного плана | §19.1 |
| `PlanLimit` | id: Id, name: str, value: int, unit: str \| None (users, mb, projects, etc.) | Лимит тарифного плана | §19.1 |
| `InvoiceLineItem` | id: Id, description: str, quantity: int, unit_price: Money, total: Money, discount: Discount \| None | Строка счёта | §19.5 |
| `Discount` | id: Id, discount_type: DiscountType, value: float, description: str \| None, coupon_id: Id \| None | Скидка | §19.1 |
| `Coupon` | id: Id, code: str, discount_type: DiscountType, value: float, max_uses: int \| None, current_uses: int, expires_at: datetime \| None, status: CouponStatus, applicable_plan_ids: list[Id] \| None | Промокод | §19.1 |
| `Refund` | id: Id, transaction_id: Id, amount: Money, reason: str, status: RefundStatus, processed_by: Id \| None, processed_at: datetime \| None | Возврат средств | §19.5 |

> **`PaymentMethod`** — добавлены `id`, `billing_address`. `last4` опционален (не все провайдеры дают).
>
> **`Transaction`** — добавлены `id`, `provider`, `refund_status`. `amount: Money` вместо `Money | None` — транзакция всегда имеет сумму.
>
> **`PlanFeature`** — фича тарифного плана. `name` — идентификатор фичи (например, "has_epics", "has_sprints", "has_custom_fields"), `value` — значение ("true", "false", "5"). Новые фичи = запись, не правка кода. Проверка доступности фичи на app-слое через `MethodologyCapabilities` в Project BC.
>
> **`PlanLimit`** — лимит тарифного плана. `name` — идентификатор лимита (например, "max_users", "max_storage_mb", "max_projects"), `value` — числовое значение, `unit` — единица измерения. Новые лимиты = запись. Проверка лимитов на app-слое.
>
> **`InvoiceLineItem`** — детализация счёта. Одна строка = одна услуга. `discount` — применённая скидка. Новые типы строк = расширение.
>
> **`Discount`** — скидка. `discount_type` + `value` определяют размер скидки. `coupon_id` — ссылка на купон, если скидка из промокода.
>
> **`Coupon`** — промокод. `code` — уникальный код. `applicable_plan_ids` — к каким планам применяется (None = ко всем). `max_uses` — ограничение использований. Новые купоны = запись.
>
> **`Refund`** — возврат средств. Связан с транзакцией. `status` — жизненный цикл возврата.

## Domain Events

| Событие | Поля | Описание | Исходное требование |
|---|---|---|---|
| `PlanCreated` | plan_id, name | Тарифный план создан | §19.1 |
| `PlanUpdated` | plan_id, changed_fields: list[str] | Тарифный план обновлён | §19.1 |
| `PlanArchived` | plan_id | Тарифный план архивирован | §19.1 |
| `SubscriptionCreated` | subscription_id, owner_type: SubscriptionOwnerType, owner_id, plan_id | Подписка создана | §19.2 |
| `SubscriptionUpgraded` | subscription_id, old_plan_id, new_plan_id | Тариф повышен | §19.2 |
| `SubscriptionDowngraded` | subscription_id, old_plan_id, new_plan_id | Тариф понижен | §19.2 |
| `SubscriptionCanceled` | subscription_id, reason | Подписка отменена | §19.2 |
| `SubscriptionResumed` | subscription_id | Подписка возобновлена | §19.2 |
| `SubscriptionPaused` | subscription_id | Подписка приостановлена | §19.2 |
| `SubscriptionExpired` | subscription_id | Подписка истекла | §19.2 |
| `BillingCycleChanged` | subscription_id, old_cycle, new_cycle | Цикл оплаты изменён | §19.2 |
| `TrialStarted` | subscription_id, expires_at | Пробный период начат | §19.2 |
| `TrialExpired` | subscription_id | Пробный период истёк | §19.2 |
| `TrialExtended` | subscription_id, new_expires_at | Пробный период продлён | §19.2 |
| `GracePeriodStarted` | subscription_id, expires_at | Grace period начат | §19.2 |
| `GracePeriodEnded` | subscription_id | Grace period завершён | §19.2 |
| `PaymentSucceeded` | subscription_id, invoice_id, transaction_id | Оплата успешна | §19.6 |
| `PaymentFailed` | subscription_id, invoice_id, transaction_id | Оплата не прошла | §19.6 |
| `PaymentRetryScheduled` | subscription_id, invoice_id, retry_at | Планируется повторная попытка | §19.6 |
| `RefundRequested` | transaction_id, amount | Запрос на возврат | §19.5 |
| `RefundProcessed` | transaction_id, amount | Возврат обработан | §19.5 |
| `RefundRejected` | transaction_id, reason | Возврат отклонён | §19.5 |
| `InvoiceGenerated` | invoice_id, subscription_id, amount | Счёт сформирован | §19.5 |
| `InvoicePaid` | invoice_id, transaction_id | Счёт оплачен | §19.5 |
| `CardExpiringWarning` | subscription_id, payment_method_id | Карта скоро истечёт | §19.6 |
| `PlanLimitApproaching` | owner_type: SubscriptionOwnerType, owner_id, limit_name, current, maximum | Лимит тарифа приближается (≥90%) | §19.6 |
| `PlanLimitExceeded` | owner_type: SubscriptionOwnerType, owner_id, limit_name | Лимит тарифа превышен | §19.6 |
| `CouponApplied` | subscription_id, coupon_id, discount | Купон применён | §19.1 |
| `CouponCreated` | coupon_id, code | Купон создан | §19.1 |
| `CouponExhausted` | coupon_id | Купон исчерпан | §19.1 |
| `CancellationReasonRecorded` | subscription_id, reason | Причина отмены записана | §19.2 |

> **`PlanCreated`/`PlanUpdated`/`PlanArchived`** — события для управления тарифными планами как AR. Позволяют другим BC реагировать на изменения планов.
>
> **`SubscriptionExpired`** — подписка истекла после grace period без оплаты. Отличается от `CANCELED` (инициировано пользователем).
>
> **`BillingCycleChanged`** — пользователь переключился с месячной на годовую оплату (или наоборот).
>
> **`RefundRequested`/`Processed`/`Rejected`** — жизненный цикл возврата средств.
>
> **`CouponApplied`** — купон применён к подписке. `discount` — рассчитанная сумма скидки.
>
> **`PlanLimitApproaching`** — `owner_type: SubscriptionOwnerType` вместо строки.

## Exceptions

| Исключение | Описание |
|---|---|
| `SubscriptionNotFoundException` | Подписка не найдена |
| `InvoiceNotFoundException` | Счёт не найден |
| `PlanNotFoundException` | Тарифный план не найден |
| `PlanArchivedException` | Тарифный план архивирован, нельзя подписаться |
| `PaymentFailedException` | Платёж не прошёл |
| `CannotDowngradeException` | Нельзя понизить тариф (текущее использование > новые лимиты) |
| `CannotUpgradeSamePlanException` | Нельзя повысить до текущего плана |
| `TrialAlreadyUsedException` | Пробный период уже использован |
| `PlanLimitExceededException` | Лимит тарифа превышен |
| `CardDeclinedException` | Карта отклонена |
| `PaymentMethodNotFoundException` | Платёжный метод не найден |
| `CannotRemoveLastPaymentMethodException` | Нельзя удалить последний платёжный метод |
| `CouponNotFoundException` | Купон не найден |
| `CouponExpiredException` | Срок действия купона истёк |
| `CouponExhaustedException` | Купон исчерпан (max_uses) |
| `CouponNotApplicableException` | Купон не применим к этому плану |
| `DuplicateCouponCodeException` | Код купона уже существует |
| `RefundNotFoundException` | Возврат не найден |
| `CannotRefundProcessedException` | Нельзя повторно вернуть обработанный возврат |
| `InvalidBillingCycleException` | Некорректный цикл оплаты |
| `TransactionNotFoundException` | Транзакция не найдена |
| `DuplicatePaymentMethodException` | Платёжный метод уже привязан |

## Aggregates

### Plan (Aggregate Root)

Поля:
- name: str
- description: str | None
- price_monthly: Money | None — None для FREE
- price_yearly: Money | None — None для FREE
- billing_cycle: BillingCycle | None — по умолчанию для новых подписок
- features: list[PlanFeature]
- limits: list[PlanLimit]
- is_archived: bool — архивированные планы недоступны для новых подписок
- is_default: bool — план по умолчанию (FREE)
- sort_order: int — порядок отображения
- created_at: datetime
- updated_at: datetime

Методы:
- `create(name, price_monthly=None, price_yearly=None, billing_cycle=None)` → `Plan` (factory)
- `add_feature(name, value, description=None)`
- `remove_feature(feature_id)`
- `update_feature(feature_id, value=None, description=None)`
- `add_limit(name, value, unit=None)`
- `remove_limit(limit_id)`
- `update_limit(limit_id, value=None, unit=None)`
- `set_pricing(price_monthly, price_yearly)`
- `archive()` — архивирование, недоступно для новых подписок
- `unarchive()`
- `set_sort_order(order)`
- `has_feature(name) → bool`
- `get_feature_value(name) → str | None`
- `get_limit_value(name) → int | None`

Инварианты:
- `name` уникально среди не-архивированных планов
- `price_monthly`/`price_yearly` — None только для FREE плана
- Архивированный план нельзя изменить (кроме unarchive)
- `is_default=True` — только один план по умолчанию
- `PlanFeature.name` уникально в рамках плана
- `PlanLimit.name` уникально в рамках плана

### Subscription (Aggregate Root)

Поля:
- owner_type: SubscriptionOwnerType
- owner_id: Id (opaque, из Workspace BC или Organization BC)
- plan_id: Id (opaque, ссылка на Plan AR)
- billing_cycle: BillingCycle
- status: SubscriptionStatus
- trial_period: TrialPeriod | None
- grace_period: GracePeriod | None
- payment_methods: list[PaymentMethod]
- applied_coupon: Coupon | None
- applied_discount: Discount | None
- billing_address: BillingAddress | None
- tax_info: TaxInfo | None
- current_period_start: datetime
- current_period_end: datetime
- canceled_at: datetime | None
- cancellation_reason: str | None
- created_at: datetime
- updated_at: datetime

Методы:
- `create(owner_type, owner_id, plan_id, billing_cycle)` → `Subscription` (factory, status=ACTIVE)
- `create_with_trial(owner_type, owner_id, plan_id, billing_cycle, trial_days)` → `Subscription` (factory, status=TRIALING)
- `upgrade(new_plan_id)` — проверяет, что новый план выше текущего (app-слое)
- `downgrade(new_plan_id)` — проверяет, что текущее использование ≤ новые лимиты (app-слое)
- `change_billing_cycle(new_cycle)`
- `cancel(reason)`
- `resume()` — из CANCELED/PAUSED
- `pause()`
- `start_trial(days)` — только если trial не использован
- `extend_trial(days)` — продление текущего trial
- `start_grace_period(days)` — после неуспешной оплаты
- `end_grace_period()` — grace period завершён
- `expire()` — после grace period без оплаты
- `add_payment_method(method: PaymentMethod)`
- `remove_payment_method(method_id)`
- `set_default_payment_method(method_id)`
- `apply_coupon(coupon: Coupon)` — валидация coupon на app-слое
- `remove_coupon()`
- `set_billing_address(address: BillingAddress)`
- `set_tax_info(tax_info: TaxInfo)`

Инварианты:
- Нельзя понизить, если текущее использование > новые лимиты (проверка на app-слое через Plan AR)
- Trial можно использовать только один раз
- Grace period начинается после неуспешной оплаты
- Отмена подписки: сохраняем данные до конца оплаченного периода
- `billing_cycle` определяет периодичность списания
- `applied_coupon` — только один купон на подписку
- Нельзя изменить `plan_id` на тот же самый

### Invoice (Aggregate Root)

Поля:
- subscription_id: Id (opaque, ссылка на Subscription AR)
- line_items: list[InvoiceLineItem]
- subtotal: Money
- discount: Discount | None
- tax_amount: Money | None
- total: Money
- tax_info: TaxInfo | None
- billing_address: BillingAddress | None
- status: PaymentStatus
- transactions: list[Transaction]
- refunds: list[Refund]
- invoice_number: str
- issued_at: datetime
- due_at: datetime
- paid_at: datetime | None
- pdf_url: str | None
- created_at: datetime
- updated_at: datetime

Методы:
- `create(subscription_id, line_items, tax_info=None, billing_address=None, due_at=None)` → `Invoice` (factory, subtotal/total вычисляются из line_items)
- `add_line_item(item: InvoiceLineItem)` — только если статус PENDING
- `remove_line_item(item_id)` — только если статус PENDING
- `apply_discount(discount: Discount)` — пересчёт total
- `remove_discount()` — пересчёт total
- `calculate_tax()` — расчёт налога на основе tax_info и billing_address
- `mark_paid(transaction: Transaction)`
- `mark_failed(transaction: Transaction)`
- `request_refund(transaction_id, amount, reason)` → `Refund`
- `process_refund(refund_id)` — одобрение возврата
- `reject_refund(refund_id, reason)` — отклонение возврата
- `set_pdf_url(url)`

Инварианты:
- `invoice_number` уникален
- Оплаченный счёт нельзя редактировать (line_items, discount)
- `total` = `subtotal` - `discount` + `tax_amount`
- Возврат не может превышать сумму транзакции
- `Refund` связан с конкретной транзакцией

## Repositories

| Репозиторий | Методы |
|---|---|
| `PlanRepository` | `get_by_id`, `get_by_name`, `get_active_plans`, `get_default_plan`, `get_archived`, `search` |
| `SubscriptionRepository` | `get_by_id`, `get_by_owner`, `get_by_owner_type`, `get_by_plan`, `get_by_status`, `get_expiring_trials`, `get_in_grace_period`, `get_expiring_subscriptions`, `search` |
| `InvoiceRepository` | `get_by_id`, `get_by_subscription`, `get_by_owner`, `get_by_status`, `get_overdue`, `get_by_period`, `search` |
| `CouponRepository` | `get_by_id`, `get_by_code`, `get_active_coupons`, `get_by_status`, `search` |

> **`PlanRepository.get_active_plans`** — не-архивированные планы для отображения в UI.
>
> **`SubscriptionRepository.get_expiring_subscriptions`** — подписки с истекающим периодом для автоматического продления.
>
> **`InvoiceRepository.get_overdue`** — неоплаченные счета с прошедшим due_at.
>
> **`CouponRepository.get_by_code`** — поиск купона по коду (для применения при оформлении).

## Предустановленные тарифные планы

При инициализации создаются записи `Plan`:

| name | price_monthly | price_yearly | features | limits |
|---|---|---|---|---|
| `FREE` | None | None | [has_basic_reports, has_dm_chat] | [max_users=5, max_storage_mb=500, max_projects=3] |
| `START` | $9/user | $90/user | [has_basic_reports, has_dm_chat, has_group_chat, has_file_storage] | [max_users=15, max_storage_mb=5000, max_projects=10] |
| `PROFESSIONAL` | $19/user | $190/user | [has_basic_reports, has_advanced_reports, has_dm_chat, has_group_chat, has_channels, has_file_storage, has_epics, has_sprints, has_custom_fields, has_time_tracking] | [max_users=50, max_storage_mb=50000, max_projects=50] |
| `ENTERPRISE` | None (custom) | None (custom) | [has_all_features] | [max_users=None, max_storage_mb=None, max_projects=None] |

> Новые планы = запись `Plan`. `ENTERPRISE` — custom pricing, `max_users=None` = безлимит. `has_all_features` — все фичи доступны. Новые фичи добавляются в PlanFeature, не требуют правки кода.
