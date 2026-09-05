"""Fuzzes a live instance of the app against its own OpenAPI schema (schemathesis).

Guards the constitution's "implementation must match the published API contract"
rule: any handler whose real behavior diverges from its declared schema fails here.

Runs the app as a real subprocess (rather than schemathesis's in-process ASGI
loader) because schemathesis's ASGI/WSGI loaders depend on the unmaintained
``starlette-testclient`` shim, which is currently incompatible with modern
anyio releases (``anyio.start_blocking_portal`` was moved/removed). Talking to
a real server over HTTP sidesteps that broken dependency entirely.
"""

import asyncio
import atexit
import os
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, cast

import httpx
import schemathesis
from schemathesis import CheckFunction
from sqlalchemy.ext.asyncio import create_async_engine

from app.db.base import Base
from app.models import item as _item  # noqa: F401  register model metadata


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _wait_until_ready(base_url: str, timeout: float = 10.0) -> None:
    deadline = time.monotonic() + timeout
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            httpx.get(f"{base_url}/health", timeout=0.5)
            return
        except httpx.TransportError as exc:
            last_error = exc
            time.sleep(0.2)
    raise RuntimeError("live contract-test server did not become ready in time") from last_error


async def _create_schema(database_url: str) -> None:
    engine = create_async_engine(database_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()


_db_path = Path(tempfile.mkdtemp(prefix="fastapisample-contract-")) / "contract.db"
_database_url = f"sqlite+aiosqlite:///{_db_path}"

asyncio.run(_create_schema(_database_url))

_port = _free_port()
_base_url = f"http://127.0.0.1:{_port}"
_process = subprocess.Popen(  # noqa: S603
    [
        sys.executable,
        "-m",
        "uvicorn",
        "app.main:app",
        "--host",
        "127.0.0.1",
        "--port",
        str(_port),
    ],
    env={**os.environ, "DATABASE_URL": _database_url},
)
atexit.register(_process.terminate)
_wait_until_ready(_base_url)

schema = schemathesis.openapi.from_url(f"{_base_url}/openapi.json")

# Two checks are excluded as deliberate design choices, not spec gaps:
# - allow_header_conformance: FastAPI registers one route per HTTP-method decorator,
#   so Starlette's automatic 405 handler only ever reports the first matching
#   route's method in `Allow`, never the union for the path. Framework behavior,
#   not something endpoint code controls.
# - negative_data_rejection: this API intentionally ignores unknown query/body
#   properties (forward-compatible clients) instead of rejecting them with 422.
_excluded_checks = cast(
    list[CheckFunction],
    schemathesis.checks.CHECKS.get_by_names(
        ["allow_header_conformance", "negative_data_rejection"]
    ),
)


@schemathesis.pytest.parametrize(schema=schema)
def test_api_conforms_to_openapi_schema(case: schemathesis.Case[Any]) -> None:
    case.call_and_validate(excluded_checks=_excluded_checks)
