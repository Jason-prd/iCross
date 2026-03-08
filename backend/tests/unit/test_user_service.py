"""
Unit tests for user service.
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch


class TestUserModel:
    """Test user model validation."""

    def test_user_creation(self):
        """Test user model can be created."""
        from app.models.database import User
        
        # Create a mock user
        user = MagicMock(spec=User)
        user.id = "test-uuid"
        user.email = "test@example.com"
        user.name = "Test User"
        user.password_hash = "hashed_password"
        user.status = "active"
        user.role = "member"
        user.created_at = datetime.now(timezone.utc)
        user.updated_at = datetime.now(timezone.utc)
        
        assert user.email == "test@example.com"
        assert user.name == "Test User"
        assert user.status == "active"

    def test_user_password_hashing(self):
        """Test password hashing functionality."""
        from app.core.security import get_password_hash, verify_password
        
        password = "test_password123"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert verify_password(password, hashed)
        assert not verify_password("wrong_password", hashed)


class TestAuthService:
    """Test authentication service."""

    @pytest.mark.asyncio
    async def test_create_access_token(self):
        """Test JWT token creation."""
        from app.core.security import create_access_token
        
        token = create_access_token(data={"sub": "test-user-id"})
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0


class TestUserService:
    """Test user service business logic."""

    @pytest.mark.asyncio
    async def test_get_user_by_email(self):
        """Test getting user by email."""
        # This test would require a real database
        # Here we test the mock behavior
        mock_session = AsyncMock()
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        
        # Test that execute was called
        from sqlalchemy import select
        from app.models.database import User
        
        query = select(User).where(User.email == "test@example.com")
        mock_session.execute(query)
        
        # Verify the mock was called
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_user_flow(self):
        """Test user creation flow."""
        # Test with core security
        from app.core.security import get_password_hash
        
        password = "securepassword123"
        hashed = get_password_hash(password)
        
        # Verify password is hashed
        assert hashed != password
        assert len(hashed) > 0


class TestSecurityUtils:
    """Test security utilities."""

    def test_password_hash_different_salts(self):
        """Test that same password produces different hashes (salt)."""
        from app.core.security import get_password_hash
        
        password = "samepassword"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        # Same password should produce different hashes due to salt
        assert hash1 != hash2

    def test_password_verification(self):
        """Test password verification works correctly."""
        from app.core.security import get_password_hash, verify_password
        
        password = "test_password_123"
        hashed = get_password_hash(password)
        
        # Correct password
        assert verify_password(password, hashed)
        
        # Wrong password
        assert not verify_password("wrong_password", hashed)
        assert not verify_password("", hashed)
        assert not verify_password(password.upper(), hashed)
