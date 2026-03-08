"""
Pytest configuration and fixtures for iCross backend tests.
"""

import os
import sys
from pathlib import Path
from typing import Generator
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))


# Test database URL
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "sqlite+aiosqlite:///:memory:"
)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_db_session():
    """Create a mock database session for testing."""
    session = AsyncMock(spec=AsyncSession)
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    return session


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "password": "password123",
        "name": "Test User",
        "phone": "+1234567890",
    }


@pytest.fixture
def sample_shop_data():
    """Sample shop data for testing."""
    return {
        "name": "Test Ozon Shop",
        "platform": "ozon",
        "api_credentials": {
            "client_id": "123456",
            "api_key": "test_api_key",
        },
    }


@pytest.fixture
def sample_product_data():
    """Sample product data for testing."""
    return {
        "offer_id": "TEST001",
        "title": "Test Product",
        "price": 1000.0,
        "stock": 50,
        "category_id": 17027500,
    }


@pytest.fixture
def mock_ozon_adapter():
    """Create a mock Ozon adapter for testing."""
    adapter = AsyncMock()
    adapter.connect = AsyncMock(return_value=True)
    adapter.get_products = AsyncMock(return_value=[])
    adapter.get_categories = AsyncMock(return_value=[])
    adapter.get_description_category_tree = AsyncMock(return_value=[])
    adapter.close = AsyncMock()
    return adapter


# Configure asyncio mode for pytest-asyncio
def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line(
        "markers", "asyncio: mark test as an asyncio test"
    )
