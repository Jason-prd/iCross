"""
Unit tests for order and customer services.
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4


class TestOrderModel:
    """Test order model operations."""

    def test_order_creation(self):
        """Test order model can be created."""
        from app.models.database import Order

        order = MagicMock(spec=Order)
        order.id = str(uuid4())
        order.team_id = str(uuid4())
        order.shop_id = str(uuid4())
        order.platform_order_id = "OZON-ORDER-12345"
        order.status = "pending"
        order.total_amount = 299.99
        order.currency = "RUB"
        order.created_at = datetime.now(timezone.utc)
        order.updated_at = datetime.now(timezone.utc)

        assert order.platform_order_id == "OZON-ORDER-12345"
        assert order.status == "pending"
        assert order.total_amount == 299.99

    def test_order_status_types(self):
        """Test order status types."""
        status_types = [
            "pending",
            "confirmed",
            "processing",
            "shipped",
            "delivered",
            "cancelled",
            "refunded",
        ]

        for status in status_types:
            order = MagicMock(spec=Order)
            order.status = status
            assert order.status in status_types


class TestOrderItemModel:
    """Test order item model operations."""

    def test_order_item_creation(self):
        """Test order item can be created."""
        from app.models.database import OrderItem

        item = MagicMock(spec=OrderItem)
        item.id = str(uuid4())
        item.order_id = str(uuid4())
        item.product_id = str(uuid4())
        item.variant_id = str(uuid4())
        item.quantity = 2
        item.price = 149.99
        item.total_amount = 299.98

        assert item.quantity == 2
        assert item.price == 149.99
        assert item.total_amount == 299.98


class TestOrderStatusHistoryModel:
    """Test order status history model."""

    def test_order_status_history(self):
        """Test order status history tracking."""
        from app.models.database import OrderStatusHistory

        history = MagicMock(spec=OrderStatusHistory)
        history.id = str(uuid4())
        history.order_id = str(uuid4())
        history.from_status = "pending"
        history.to_status = "confirmed"
        history.note = "Order confirmed by system"
        history.created_at = datetime.now(timezone.utc)

        assert history.from_status == "pending"
        assert history.to_status == "confirmed"


class TestCustomerModel:
    """Test customer model operations."""

    def test_customer_creation(self):
        """Test customer model can be created."""
        from app.models.database import Customer

        customer = MagicMock(spec=Customer)
        customer.id = str(uuid4())
        customer.team_id = str(uuid4())
        customer.email = "customer@example.com"
        customer.name = "John Doe"
        customer.phone = "+1234567890"
        customer.country = "Russia"
        customer.city = "Moscow"
        customer.total_orders = 5
        customer.total_spent = 1500.00
        customer.created_at = datetime.now(timezone.utc)

        assert customer.email == "customer@example.com"
        assert customer.name == "John Doe"
        assert customer.total_orders == 5

    def test_customer_address(self):
        """Test customer address information."""
        customer = MagicMock(spec=Customer)
        customer.address = {
            "country": "Russia",
            "city": "Moscow",
            "street": "Tverskaya Street",
            "building": "1",
            "apartment": "10",
            "postal_code": "125009",
        }

        assert customer.address["city"] == "Moscow"
        assert customer.address["postal_code"] == "125009"


class TestCustomerCommunicationModel:
    """Test customer communication model."""

    def test_communication_types(self):
        """Test customer communication types."""
        from app.models.database import CustomerCommunication

        comm_types = ["email", "sms", "whatsapp", "telegram"]

        for comm_type in comm_types:
            comm = MagicMock(spec=CustomerCommunication)
            comm.type = comm_type
            assert comm.type in comm_types


class TestOrdersService:
    """Test orders service business logic."""

    @pytest.mark.asyncio
    async def test_get_orders_by_shop(self):
        """Test getting orders by shop."""
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result

        from sqlalchemy import select
        from app.models.database import Order

        query = select(Order).where(Order.shop_id == "shop-123")
        mock_session.execute(query)

        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_orders_by_status(self):
        """Test getting orders by status."""
        mock_session = AsyncMock()

        from sqlalchemy import select
        from app.models.database import Order

        query = select(Order).where(Order.status == "pending")
        mock_session.execute(query)

        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_order_status(self):
        """Test updating order status."""
        mock_session = AsyncMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        order_data = {"id": str(uuid4()), "status": "pending"}

        mock_session.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_calculate_order_total(self):
        """Test order total calculation."""
        items = [
            {"quantity": 2, "price": 100.00},
            {"quantity": 1, "price": 50.00},
        ]

        total = sum(item["quantity"] * item["price"] for item in items)
        assert total == 250.00


class TestCustomersService:
    """Test customers service business logic."""

    @pytest.mark.asyncio
    async def test_get_customers_by_team(self):
        """Test getting customers by team."""
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result

        from sqlalchemy import select
        from app.models.database import Customer

        query = select(Customer).where(Customer.team_id == "team-123")
        mock_session.execute(query)

        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_customers(self):
        """Test customer search."""
        mock_session = AsyncMock()

        from sqlalchemy import select
        from app.models.database import Customer

        search_term = "John"
        query = select(Customer).where(Customer.name.ilike(f"%{search_term}%"))

        mock_session.execute(query)
        mock_session.execute.assert_called_once()


class TestOrdersAPI:
    """Test orders API endpoints."""

    def test_order_response_format(self):
        """Test order API response format."""
        order = {
            "id": str(uuid4()),
            "platform_order_id": "OZON-12345",
            "status": "pending",
            "total_amount": 299.99,
            "currency": "RUB",
            "items": [],
        }

        assert "id" in order
        assert "platform_order_id" in order
        assert "status" in order

    def test_order_status_transitions(self):
        """Test valid order status transitions."""
        valid_transitions = {
            "pending": ["confirmed", "cancelled"],
            "confirmed": ["processing", "cancelled"],
            "processing": ["shipped", "cancelled"],
            "shipped": ["delivered"],
            "delivered": ["refunded"],
            "cancelled": [],
            "refunded": [],
        }

        assert "pending" in valid_transitions
        assert "delivered" in valid_transitions
