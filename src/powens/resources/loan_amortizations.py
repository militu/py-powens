"""Loan amortizations resource."""

from __future__ import annotations

from powens.models.loan_amortization import LoanAmortizationsList
from powens.resources._base import Resource


class LoanAmortizationsResource(Resource):
    """Endpoints under ``/users/{userId}/amortizations``."""

    async def list(
        self,
        *,
        user_id: int | str = "me",
        account_id: int | None = None,
        connection_id: int | None = None,
    ) -> LoanAmortizationsList:
        """Calls ``GET /users/{u}/amortizations`` (or alias)."""
        if account_id is not None:
            path = f"/users/{user_id}/accounts/{account_id}/amortizations"
        elif connection_id is not None:
            path = f"/users/{user_id}/connections/{connection_id}/amortizations"
        else:
            path = f"/users/{user_id}/amortizations"
        payload = await self._http.request_json("GET", path)
        return self._parse(LoanAmortizationsList, payload)


__all__ = ["LoanAmortizationsResource"]
