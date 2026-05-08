from __future__ import annotations

from app.shared.application.ports.security.virus_scanner_port import (
    ScanResult,
    VirusScannerPort,
)


class NoOpScannerAdapter(VirusScannerPort):
    """
    Заглушка-сканер для dev/test.

    Всегда возвращает CLEAN. **Не использовать в production** —
    включается, когда `CLAMAV_ENABLED=false`.
    """

    SCANNER_NAME = "noop:0.0.0"

    async def scan_bytes(self, data: bytes, filename: str = "") -> ScanResult:
        return ScanResult.clean(scanner=self.SCANNER_NAME)

    async def ping(self) -> bool:
        return True
