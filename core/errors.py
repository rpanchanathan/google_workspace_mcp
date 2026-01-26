"""Error codes for Google Workspace MCP."""
from enum import Enum


class ErrorCode(Enum):
    """Standardized error codes for Google Workspace MCP operations."""

    # Authentication errors (1xx)
    AUTH_MISSING_CREDENTIALS = 100
    AUTH_INVALID_TOKEN = 101
    AUTH_SCOPE_MISMATCH = 102
    AUTH_REFRESH_FAILED = 103
    AUTH_SESSION_INVALID = 104

    # API errors (2xx)
    API_RATE_LIMITED = 200
    API_TIMEOUT = 201
    API_NOT_FOUND = 202
    API_PERMISSION_DENIED = 203
    API_QUOTA_EXCEEDED = 204

    # Input errors (3xx)
    INPUT_INVALID_PARAMETER = 300
    INPUT_MISSING_REQUIRED = 301
    INPUT_FILE_NOT_FOUND = 302

    # Network errors (4xx)
    NETWORK_TRANSIENT = 400
    NETWORK_SSL_ERROR = 401


class MCPError(Exception):
    """Base exception with error code for MCP operations.

    Attributes:
        code: ErrorCode enum value
        message: Human-readable error message
        details: Additional error details (optional)
    """

    def __init__(self, message: str, code: ErrorCode, details: dict = None):
        """Initialize MCP error.

        Args:
            message: Human-readable error message
            code: ErrorCode enum value
            details: Additional error context (optional)
        """
        self.code = code
        self.details = details or {}
        super().__init__(f"[{code.name}] {message}")
