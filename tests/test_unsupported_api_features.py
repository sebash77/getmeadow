import pytest
from getmeadow import MeadowClient, MeadowAPIEndpoints, UnsupportedAPIFeatureException


def _api_mode_client() -> MeadowClient:
    """Build an API-key-mode client without hitting the network."""
    client = MeadowClient.__new__(MeadowClient)
    client._api_key_mode = True
    client.endpoints = MeadowAPIEndpoints
    return client


def test_login_only_method_raises_unsupported_api_feature():
    client = _api_mode_client()
    with pytest.raises(UnsupportedAPIFeatureException, match="cancel_order"):
        client.cancel_order(1, "test")


def test_missing_public_api_endpoint_raises_unsupported_api_feature():
    with pytest.raises(UnsupportedAPIFeatureException, match="brands"):
        MeadowAPIEndpoints.brands
