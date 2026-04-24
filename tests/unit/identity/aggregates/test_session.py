"""Unit-тесты для агрегата Session (Identity BC)."""

from datetime import datetime, timedelta, timezone

import pytest

from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.ip_address_vo import IpAddress
from app.context.identity.domain.aggregates.session import Session
from app.context.identity.domain.exceptions.session_exceptions import InactiveSessionException
from app.context.identity.domain.events.session_events import (
    AllOtherSessionsTerminated,
    SessionCreated,
    SessionRefreshed,
    SessionTerminated,
)
from app.context.identity.domain.value_objects.device_info import DeviceInfo
from app.context.identity.domain.value_objects.geolocation import Geolocation
from app.context.identity.domain.value_objects.refresh_token import RefreshToken
from tests.factories import IdFactory, RefreshTokenFactory


# ═══════════════════════════════════════════════════════════════════════════
# Создание сессии
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestSessionCreation:
    def test_create_session(self, active_session: Session) -> None:
        session = active_session
        assert session.is_active
        assert session.user_id is not None
        assert not session.is_remember_me

    def test_create_session_emits_event(self, active_session: Session) -> None:
        session = active_session
        events = session.clear_domain_events()
        assert len(events) == 1
        assert isinstance(events[0], SessionCreated)

    def test_create_session_with_remember_me(self, any_device_info: DeviceInfo, any_ip: IpAddress, any_refresh_token: RefreshToken) -> None:
        session = Session.create(
            user_id=IdFactory(),
            device_info=any_device_info,
            ip_address=any_ip,
            is_remember_me=True,
            refresh_token=any_refresh_token,
        )
        assert session.is_remember_me

    def test_create_session_remember_me_longer_expiry(self, any_device_info: DeviceInfo, any_ip: IpAddress, any_refresh_token: RefreshToken) -> None:
        session_remember = Session.create(user_id=IdFactory(), device_info=any_device_info, ip_address=any_ip, is_remember_me=True, refresh_token=any_refresh_token)
        session_normal = Session.create(user_id=IdFactory(), device_info=any_device_info, ip_address=any_ip, is_remember_me=False, refresh_token=any_refresh_token)
        assert session_remember.expires_at > session_normal.expires_at

    def test_create_session_with_geolocation(self) -> None:
        user_id = IdFactory()
        geo = Geolocation(country="Russia", city="Moscow", latitude=55.75, longitude=37.62)
        session = Session.create(
            user_id=user_id,
            device_info=DeviceInfo(user_agent="Mozilla/5.0"),
            ip_address=IpAddress("192.168.1.1"),
            geolocation=geo,
        )
        assert session.geolocation == geo

    def test_create_session_with_custom_expiry(self) -> None:
        user_id = IdFactory()
        custom_expiry = datetime.now(tz=timezone.utc) + timedelta(days=7)
        session = Session.create(
            user_id=user_id,
            device_info=DeviceInfo(user_agent="Mozilla/5.0"),
            ip_address=IpAddress("192.168.1.1"),
            expires_at=custom_expiry,
        )
        assert session.expires_at == custom_expiry


# ═══════════════════════════════════════════════════════════════════════════
# Завершение сессии
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestSessionTermination:
    def test_terminate_session(self, active_session: Session) -> None:
        session = active_session
        session.terminate()
        assert not session.is_active
        assert session.terminated_at is not None

    def test_terminate_session_emits_event(self, active_session: Session) -> None:
        session = active_session
        session.clear_domain_events()
        session.terminate()
        events = session.clear_domain_events()
        assert any(isinstance(e, SessionTerminated) for e in events)

    def test_terminate_already_terminated_is_noop(self, active_session: Session) -> None:
        session = active_session
        session.terminate()
        session.clear_domain_events()
        session.terminate()
        events = session.clear_domain_events()
        assert not any(isinstance(e, SessionTerminated) for e in events)


# ═══════════════════════════════════════════════════════════════════════════
# Истечение сессии
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestSessionExpiry:
    def test_is_expired_when_past(self, active_session: Session) -> None:
        session = active_session
        session.expires_at = datetime.now(tz=timezone.utc) - timedelta(hours=1)
        assert session.is_expired()

    def test_is_not_expired_when_future(self, active_session: Session) -> None:
        session = active_session
        session.expires_at = datetime.now(tz=timezone.utc) + timedelta(hours=1)
        assert not session.is_expired()


# ═══════════════════════════════════════════════════════════════════════════
# Обновление сессии (refresh)
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestSessionRefresh:
    def test_refresh_session(self, active_session: Session) -> None:
        session = active_session
        new_token = RefreshTokenFactory()
        new_expiry = datetime.now(tz=timezone.utc) + timedelta(days=30)
        session.refresh(new_token, new_expiry)
        assert session.refresh_token == new_token
        assert session.expires_at == new_expiry

    def test_refresh_session_emits_event(self, active_session: Session) -> None:
        session = active_session
        session.clear_domain_events()
        new_token = RefreshTokenFactory()
        new_expiry = datetime.now(tz=timezone.utc) + timedelta(days=30)
        session.refresh(new_token, new_expiry)
        events = session.clear_domain_events()
        assert any(isinstance(e, SessionRefreshed) for e in events)

    def test_refresh_terminated_session_raises(self, active_session: Session) -> None:
        session = active_session
        session.terminate()
        with pytest.raises(InactiveSessionException):
            session.refresh(RefreshTokenFactory(), datetime.now(tz=timezone.utc) + timedelta(days=1))


# ═══════════════════════════════════════════════════════════════════════════
# Событие завершения всех других сессий
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestAllOtherSessionsTerminated:
    def test_create_event(self) -> None:
        user_id = IdFactory()
        current_session_id = IdFactory()
        event = Session.create_all_other_sessions_terminated_event(user_id, current_session_id)
        assert isinstance(event, AllOtherSessionsTerminated)
        assert event.user_id == str(user_id)
        assert event.current_session_id == str(current_session_id)
