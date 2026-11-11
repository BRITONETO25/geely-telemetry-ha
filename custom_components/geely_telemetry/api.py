"""Reader for the head unit's newline-delimited, headerless telemetry stream."""

from __future__ import annotations

import asyncio
import json
from typing import Any


class TelemetryConnectionError(Exception):
    """Raised when a complete live telemetry frame cannot be read."""


async def async_fetch_telemetry(host: str, port: int) -> dict[str, Any]:
    """Read the latest trip, charge, and live-state frames from the car."""

    writer: asyncio.StreamWriter | None = None
    trip: dict[str, Any] | None = None
    charge: dict[str, Any] | None = None
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port), timeout=5
        )
        request = (
            f"GET /sync/telemetry HTTP/1.1\r\n"
            f"Host: {host}:{port}\r\n"
            "User-Agent: HomeAssistant-GeelyTelemetry\r\n"
            "Accept: */*\r\n\r\n"
        )
        writer.write(request.encode())
        await writer.drain()

        loop = asyncio.get_running_loop()
        deadline = loop.time() + 25
        while loop.time() < deadline:
            remaining = deadline - loop.time()
            line = await asyncio.wait_for(reader.readline(), timeout=remaining)
            if not line:
                break
            try:
                frame = json.loads(line.decode("utf-8").strip())
            except (UnicodeDecodeError, json.JSONDecodeError):
                continue
            if not isinstance(frame, dict):
                continue
            if isinstance(frame.get("trip"), dict):
                trip = frame["trip"]
            if isinstance(frame.get("charge"), dict):
                charge = frame["charge"]
            if "speed" in frame:
                return {"live": frame, "trip": trip, "charge": charge}

        raise TelemetryConnectionError(
            "A central não enviou um quadro de telemetria ao vivo em 25 segundos."
        )
    except (OSError, asyncio.TimeoutError) as err:
        raise TelemetryConnectionError(
            f"Não foi possível ler a telemetria em {host}:{port}: {err}"
        ) from err
    finally:
        if writer is not None:
            writer.close()
            try:
                await writer.wait_closed()
            except OSError:
                pass
