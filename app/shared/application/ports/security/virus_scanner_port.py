from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum


class ScanVerdict(str, Enum):
    """Вердикт сканера."""

    CLEAN = "clean"
    INFECTED = "infected"
    ERROR = "error"
    SKIPPED = "skipped"


@dataclass(frozen=True)
class ScanResult:
    """
    Результат проверки файла на вирусы.

    Атрибуты:
        verdict: Итоговый вердикт.
        virus_name: Имя вируса (для INFECTED).
        scanner: Имя/версия сканера, выдавшего вердикт (для аудита).
        scanned_at: Время завершения сканирования (UTC).
        message: Дополнительное сообщение (для ERROR/SKIPPED).
    """

    verdict: ScanVerdict
    scanner: str
    scanned_at: datetime
    virus_name: str | None = None
    message: str | None = None

    @property
    def is_clean(self) -> bool:
        return self.verdict == ScanVerdict.CLEAN

    @property
    def is_infected(self) -> bool:
        return self.verdict == ScanVerdict.INFECTED

    @classmethod
    def clean(cls, scanner: str) -> "ScanResult":
        return cls(
            verdict=ScanVerdict.CLEAN,
            scanner=scanner,
            scanned_at=datetime.now(tz=timezone.utc),
        )

    @classmethod
    def infected(cls, scanner: str, virus_name: str) -> "ScanResult":
        return cls(
            verdict=ScanVerdict.INFECTED,
            scanner=scanner,
            scanned_at=datetime.now(tz=timezone.utc),
            virus_name=virus_name,
        )

    @classmethod
    def error(cls, scanner: str, message: str) -> "ScanResult":
        return cls(
            verdict=ScanVerdict.ERROR,
            scanner=scanner,
            scanned_at=datetime.now(tz=timezone.utc),
            message=message,
        )

    @classmethod
    def skipped(cls, scanner: str, message: str = "") -> "ScanResult":
        return cls(
            verdict=ScanVerdict.SKIPPED,
            scanner=scanner,
            scanned_at=datetime.now(tz=timezone.utc),
            message=message,
        )


class VirusScannerPort(ABC):
    """
    Порт для антивирусного сканера.

    Application-слой зависит от этого порта. Реализации
    (ClamAV / VirusTotal / NoOp) живут в infrastructure-слое.

    Все методы — async, поскольку реальные сканеры работают по сети
    (clamd по TCP, REST API VirusTotal и т.д.).
    """

    @abstractmethod
    async def scan_bytes(self, data: bytes, filename: str = "") -> ScanResult:
        """Просканировать содержимое файла, переданное в памяти."""

    @abstractmethod
    async def ping(self) -> bool:
        """Проверить доступность сканера (для healthcheck/диагностики)."""
