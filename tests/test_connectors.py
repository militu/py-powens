"""Tests for the Connectors resource and model."""

from __future__ import annotations

import httpx
import respx

from powens import PowensClient
from powens.models.connector import (
    AuthMechanism,
    Connector,
    ConnectorFieldType,
    Product,
    ProvidingPayerAccount,
)

SAMPLE_CONNECTOR: dict[str, object] = {
    "id": 4,
    "uuid": "07d76adf-ae35-5b38-aca8-67aafba13169",
    "name": "Bourso",
    "hidden": False,
    "charged": True,
    "code": "40618",
    "beta": False,
    "color": "f10389",
    "slug": "BOU",
    "months_to_fetch": None,
    "auth_mechanism": "webauth",
    "available_auth_mechanisms": ["webauth"],
    "transfer_mechanism": "webauth",
    "siret": None,
    "restricted": False,
    "capabilities": ["bank", "transfer"],
    "account_usages": ["ORGA", "PRIV"],
    "products": ["bank", "wealth", "pay"],
    "payment_settings": {
        "available_validate_mechanisms": ["webauth"],
        "beneficiary_types": ["iban"],
        "execution_date_types": ["first_open_day", "deferred", "instant"],
        "execution_frequencies": ["monthly"],
        "maximum_number_of_instructions": 1,
        "providing_payer_account": "optional",
        "partial_status_tracking": [],
        "is_app_to_app_used": {"android": True, "ios": True},
        "bank_provides_payer_account": True,
        "bank_provides_payer_label": None,
        "transfer_date_types_where_trusted_beneficiary_required": [],
        "cancellation_available": True,
        "minimum_amount": {"first_open_day": 0, "instant": 0, "deferred": 0},
        "maximum_amount": {"first_open_day": 4000, "instant": 1000, "deferred": 4000},
        "minimum_date_delta_days": 1,
        "maximum_date_delta_days": 30,
    },
}


def test_connector_enums_cover_documented_values() -> None:
    assert AuthMechanism.CREDENTIALS.value == "credentials"
    assert AuthMechanism.WEBAUTH.value == "webauth"
    assert ConnectorFieldType.TEXT.value == "text"
    assert ConnectorFieldType.PASSWORD.value == "password"
    assert ConnectorFieldType.DATE.value == "date"
    assert ConnectorFieldType.LIST.value == "list"
    assert ProvidingPayerAccount.NOT_USED.value == "not_used"
    assert ProvidingPayerAccount.OPTIONAL.value == "optional"
    assert ProvidingPayerAccount.MANDATORY.value == "mandatory"
    for p in ("bank", "wealth", "bill", "pay"):
        assert Product(p).value == p


def test_connector_model_parses_full_payment_settings() -> None:
    c = Connector.model_validate(SAMPLE_CONNECTOR)
    assert c.id == 4
    assert c.uuid == "07d76adf-ae35-5b38-aca8-67aafba13169"
    assert c.auth_mechanism == "webauth"
    assert c.products == ["bank", "wealth", "pay"]
    assert c.payment_settings is not None
    assert c.payment_settings.providing_payer_account == "optional"
    assert c.payment_settings.is_app_to_app_used is not None
    assert c.payment_settings.is_app_to_app_used.android is True


@respx.mock
async def test_list_connectors_no_auth(client: PowensClient, base_url: str) -> None:
    route = respx.get(f"{base_url}/connectors").mock(
        return_value=httpx.Response(200, json={"connectors": [SAMPLE_CONNECTOR]}),
    )
    result = await client.connectors.list()
    assert len(result.connectors) == 1
    # ``auth_required=False`` means no Authorization header in the outgoing request.
    sent = route.calls.last.request
    assert "Authorization" not in sent.headers


@respx.mock
async def test_list_connectors_with_country_filter(client: PowensClient, base_url: str) -> None:
    route = respx.get(f"{base_url}/connectors").mock(
        return_value=httpx.Response(200, json={"connectors": []}),
    )
    await client.connectors.list(country_codes="fr,es")
    assert "country_codes=fr" in str(route.calls.last.request.url)


@respx.mock
async def test_get_connector_by_uuid_with_expand(client: PowensClient, base_url: str) -> None:
    uuid = str(SAMPLE_CONNECTOR["uuid"])
    route = respx.get(f"{base_url}/connectors/{uuid}").mock(
        return_value=httpx.Response(200, json=SAMPLE_CONNECTOR),
    )
    c = await client.connectors.get(connector_uuid=uuid, expand="sources,fields")
    assert c.id == 4
    sent = route.calls.last.request
    assert "expand=sources%2Cfields" in str(sent.url) or "expand=sources,fields" in str(sent.url)


@respx.mock
async def test_get_connector_sources(client: PowensClient, base_url: str) -> None:
    uuid = str(SAMPLE_CONNECTOR["uuid"])
    respx.get(f"{base_url}/connectors/{uuid}/sources").mock(
        return_value=httpx.Response(
            200,
            json={
                "sources": [
                    {
                        "id": 1,
                        "id_connector": 4,
                        "name": "direct",
                        "auth_mechanism": "webauth",
                        "available_auth_mechanisms": ["webauth"],
                        "disabled": None,
                        "priority": 1,
                        "account_usages": ["PRIV"],
                    }
                ]
            },
        ),
    )
    sources = await client.connectors.list_sources(connector_uuid=uuid)
    assert sources.sources[0].name == "direct"


@respx.mock
async def test_update_connector_requires_bearer(client: PowensClient, base_url: str) -> None:
    uuid = str(SAMPLE_CONNECTOR["uuid"])
    route = respx.put(f"{base_url}/connectors/{uuid}").mock(
        return_value=httpx.Response(200, json=SAMPLE_CONNECTOR),
    )
    await client.connectors.update(connector_uuid=uuid, body={"hidden": True})
    sent = route.calls.last.request
    assert sent.headers.get("Authorization", "").startswith("Bearer ")
