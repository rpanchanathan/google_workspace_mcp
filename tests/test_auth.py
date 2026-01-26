"""Tests for authentication module."""
import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock, patch
from google.oauth2.credentials import Credentials

from auth.google_auth import _is_token_expiring_soon
from core.utils import redact_sensitive_data


class TestTokenExpiry:
    """Tests for token expiry checking."""

    def test_no_expiry_returns_true(self):
        """Token with no expiry should be considered expiring soon."""
        credentials = MagicMock(spec=Credentials)
        credentials.expiry = None
        assert _is_token_expiring_soon(credentials) is True

    def test_expired_token(self):
        """Token that already expired should be considered expiring soon."""
        credentials = MagicMock(spec=Credentials)
        # Set expiry to 1 hour ago
        credentials.expiry = datetime.now(timezone.utc) - timedelta(hours=1)
        assert _is_token_expiring_soon(credentials) is True

    def test_expiring_soon_token(self):
        """Token expiring within 5 minutes should be considered expiring soon."""
        credentials = MagicMock(spec=Credentials)
        # Set expiry to 2 minutes from now
        credentials.expiry = datetime.now(timezone.utc) + timedelta(minutes=2)
        assert _is_token_expiring_soon(credentials) is True

    def test_valid_token_not_expiring_soon(self):
        """Token expiring more than 5 minutes away should not be considered expiring soon."""
        credentials = MagicMock(spec=Credentials)
        # Set expiry to 10 minutes from now
        credentials.expiry = datetime.now(timezone.utc) + timedelta(minutes=10)
        assert _is_token_expiring_soon(credentials) is False

    def test_token_expiring_at_exact_buffer(self):
        """Token expiring exactly at buffer time should be considered expiring soon."""
        credentials = MagicMock(spec=Credentials)
        # Set expiry to exactly 5 minutes from now
        credentials.expiry = datetime.now(timezone.utc) + timedelta(seconds=300)
        # Should be True because we check if remaining time < buffer
        assert _is_token_expiring_soon(credentials) is True

    def test_custom_buffer_seconds(self):
        """Test with custom buffer time."""
        credentials = MagicMock(spec=Credentials)
        # Set expiry to 90 seconds from now
        credentials.expiry = datetime.now(timezone.utc) + timedelta(seconds=90)

        # With 60 second buffer, should not be expiring soon
        assert _is_token_expiring_soon(credentials, buffer_seconds=60) is False

        # With 120 second buffer, should be expiring soon
        assert _is_token_expiring_soon(credentials, buffer_seconds=120) is True

    def test_naive_datetime_expiry(self):
        """Test handling of naive datetime (no timezone info)."""
        credentials = MagicMock(spec=Credentials)
        # Set expiry as naive datetime (10 minutes from now, assumed UTC)
        credentials.expiry = datetime.utcnow() + timedelta(minutes=10)
        # Should handle naive datetime correctly
        assert _is_token_expiring_soon(credentials) is False


