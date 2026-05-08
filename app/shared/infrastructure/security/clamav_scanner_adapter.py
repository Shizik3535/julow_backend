from __future__ import annotations

import asyncio
import struct

from app.core.logging import get_logger
from app.shared.application.ports.security.virus_scanner_port import (
    ScanResult,
    VirusScannerPort,
)

logger = get_logger(__name__)


class ClamAvScannerAdapter(VirusScannerPort):
    """
    Async-клиент ClamAV (clamd) через TCP-протокол INSTREAM.

    Не использует внешние библиотеки: реализует протокол поверх
    ``asyncio.open_connection``.

    Протокол INSTREAM:
        1. Команда:        ``zINSTREAM\\0``  (z-prefix + null-terminator)
        2. Чанки данных:   <4 байта BE длины> + <данные>
        3. Конец потока:   <4 байта BE = 0>
        4. Ответ:          ``stream: OK\\0``  или  ``stream: <Virus> FOUND\\0``

    Аргументы конструктора:
        host: Хост clamd.
        port: TCP-порт clamd.
        timeout_seconds: Общий таймаут операции.
        chunk_size_bytes: Размер чанка передачи (≤ ``StreamMaxLength`` clamd).
    """

    SCANNER_NAME = "clamav"

    def __init__(
        self,
        host: str,
        port: int,
        timeout_seconds: float = 60.0,
        chunk_size_bytes: int = 1024 * 1024,
    ) -> None:
        self._host = host
        self._port = port
        self._timeout = timeout_seconds
        self._chunk_size = chunk_size_bytes

    async def ping(self) -> bool:
        try:
            response = await self._send_command(b"zPING\0")
        except Exception as exc:  # noqa: BLE001
            logger.warning("ClamAV ping failed", host=self._host, port=self._port, error=str(exc))
            return False
        return response.strip(b"\x00").strip() == b"PONG"

    async def scan_bytes(self, data: bytes, filename: str = "") -> ScanResult:
        try:
            response = await asyncio.wait_for(
                self._instream(data),
                timeout=self._timeout,
            )
        except asyncio.TimeoutError:
            logger.error("ClamAV scan timeout", filename=filename, size=len(data))
            return ScanResult.error(
                scanner=self.SCANNER_NAME,
                message=f"timeout after {self._timeout}s",
            )
        except Exception as exc:  # noqa: BLE001
            logger.error("ClamAV scan failed", filename=filename, error=str(exc))
            return ScanResult.error(scanner=self.SCANNER_NAME, message=str(exc))

        return self._parse_response(response, filename=filename)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    async def _instream(self, data: bytes) -> bytes:
        reader, writer = await asyncio.open_connection(self._host, self._port)
        try:
            writer.write(b"zINSTREAM\0")
            await writer.drain()

            for offset in range(0, len(data), self._chunk_size):
                chunk = data[offset : offset + self._chunk_size]
                writer.write(struct.pack("!I", len(chunk)))
                writer.write(chunk)
                await writer.drain()

            # Конец потока — нулевой размер.
            writer.write(struct.pack("!I", 0))
            await writer.drain()

            response = await reader.read(4096)
            return response
        finally:
            writer.close()
            try:
                await writer.wait_closed()
            except Exception:  # noqa: BLE001
                pass

    async def _send_command(self, command: bytes) -> bytes:
        reader, writer = await asyncio.open_connection(self._host, self._port)
        try:
            writer.write(command)
            await writer.drain()
            return await asyncio.wait_for(reader.read(4096), timeout=self._timeout)
        finally:
            writer.close()
            try:
                await writer.wait_closed()
            except Exception:  # noqa: BLE001
                pass

    def _parse_response(self, response: bytes, filename: str) -> ScanResult:
        text = response.decode("utf-8", errors="replace").strip().strip("\x00").strip()
        # Примеры:
        #   "stream: OK"
        #   "stream: Eicar-Test-Signature FOUND"
        #   "stream: <error> ERROR"
        if text.endswith(": OK") or text == "OK" or text.endswith(" OK"):
            logger.debug("ClamAV: clean", filename=filename)
            return ScanResult.clean(scanner=self.SCANNER_NAME)
        if text.endswith("FOUND"):
            # формат: "stream: <virus_name> FOUND"
            try:
                payload = text.split(":", 1)[1].strip()  # "<virus_name> FOUND"
                virus_name = payload.rsplit(" ", 1)[0].strip()
            except Exception:  # noqa: BLE001
                virus_name = "UNKNOWN"
            logger.warning("ClamAV: infected", filename=filename, virus=virus_name)
            return ScanResult.infected(scanner=self.SCANNER_NAME, virus_name=virus_name)
        if text.endswith("ERROR"):
            logger.error("ClamAV: error", filename=filename, response=text)
            return ScanResult.error(scanner=self.SCANNER_NAME, message=text)
        # Неизвестный ответ — трактуем как error.
        logger.error("ClamAV: unexpected response", filename=filename, response=text)
        return ScanResult.error(
            scanner=self.SCANNER_NAME, message=f"unexpected response: {text!r}"
        )
