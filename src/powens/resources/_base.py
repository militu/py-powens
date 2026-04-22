"""Shared base class for resources."""

from __future__ import annotations

from pydantic import ValidationError

from powens._http.client import HTTPClient
from powens.exceptions import PowensSerializationError
from powens.models.base import PowensModel


class Resource:
    """Base class for every resource wrapper.

    A resource holds a reference to the shared :class:`HTTPClient` and
    provides helpers to parse payloads into Pydantic models with consistent
    error handling.
    """

    __slots__ = ("_http",)

    def __init__(self, http: HTTPClient) -> None:
        self._http = http

    @staticmethod
    def _parse[T: PowensModel](model: type[T], payload: object) -> T:
        try:
            return model.model_validate(payload)
        except ValidationError as exc:
            raise PowensSerializationError(
                f"Failed to parse Powens payload as {model.__name__}: {exc}"
            ) from exc


__all__ = ["Resource"]
