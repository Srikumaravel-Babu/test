"""Tests for the orders API."""


class TestHealthCheck:
    def test_health_returns_ok(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestCreateOrder:
    def test_create_order_success(self, client, seed_items):
        """Test creating an order with available items."""
        response = client.post(
            "/orders",
            json={
                "customer_id": "customer-456",
                "item_ids": ["item-001", "item-002"],
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["customer_id"] == "customer-456"
        assert data["status"] == "PENDING"
        assert len(data["items"]) == 2

    def test_create_order_item_not_found(self, client, seed_items):
        """Test that ordering a non-existent item returns 404."""
        response = client.post(
            "/orders",
            json={
                "customer_id": "customer-456",
                "item_ids": ["item-001", "nonexistent-item"],
            },
        )
        assert response.status_code == 404

    def test_create_order_item_already_reserved(self, client, seed_items):
        """Test that ordering an already-reserved item returns 409."""
        response = client.post(
            "/orders",
            json={
                "customer_id": "customer-456",
                "item_ids": ["item-005"],  # This item is already RESERVED
            },
        )
        assert response.status_code == 409


class TestGetOrder:
    def test_get_order_success(self, client, seed_order_with_items):
        """Test retrieving an existing order."""
        response = client.get("/orders/order-001")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "order-001"
        assert len(data["items"]) == 3

    def test_get_order_not_found(self, client):
        """Test that a non-existent order returns 404."""
        response = client.get("/orders/nonexistent")
        assert response.status_code == 404


# ──────────────────────────────────────────────────────────────────────────────
# TODO: Add tests for POST /orders/{order_id}/pick
#
# Test cases to consider:
#   1. Happy path — pick a PENDING order, verify items sorted by shelf_location
#   2. Order not found — should return 404
#   3. Order already picked (status != PENDING) — should return 409
#   4. Verify box size calculation based on total weight
#   5. Verify item statuses updated to PICKED
# ──────────────────────────────────────────────────────────────────────────────


class TestPickOrder:
    def test_pick_order_success(self, client, seed_order_with_items):
        """
        TODO: Implement this test.

        POST /orders/order-001/pick should return a pick list with:
        - Items sorted by shelf_location
        - A suggested box size
        - Total weight
        """
        pass

    def test_pick_order_not_found(self, client):
        """
        TODO: Implement this test.

        POST /orders/nonexistent/pick should return 404.
        """
        pass