class TestRedaction:
    """Tests for sensitive data redaction."""

    def test_redacts_refresh_token(self):
        """Refresh token should be redacted."""
        data = {"refresh_token": "secret123", "email": "test@test.com"}
        result = redact_sensitive_data(data)
        assert result["refresh_token"] == "***REDACTED***"
        assert result["email"] == "test@test.com"

    def test_redacts_access_token(self):
        """Access token should be redacted."""
        data = {"access_token": "ya29.a0AfH6SMBxyz123", "user_id": "12345"}
        result = redact_sensitive_data(data)
        assert result["access_token"] == "***REDACTED***"
        assert result["user_id"] == "12345"

    def test_redacts_client_secret(self):
        """Client secret should be redacted."""
        data = {"client_secret": "GOCSPX-xyz123", "client_id": "12345"}
        result = redact_sensitive_data(data)
        assert result["client_secret"] == "***REDACTED***"
        assert result["client_id"] == "12345"

    def test_redacts_nested_tokens(self):
        """Tokens in nested structures should be redacted."""
        data = {
            "user": "test@test.com",
            "credentials": {
                "refresh_token": "secret123",
                "access_token": "ya29.access",
                "metadata": {"scope": "email"}
            }
        }
        result = redact_sensitive_data(data)
        assert result["credentials"]["refresh_token"] == "***REDACTED***"
        assert result["credentials"]["access_token"] == "***REDACTED***"
        assert result["credentials"]["metadata"]["scope"] == "email"
        assert result["user"] == "test@test.com"

    def test_redacts_google_access_token_in_string(self):
        """Google access tokens (ya29.*) in strings should be redacted."""
        # Use a realistic length token (50+ chars) to match the regex pattern
        text = "Using token ya29.a0AfH6SMBxyz123abc456def789ghi012jkl345mno678pqr901stu234vwx567yz890 for authentication"
        result = redact_sensitive_data(text)
        assert "ya29." not in result
        assert "***ACCESS_TOKEN_REDACTED***" in result
        assert "for authentication" in result

    def test_redacts_google_refresh_token_in_string(self):
        """Google refresh tokens (1//*) in strings should be redacted."""
        text = "Refresh token: 1//abc123def456ghi789jkl012mno345pqr678stu901vwx234yz"
        result = redact_sensitive_data(text)
        assert "1//" not in result
        assert "***REFRESH_TOKEN_REDACTED***" in result
        assert "Refresh token:" in result

    def test_non_dict_non_string_unchanged(self):
        """Non-dict, non-string data should be returned unchanged."""
        assert redact_sensitive_data(123) == 123
        assert redact_sensitive_data(None) is None
        assert redact_sensitive_data([1, 2, 3]) == [1, 2, 3]

    def test_empty_dict(self):
        """Empty dict should return empty dict."""
        assert redact_sensitive_data({}) == {}

    def test_all_sensitive_keys_redacted(self):
        """All sensitive keys should be redacted."""
        data = {
            "refresh_token": "rt1",
            "access_token": "at1",
            "client_secret": "cs1",
            "token": "t1",
            "id_token": "it1",
            "safe_field": "safe_value"
        }
        result = redact_sensitive_data(data)
        assert result["refresh_token"] == "***REDACTED***"
        assert result["access_token"] == "***REDACTED***"
        assert result["client_secret"] == "***REDACTED***"
        assert result["token"] == "***REDACTED***"
        assert result["id_token"] == "***REDACTED***"
        assert result["safe_field"] == "safe_value"


class TestCredentialFilePermissions:
    """Tests for credential file permissions."""

    @patch('os.chmod')
    @patch('builtins.open', create=True)
    @patch('json.dump')
    def test_credential_file_has_restrictive_permissions(self, mock_dump, mock_open, mock_chmod):
        """Credential files should be created with 600 permissions."""
        from auth.credential_store import LocalDirectoryCredentialStore

        # Create mock credentials
        credentials = MagicMock(spec=Credentials)
        credentials.token = "test_token"
        credentials.refresh_token = "test_refresh"
        credentials.token_uri = "https://oauth2.googleapis.com/token"
        credentials.client_id = "test_client_id"
        credentials.client_secret = "test_client_secret"
        credentials.scopes = ["email", "profile"]
        credentials.expiry = None

        # Create store and save credentials
        store = LocalDirectoryCredentialStore("/tmp/test_creds")
        with patch('os.path.exists', return_value=True):
            store.store_credential("test@test.com", credentials)

        # Verify chmod was called with 0o600
        mock_chmod.assert_called_once()
        args, kwargs = mock_chmod.call_args
        assert args[1] == 0o600  # Verify the permission mode

    @patch('os.makedirs')
    def test_credential_directory_created_with_restrictive_permissions(self, mock_makedirs):
        """Credential directory should be created with 700 permissions."""
        from auth.credential_store import LocalDirectoryCredentialStore

        with patch('os.path.exists', return_value=False):
            store = LocalDirectoryCredentialStore("/tmp/test_creds")
            # Trigger directory creation by getting credential path
            store._get_credential_path("test@test.com")

        # Verify makedirs was called with mode 0o700
        mock_makedirs.assert_called_once()
        args, kwargs = mock_makedirs.call_args
        assert kwargs.get('mode') == 0o700
