"""Unit-тесты для shared domain: Value Objects, Entities, Exceptions, Events."""

from dataclasses import dataclass
from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import UUID

import pytest

from app.shared.domain.base_aggregate import AggregateRoot
from app.shared.domain.base_domain_event import BaseDomainEvent
from app.shared.domain.base_entity import BaseEntity
from app.shared.domain.base_exceptions import DomainException
from app.shared.domain.base_value_object import ValueObject
from app.shared.domain.exceptions.business_rule_violation_exception import BusinessRuleViolationException
from app.shared.domain.exceptions.entity_not_found_exception import EntityNotFoundException
from app.shared.domain.exceptions.validation_exception import ValidationException
from app.shared.domain.value_objects.color_vo import Color
from app.shared.domain.value_objects.date_range_vo import DateRange
from app.shared.domain.value_objects.email_vo import Email
from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.ip_address_vo import IpAddress
from app.shared.domain.value_objects.language_code_vo import LanguageCode
from app.shared.domain.value_objects.money_vo import Money
from app.shared.domain.value_objects.percent_vo import Percent
from app.shared.domain.value_objects.timezone_vo import Timezone
from app.shared.domain.value_objects.url_vo import Url

from tests.factories import EmailFactory, IdFactory


# ═══════════════════════════════════════════════════════════════════════════
# Value Objects
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestId:
    def test_generate_creates_valid_id(self) -> None:
        id_ = Id.generate()
        assert isinstance(id_.value, UUID)

    def test_from_string_creates_id(self) -> None:
        raw = "550e8400-e29b-41d4-a716-446655440000"
        id_ = Id.from_string(raw)
        assert str(id_.value) == raw

    def test_from_string_invalid_raises(self) -> None:
        with pytest.raises(ValueError):
            Id.from_string("not-a-uuid")

    def test_equality_by_value(self) -> None:
        id1 = Id.generate()
        id2 = Id(value=id1.value)
        assert id1 == id2

    def test_inequality_different_values(self, any_id: Id) -> None:
        assert any_id != Id.generate()

    def test_str_representation(self, any_id: Id) -> None:
        assert str(any_id) == str(any_id.value)

    def test_factory_creates_valid_id(self) -> None:
        id_ = IdFactory()
        assert isinstance(id_.value, UUID)


@pytest.mark.unit
class TestEmail:
    def test_valid_email_normalizes_to_lowercase(self) -> None:
        email = Email("User@Example.COM")
        assert email.value == "user@example.com"

    def test_invalid_email_raises(self) -> None:
        with pytest.raises(ValidationException) as exc_info:
            Email("not-email")
        assert exc_info.value.field == "email"

    def test_equality_ignores_case(self) -> None:
        assert Email("a@b.com") == Email("A@B.COM")

    def test_str_representation(self) -> None:
        email = Email("test@example.com")
        assert str(email) == "test@example.com"

    def test_factory_creates_valid_email(self) -> None:
        email = EmailFactory()
        assert "@" in email.value


@pytest.mark.unit
class TestUrl:
    def test_valid_url(self) -> None:
        url = Url("https://example.com/path")
        assert url.value == "https://example.com/path"

    def test_invalid_url_no_scheme_raises(self) -> None:
        with pytest.raises(ValidationException) as exc_info:
            Url("example.com")
        assert exc_info.value.field == "url"

    def test_invalid_url_no_netloc_raises(self) -> None:
        with pytest.raises(ValidationException):
            Url("https://")

    def test_str_representation(self) -> None:
        url = Url("https://example.com")
        assert str(url) == "https://example.com"


@pytest.mark.unit
class TestMoney:
    def test_create_money_normalizes_currency(self) -> None:
        money = Money(Decimal("199.99"), "rub")
        assert money.amount == Decimal("199.99")
        assert money.currency == "RUB"

    def test_negative_amount_raises(self) -> None:
        with pytest.raises(ValidationException) as exc_info:
            Money(Decimal("-10"), "USD")
        assert exc_info.value.field == "amount"

    def test_non_decimal_amount_raises(self) -> None:
        with pytest.raises(ValidationException) as exc_info:
            Money(100, "USD")  # type: ignore[arg-type]
        assert exc_info.value.field == "amount"

    def test_invalid_currency_code_raises(self) -> None:
        with pytest.raises(ValidationException) as exc_info:
            Money(Decimal("10"), "US")
        assert exc_info.value.field == "currency"

    def test_str_representation(self) -> None:
        money = Money(Decimal("99.99"), "USD")
        assert str(money) == "99.99 USD"


