"""Shared Pydantic base class for every Powens model."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class PowensModel(BaseModel):
    """Immutable, permissive base model for all SDK models.

    - ``frozen=True``: instances are hashable and never mutated in place.
    - ``extra="ignore"``: unknown fields coming from future Powens API
      changes do not break deserialization.
    - ``populate_by_name=True``: allows the SDK to expose Pythonic aliases
      while still matching the API's snake_case payloads.
    """

    model_config = ConfigDict(
        frozen=True,
        extra="ignore",
        populate_by_name=True,
        str_strip_whitespace=True,
    )


__all__ = ["PowensModel"]
