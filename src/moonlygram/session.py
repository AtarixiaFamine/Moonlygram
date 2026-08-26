"""HTTP transport layer.

Session owns the httpx client, builds the ``/bot<token>/<method>`` URL, and
unwraps the Bot API ``{ok, result, description}`` envelope into a result value
or a typed exception. Requests carrying an InputFile are sent as multipart
form-data; all others are sent as JSON. A file nested inside a media object is
hoisted into its own part and referenced by an ``attach://`` name, which is how
the Bot API takes an upload that is not a top-level parameter.
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

        Parameters set to None are dropped. An InputFile triggers a multipart
        upload, whether it is the parameter itself or nested inside a media
        object; other values with a to_dict() method (such as keyboard markups)
        are serialized through it.
        """
        params = {k: v for k, v in params.items() if v is not None}
        files = {k: v for k, v in params.items() if isinstance(v, InputFile)}
        payload = {
            k: _attach(_serialize(v), files)
            for k, v in params.items()
            if k not in files
        }
        url = f"{self._base}/{method}"

        if files:
            data = {k: _to_form(v) for k, v in payload.items()}
            uploads = {k: (f.filename, f.content) for k, f in files.items()}
            resp = await self._request(self._http.post(url, data=data, files=uploads))
        else:
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
    """Convert a value to its JSON form, recursing through lists and dicts.

    Anything with a to_dict() method is serialized through it. Lists and dicts
    are walked so that a list of objects (message entities, media items) works
    the same as a single one.
    """
    to_dict = getattr(value, "to_dict", None)
    if callable(to_dict):
        return _serialize(to_dict())
    if isinstance(value, list):
        return [_serialize(v) for v in value]
    if isinstance(value, dict):
        return {k: _serialize(v) for k, v in value.items()}
    return value


def _attach(value: Any, files: dict[str, InputFile]) -> Any:
    """Swap nested InputFiles for attach:// names, collecting them into files.

    A file the Bot API takes inside an object (a media group item, an edited
    message's media, a sticker) travels as its own multipart part; the object
    names that part instead of carrying the bytes. Walks lists and dicts, so one
    call covers a list of media items.
    """
    if isinstance(value, InputFile):
        name = f"attached{len(files)}"
        files[name] = value
        return f"attach://{name}"
    if isinstance(value, list):
        return [_attach(v, files) for v in value]
    if isinstance(value, dict):
        return {k: _attach(v, files) for k, v in value.items()}
    return value


def _to_form(value: Any) -> str:
    """Render an already-serialized value as a multipart form field."""
    return value if isinstance(value, str) else json.dumps(value)
