"""HTTP transport layer.

Session owns the httpx client, builds the ``/bot<token>/<method>`` URL, and
unwraps the Bot API ``{ok, result, description}`` envelope into a result value
or a typed exception. Requests carrying an InputFile are sent as multipart
form-data; all others are sent as JSON.
"""
from __future__ import annotations

import json
from collections.abc import Awaitable
from typing import Any

import httpx

from .errors import InvalidToken, NetworkError, TimedOut, error_from_response
from .types import InputFile


class Session:
    def __init__(
        self,
        token: str,
        *,
        base_url: str = "https://api.telegram.org",
        timeout: float = 30.0,
    ) -> None:
        if not token:
            raise InvalidToken("A bot token is required.")
        self._token = token
        self._base = f"{base_url}/bot{token}"
        self._file_base = f"{base_url}/file/bot{token}"
        self._http = httpx.AsyncClient(timeout=timeout)

    async def close(self) -> None:
        await self._http.aclose()

    async def call(self, method: str, /, **params: Any) -> Any:
        """Call a Bot API method and return its ``result``, or raise.

        Parameters set to None are dropped. An InputFile value triggers a
        multipart upload; other values with a to_dict() method (such as keyboard
        markups) are serialized through it.
        """
        params = {k: v for k, v in params.items() if v is not None}
        files = {k: v for k, v in params.items() if isinstance(v, InputFile)}
        url = f"{self._base}/{method}"

        if files:
            data = {k: _to_form(v) for k, v in params.items() if k not in files}
            uploads = {k: (f.filename, f.content) for k, f in files.items()}
            resp = await self._request(self._http.post(url, data=data, files=uploads))
        else:
            payload = {k: _serialize(v) for k, v in params.items()}
            resp = await self._request(self._http.post(url, json=payload))

        return self._result(resp, method)

    async def download(self, file_path: str) -> bytes:
        """Download a file's bytes given the file_path returned by getFile."""
        resp = await self._request(self._http.get(f"{self._file_base}/{file_path}"))
        resp.raise_for_status()
        return resp.content

    @staticmethod
    async def _request(coro: Awaitable[httpx.Response]) -> httpx.Response:
        """Await an httpx request, translating transport failures into our errors."""
        try:
            return await coro
        except httpx.TimeoutException as exc:
            raise TimedOut(f"Request timed out: {exc}") from exc
        except httpx.HTTPError as exc:
            raise NetworkError(f"Request failed: {exc}") from exc

    def _result(self, resp: httpx.Response, method: str) -> Any:
        data = resp.json()
        if data.get("ok"):
            return data["result"]

        code = data.get("error_code", resp.status_code)
        desc = data.get("description", "Unknown error")
        parameters = data.get("parameters") or {}
        raise error_from_response(code, desc, method, parameters)


def _serialize(value: Any) -> Any:
    """Convert a value with a to_dict() method to its dict form, else pass through."""
    to_dict = getattr(value, "to_dict", None)
    return to_dict() if callable(to_dict) else value


def _to_form(value: Any) -> str:
    """Render a non-file value as a multipart form field (JSON unless a string)."""
    to_dict = getattr(value, "to_dict", None)
    if callable(to_dict):
        value = to_dict()
    return value if isinstance(value, str) else json.dumps(value)