@pytest.mark.unit
class TestPercent:
    def test_valid_percent(self) -> None:
        p = Percent(Decimal("50"))
        assert p.value == Decimal("50")

    def test_zero_is_valid(self) -> None:
        p = Percent(Decimal("0"))
        assert p.value == Decimal("0")

    def test_hundred_is_valid(self) -> None:
        p = Percent(Decimal("100"))
        assert p.value == Decimal("100")

    def test_over_100_raises(self) -> None:
        with pytest.raises(ValidationException) as exc_info:
            Percent(Decimal("101"))
        assert exc_info.value.field == "percent"

    def test_negative_raises(self) -> None:
        with pytest.raises(ValidationException) as exc_info:
            Percent(Decimal("-1"))
        assert exc_info.value.field == "percent"

    def test_non_decimal_raises(self) -> None:
        with pytest.raises(ValidationException):
            Percent(50)  # type: ignore[arg-type]

    def test_str_representation(self) -> None:
        assert str(Percent(Decimal("15.5"))) == "15.5%"


@pytest.mark.unit
class TestColor:
    def test_valid_color_normalizes_to_uppercase(self) -> None:
        color = Color("#ff5500")
        assert color.value == "#FF5500"

    def test_whitespace_is_stripped(self) -> None:
        color = Color("  #aabbcc  ")
        assert color.value == "#AABBCC"

    def test_invalid_color_name_raises(self) -> None:
        with pytest.raises(ValidationException) as exc_info:
            Color("red")
        assert exc_info.value.field == "color"

    def test_short_hex_raises(self) -> None:
        with pytest.raises(ValidationException):
            Color("#fff")

    def test_str_representation(self) -> None:
        assert str(Color("#000000")) == "#000000"


@pytest.mark.unit
class TestDateRange:
    def test_valid_range(self) -> None:
        dr = DateRange(date(2025, 1, 1), date(2025, 12, 31))
        assert dr.start == date(2025, 1, 1)
        assert dr.end == date(2025, 12, 31)

    def test_same_date_is_valid(self) -> None:
        dr = DateRange(date(2025, 6, 1), date(2025, 6, 1))
        assert dr.start == dr.end

    def test_start_after_end_raises(self) -> None:
        with pytest.raises(ValidationException) as exc_info:
            DateRange(date(2025, 12, 31), date(2025, 1, 1))
        assert exc_info.value.field == "date_range"

    def test_str_representation(self) -> None:
        dr = DateRange(date(2025, 1, 1), date(2025, 12, 31))
        assert "2025-01-01" in str(dr)


@pytest.mark.unit
class TestIpAddress:
    def test_valid_ipv4(self) -> None:
        ip = IpAddress("192.168.1.1")
        assert ip.is_ipv4
        assert not ip.is_ipv6

    def test_valid_ipv6(self) -> None:
        ip = IpAddress("::1")
        assert ip.is_ipv6
        assert not ip.is_ipv4

    def test_invalid_ip_raises(self) -> None:
        with pytest.raises(ValidationException) as exc_info:
            IpAddress("999.999.999.999")
        assert exc_info.value.field == "ip_address"

    def test_str_representation(self) -> None:
        assert str(IpAddress("10.0.0.1")) == "10.0.0.1"


@pytest.mark.unit
class TestLanguageCode:
    def test_valid_code_normalizes_to_lowercase(self) -> None:
        lang = LanguageCode("RU")
        assert lang.value == "ru"

    def test_lowercase_code_stays_lowercase(self) -> None:
        lang = LanguageCode("en")
        assert lang.value == "en"

    def test_invalid_code_raises(self) -> None:
        with pytest.raises(ValidationException) as exc_info:
            LanguageCode("xx")
        assert exc_info.value.field == "language_code"

    def test_three_letter_code_raises(self) -> None:
        with pytest.raises(ValidationException):
            LanguageCode("eng")

    def test_str_representation(self) -> None:
        assert str(LanguageCode("ru")) == "ru"


@pytest.mark.unit
class TestTimezone:
    def test_iana_timezone(self) -> None:
        tz = Timezone("Europe/Moscow")
        assert tz.is_iana
        assert not tz.is_utc_offset

    def test_utc_positive_offset(self) -> None:
        tz = Timezone("UTC+3")
        assert tz.is_utc_offset
        assert not tz.is_iana

    def test_utc_offset_with_minutes(self) -> None:
        tz = Timezone("UTC+05:30")
        assert tz.is_utc_offset

    def test_utc_negative_offset(self) -> None:
        tz = Timezone("UTC-5")
        assert tz.is_utc_offset

    def test_invalid_timezone_raises(self) -> None:
        with pytest.raises(ValidationException) as exc_info:
            Timezone("Invalid/Zone")
        assert exc_info.value.field == "timezone"

    def test_to_tzinfo_returns_zone_info(self) -> None:
        from zoneinfo import ZoneInfo

        tz = Timezone("Europe/Moscow")
        assert isinstance(tz.to_tzinfo(), ZoneInfo)

    def test_to_tzinfo_returns_timezone_for_offset(self) -> None:
        tz = Timezone("UTC+3")
        result = tz.to_tzinfo()
        assert isinstance(result, timezone)

    def test_str_representation(self) -> None:
        assert str(Timezone("UTC+3")) == "UTC+3"


