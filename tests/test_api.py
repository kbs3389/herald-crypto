"""Integration tests for the API gateway endpoints."""
import pytest
from decimal import Decimal
from fastapi.testclient import TestClient

from src.services.gateway.app import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def auth_headers(client):
    """Login and get auth headers."""
    resp = client.post("/api/v1/auth/login", json={
        "username": "demo",
        "password": "herald2026",
    })
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    data = resp.json()
    token = data.get("access_token") or data.get("token")
    return {"Authorization": f"Bearer {token}"}


class TestHealth:
    def test_health_check(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"

    def test_system_info(self, client):
        resp = client.get("/api/v1/system/info")
        assert resp.status_code == 200
        data = resp.json()
        assert "exchange_name" in data

    def test_api_health(self, client):
        resp = client.get("/api/v1/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"


class TestAuth:
    def test_login_success(self, client):
        resp = client.post("/api/v1/auth/login", json={
            "username": "demo",
            "password": "herald2026",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "token" in data or "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client):
        resp = client.post("/api/v1/auth/login", json={
            "username": "demo",
            "password": "wrong",
        })
        assert resp.status_code == 401

    def test_register_and_login(self, client):
        resp = client.post("/api/v1/auth/register", json={
            "username": "testuser_api",
            "password": "testpass123",
            "email": "testapi@herald.exchange",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["username"] == "testuser_api"

    def test_me_endpoint(self, client, auth_headers):
        resp = client.get("/api/v1/auth/me", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "user_id" in data


class TestInstruments:
    def test_list_instruments(self, client):
        resp = client.get("/api/v1/instruments")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 4  # At least spot instruments

    def test_instruments_have_required_fields(self, client):
        resp = client.get("/api/v1/instruments")
        for inst in resp.json():
            assert "id" in inst
            assert "base" in inst or "base_asset" in inst
            assert "quote" in inst or "quote_asset" in inst


class TestOrderBook:
    def test_get_orderbook(self, client):
        resp = client.get("/api/v1/orderbook/BTC-USDT-SPOT")
        assert resp.status_code == 200
        data = resp.json()
        assert "bids" in data
        assert "asks" in data

    def test_get_orderbook_v2(self, client):
        resp = client.get("/api/v1/market/BTC-USDT-SPOT/orderbook")
        assert resp.status_code == 200
        data = resp.json()
        assert "bids" in data
        assert "asks" in data

    def test_orderbook_sorted(self, client):
        resp = client.get("/api/v1/orderbook/BTC-USDT-SPOT")
        data = resp.json()
        bids = data["bids"]
        asks = data["asks"]
        if len(bids) > 1:
            # Bids should be descending
            for i in range(len(bids) - 1):
                assert float(bids[i][0]) >= float(bids[i + 1][0])
        if len(asks) > 1:
            # Asks should be ascending
            for i in range(len(asks) - 1):
                assert float(asks[i][0]) <= float(asks[i + 1][0])


class TestBalances:
    def test_get_balances(self, client, auth_headers):
        resp = client.get("/api/v1/account/balances", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "balances" in data
        balances = data["balances"]
        assert "USDT" in balances
        assert "BTC" in balances

    def test_demo_initial_balances(self, client, auth_headers):
        resp = client.get("/api/v1/account/balances", headers=auth_headers)
        balances = resp.json()["balances"]
        assert Decimal(balances["USDT"]["total"]) > 0
        assert Decimal(balances["BTC"]["total"]) > 0


class TestOrders:
    def test_place_limit_order(self, client, auth_headers):
        resp = client.post("/api/v1/orders", json={
            "instrument_id": "BTC-USDT-SPOT",
            "side": "BUY",
            "order_type": "LIMIT",
            "quantity": "0.001",
            "price": "30000",
        }, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] in ("ACCEPTED", "FILLED", "PARTIALLY_FILLED")

    def test_get_orders(self, client, auth_headers):
        client.post("/api/v1/orders", json={
            "instrument_id": "ETH-USDT-SPOT",
            "side": "BUY",
            "order_type": "LIMIT",
            "quantity": "0.01",
            "price": "2000",
        }, headers=auth_headers)
        resp = client.get("/api/v1/orders", headers=auth_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


class TestMarketData:
    def test_get_ticker(self, client):
        resp = client.get("/api/v1/ticker/BTC-USDT-SPOT")
        assert resp.status_code == 200

    def test_get_ticker_v2(self, client):
        resp = client.get("/api/v1/market/BTC-USDT-SPOT/ticker")
        assert resp.status_code == 200

    def test_get_recent_trades(self, client):
        resp = client.get("/api/v1/trades/BTC-USDT-SPOT")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


class TestMarketMaker:
    def test_market_maker_status(self, client):
        resp = client.get("/api/v1/market-maker/status")
        assert resp.status_code == 200
        data = resp.json()
        assert "market_makers" in data


class TestBlockchain:
    def test_block_heights(self, client):
        resp = client.get("/api/v1/blockchain/block-heights")
        assert resp.status_code == 200

    def test_fee_estimate(self, client):
        resp = client.get("/api/v1/blockchain/fee/ETH")
        assert resp.status_code == 200


class TestFiatEndpoints:
    def test_fiat_deposit(self, client, auth_headers):
        resp = client.post("/api/v1/fiat/deposit", json={
            "amount": "100",
            "currency": "USD",
            "payment_method": "card",
        }, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "intent_id" in data

    def test_fiat_payments(self, client, auth_headers):
        resp = client.get("/api/v1/fiat/payments", headers=auth_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)
