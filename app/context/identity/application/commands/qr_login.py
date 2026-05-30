from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone

from app.shared.application.base_command import BaseCommand
from app.shared.application.base_command_handler import BaseCommandHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.shared.application.ports.auth.auth_port import AuthTokenPort
from app.shared.application.ports.cache.cache_port import CachePort
from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.ip_address_vo import IpAddress
from app.context.identity.application.dto.qr_login_dto import QrLoginCreatedDTO, QrLoginPollDTO
from app.context.identity.application.exceptions.qr_login_exceptions import (
    QrLoginExpiredException,
    QrLoginInvalidStateException,
    QrLoginNotFoundException,
)
from app.context.identity.domain.aggregates.session import Session
from app.context.identity.domain.repositories.session_repository import SessionRepository
from app.context.identity.domain.repositories.user_auth_repository import UserAuthRepository
from app.context.identity.domain.repositories.user_repository import UserRepository
from app.context.identity.domain.value_objects.device_info import DeviceInfo
from app.context.identity.domain.value_objects.refresh_token import RefreshToken

QR_LOGIN_TTL_SECONDS = 300
QR_LOGIN_CACHE_PREFIX = "identity:qr_login:"


def _cache_key(token: str) -> str:
    return f"{QR_LOGIN_CACHE_PREFIX}{token}"


def _build_qr_uri(token: str, web_origin: str | None) -> str:
    if web_origin:
        base = web_origin.rstrip("/")
        return f"{base}/login/qr?token={token}"
    return f"julow://qr-login?token={token}"


class CreateQrLoginCommand(BaseCommand):
    ip: str = "127.0.0.1"
    user_agent: str = "unknown"
    web_origin: str | None = None


class CreateQrLoginHandler(BaseCommandHandler[CreateQrLoginCommand, QrLoginCreatedDTO]):
    def __init__(self, cache_port: CachePort) -> None:
        super().__init__()
        self._cache = cache_port

    async def handle(self, command: CreateQrLoginCommand) -> QrLoginCreatedDTO:
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(tz=timezone.utc) + timedelta(seconds=QR_LOGIN_TTL_SECONDS)
        payload = {
            "status": "pending",
            "created_at": datetime.now(tz=timezone.utc).isoformat(),
            "expires_at": expires_at.isoformat(),
            "ip": command.ip,
            "user_agent": command.user_agent,
        }
        await self._cache.set(_cache_key(token), payload, ttl=QR_LOGIN_TTL_SECONDS)
        return QrLoginCreatedDTO(
            qr_token=token,
            expires_at=expires_at.isoformat(),
            qr_uri=_build_qr_uri(token, command.web_origin),
        )


class ConfirmQrLoginCommand(BaseCommand):
    qr_token: str
    approver_user_id: str
    ip: str = "127.0.0.1"
    user_agent: str = "unknown"


class ConfirmQrLoginHandler(BaseCommandHandler[ConfirmQrLoginCommand, None]):
    def __init__(
        self,
        cache_port: CachePort,
        user_repo: UserRepository,
        user_auth_repo: UserAuthRepository,
        session_repo: SessionRepository,
        auth_token_port: AuthTokenPort,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._cache = cache_port
        self._user_repo = user_repo
        self._user_auth_repo = user_auth_repo
        self._session_repo = session_repo
        self._auth_token_port = auth_token_port
        self._event_bus = event_bus

    async def handle(self, command: ConfirmQrLoginCommand) -> None:
        key = _cache_key(command.qr_token)
        record = await self._cache.get(key)
        if not record:
            raise QrLoginNotFoundException()

        expires_at_raw = record.get("expires_at")
        if expires_at_raw:
            expires_at = datetime.fromisoformat(expires_at_raw)
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
            if datetime.now(tz=timezone.utc) >= expires_at:
                await self._cache.delete(key)
                raise QrLoginExpiredException()

        if record.get("status") != "pending":
            raise QrLoginInvalidStateException()

        user = await self._user_repo.get_by_id(Id.from_string(command.approver_user_id))
        if user is None:
            raise QrLoginNotFoundException()

        token_pair = self._auth_token_port.generate_token_pair(str(user.id))
        session = Session.create(
            user_id=user.id,
            device_info=DeviceInfo(user_agent=record.get("user_agent", "unknown")),
            ip_address=IpAddress(record.get("ip", "127.0.0.1")),
            is_remember_me=True,
            refresh_token=RefreshToken(value=token_pair.refresh_token),
        )

        user_auth = await self._user_auth_repo.get_by_user_id(user.id)
        if user_auth is not None:
            user_auth.record_successful_login(
                session_id=str(session.id),
                ip=IpAddress(record.get("ip", "127.0.0.1")),
                device=record.get("user_agent", "unknown"),
            )
            await self._user_auth_repo.update(user_auth)
            await self._event_bus.publish_all(user_auth.clear_domain_events())

        await self._session_repo.add(session)
        await self._event_bus.publish_all(session.clear_domain_events())

        record["status"] = "confirmed"
        record["approved_by"] = command.approver_user_id
        record["approved_at"] = datetime.now(tz=timezone.utc).isoformat()
        record["access_token"] = token_pair.access_token
        record["refresh_token"] = token_pair.refresh_token
        record["access_expires_in"] = token_pair.access_expires_in
        record["refresh_expires_in"] = token_pair.refresh_expires_in
        record["user_id"] = str(user.id)
        record["email"] = user.email.value

        ttl_left = QR_LOGIN_TTL_SECONDS
        if expires_at_raw:
            expires_at = datetime.fromisoformat(expires_at_raw)
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
            ttl_left = max(30, int((expires_at - datetime.now(tz=timezone.utc)).total_seconds()))
        await self._cache.set(key, record, ttl=ttl_left)


class PollQrLoginQuery(BaseCommand):
    qr_token: str


class PollQrLoginHandler(BaseCommandHandler[PollQrLoginQuery, QrLoginPollDTO]):
    def __init__(self, cache_port: CachePort) -> None:
        super().__init__()
        self._cache = cache_port

    async def handle(self, query: PollQrLoginQuery) -> QrLoginPollDTO:
        key = _cache_key(query.qr_token)
        record = await self._cache.get(key)
        if not record:
            return QrLoginPollDTO(status="expired")

        expires_at_raw = record.get("expires_at")
        if expires_at_raw:
            expires_at = datetime.fromisoformat(expires_at_raw)
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
            if datetime.now(tz=timezone.utc) >= expires_at:
                await self._cache.delete(key)
                return QrLoginPollDTO(status="expired")

        status = record.get("status", "pending")
        if status == "pending":
            return QrLoginPollDTO(status="pending")

        if status == "confirmed":
            dto = QrLoginPollDTO(
                status="confirmed",
                access_token=record.get("access_token"),
                refresh_token=record.get("refresh_token"),
                access_expires_in=record.get("access_expires_in"),
                refresh_expires_in=record.get("refresh_expires_in"),
                user_id=record.get("user_id"),
                email=record.get("email"),
            )
            await self._cache.delete(key)
            return dto

        return QrLoginPollDTO(status="expired")
