# iCross Backend Tests

This directory contains the test suite for the iCross backend.

## Test Structure

```
tests/
├── unit/                  # Unit tests
│   ├── test_user_service.py
│   └── test_ozon_adapter.py
├── integration/           # Integration tests
│   └── test_user_api.py
├── conftest.py           # Pytest fixtures
└── pytest.ini            # Pytest configuration
```

## Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_user_service.py

# Run with coverage
pytest --cov=app --cov-report=html

# Run integration tests only
pytest -m integration
```

## Test Markers

- `unit`: Unit tests
- `integration`: Integration tests
- `e2e`: End-to-end tests
- `slow`: Slow running tests
- `db`: Tests that require database
