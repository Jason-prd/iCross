"""
Ozon Integration Exception Classes

Defines exception types for Ozon platform integration.
"""


class OzonIntegrationError(Exception):
    """Base exception for Ozon integration"""

    def __init__(self, message: str, code: str = "OZON_INTEGRATION_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class OzonConnectionError(OzonIntegrationError):
    """Ozon connection exception"""

    def __init__(self, message: str = "Failed to connect to Ozon API"):
        super().__init__(message, "OZON_CONNECTION_ERROR")


class OzonAuthenticationError(OzonIntegrationError):
    """Ozon authentication exception"""

    def __init__(self, message: str = "Ozon API authentication failed"):
        super().__init__(message, "OZON_AUTHENTICATION_ERROR")


class OzonRateLimitError(OzonIntegrationError):
    """Ozon API rate limit exception"""

    def __init__(self, message: str = "Ozon API rate limit exceeded"):
        super().__init__(message, "OZON_RATE_LIMIT_ERROR")


class OzonDataValidationError(OzonIntegrationError):
    """Ozon data validation exception"""

    def __init__(self, message: str = "Ozon data validation failed"):
        super().__init__(message, "OZON_DATA_VALIDATION_ERROR")


class OzonSyncError(OzonIntegrationError):
    """Ozon data sync exception"""

    def __init__(self, message: str = "Ozon data sync failed"):
        super().__init__(message, "OZON_SYNC_ERROR")
