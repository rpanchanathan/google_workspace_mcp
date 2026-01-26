"""Shared OAuth initialization logic."""
import os
import logging
from auth.oauth_config import OAuthConfig

logger = logging.getLogger(__name__)


def initialize_oauth_config() -> OAuthConfig:
    """Initialize OAuth configuration from environment.

    Returns:
        OAuthConfig instance

    Raises:
        ValueError: If required environment variables are missing
    """
    client_id = os.environ.get('GOOGLE_OAUTH_CLIENT_ID')
    client_secret = os.environ.get('GOOGLE_OAUTH_CLIENT_SECRET')

    if not client_id or not client_secret:
        raise ValueError(
            "GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET environment variables required"
        )

    config = OAuthConfig(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=os.environ.get('GOOGLE_OAUTH_REDIRECT_URI'),
    )

    logger.info("OAuth configuration initialized")
    return config