# ═══════════════════════════════════════════════════════════════════════════
# ValueObject base
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestValueObject:
    def test_clone(self) -> None:
        email = Email("test@example.com")
        cloned = email.clone(value="other@example.com")
        assert cloned.value == "other@example.com"
        assert email.value == "test@example.com"

    def test_frozen(self) -> None:
        email = Email("test@example.com")
        with pytest.raises(AttributeError):
            email.value = "changed@example.com"  # type: ignore[misc]

    def test_hash(self) -> None:
        email1 = Email("test@example.com")
        email2 = Email("test@example.com")
        assert hash(email1) == hash(email2)
        assert {email1, email2} == {email1}


# ═══════════════════════════════════════════════════════════════════════════
# BaseEntity
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestBaseEntity:
    def test_default_id(self) -> None:
        @dataclass
        class FakeEntity(BaseEntity):
            pass

        entity = FakeEntity()
        assert isinstance(entity.id, Id)

    def test_equality_by_id(self) -> None:
        @dataclass
        class FakeEntity(BaseEntity):
            pass

        shared_id = Id.generate()
        e1 = FakeEntity(id=shared_id)
        e2 = FakeEntity(id=shared_id)
        assert e1 == e2

    def test_inequality_different_id(self) -> None:
        @dataclass
        class FakeEntity(BaseEntity):
            pass

        e1 = FakeEntity()
        e2 = FakeEntity()
        assert e1 != e2

    def test_inequality_different_type(self) -> None:
        @dataclass
        class EntityA(BaseEntity):
            pass

        @dataclass
        class EntityB(BaseEntity):
            pass

        shared_id = Id.generate()
        assert EntityA(id=shared_id) != EntityB(id=shared_id)


# ═══════════════════════════════════════════════════════════════════════════
# AggregateRoot & Domain Events
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestAggregateRoot:
    def test_register_event(self) -> None:
        @dataclass
        class FakeAggregate(AggregateRoot):
            name: str = "test"

        agg = FakeAggregate()
        event = BaseDomainEvent()
        agg._register_event(event)
        assert len(agg.domain_events) == 1
        assert agg.domain_events[0].aggregate_id == agg.id
        assert agg.domain_events[0].aggregate_type == "FakeAggregate"

    def test_clear_events(self) -> None:
        @dataclass
        class FakeAggregate(AggregateRoot):
            pass

        agg = FakeAggregate()
        agg._register_event(BaseDomainEvent())
        events = agg.clear_domain_events()
        assert len(events) == 1
        assert len(agg.domain_events) == 0


@pytest.mark.unit
class TestBaseDomainEvent:
    def test_default_fields(self) -> None:
        event = BaseDomainEvent()
        assert isinstance(event.event_id, Id)
        assert isinstance(event.occurred_at, datetime)
        assert event.event_type == "BaseDomainEvent"

    def test_frozen(self) -> None:
        event = BaseDomainEvent()
        with pytest.raises(AttributeError):
            event.event_type = "changed"  # type: ignore[misc]


# ═══════════════════════════════════════════════════════════════════════════
# Exceptions
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestDomainException:
    def test_base_exception(self) -> None:
        exc = DomainException("test error")
        assert exc.message == "test error"
        assert str(exc) == "test error"


@pytest.mark.unit
class TestValidationException:
    def test_attributes(self) -> None:
        exc = ValidationException(field="email", message="invalid")
        assert exc.field == "email"
        assert exc.message == "invalid"

    def test_is_domain_exception(self) -> None:
        exc = ValidationException(field="test", message="err")
        assert isinstance(exc, DomainException)


@pytest.mark.unit
class TestEntityNotFoundException:
    def test_default_message(self) -> None:
        exc = EntityNotFoundException(entity_type="User", id=42)
        assert "User" in exc.message
        assert "42" in exc.message

    def test_custom_message(self) -> None:
        exc = EntityNotFoundException(entity_type="User", id=1, message="custom")
        assert exc.message == "custom"

    def test_is_domain_exception(self) -> None:
        exc = EntityNotFoundException(entity_type="X", id=1)
        assert isinstance(exc, DomainException)


@pytest.mark.unit
class TestBusinessRuleViolationException:
    def test_attributes(self) -> None:
        exc = BusinessRuleViolationException(rule="UniqueEmail", message="duplicate")
        assert exc.rule == "UniqueEmail"
        assert exc.message == "duplicate"

    def test_is_domain_exception(self) -> None:
        exc = BusinessRuleViolationException(rule="test", message="err")
        assert isinstance(exc, DomainException)
