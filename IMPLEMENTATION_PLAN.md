# Google Workspace MCP - Security & Enhancement Implementation Plan

**Created**: 2026-01-26
**Repo**: ~/code/google-workspace-mcp (forked from taylorwilsdon/google_workspace_mcp)
**Purpose**: Fix security issues and enhance the MCP server
**Execution Mode**: `claude --dangerously-skip-permissions`

---

## Phase 1: Critical Security Fixes (Priority: IMMEDIATE)

### 1.1 Secure Credential File Permissions

**File**: `auth/credential_store.py`

**Problem**: Credential files are created without restrictive permissions. Anyone with filesystem access can read OAuth tokens.

**Implementation**:
1. Find the `save_credentials` method (around line 175-185)
2. After writing the JSON file, add `os.chmod(creds_path, 0o600)`
3. Add `import os` at top if not present
4. Also fix any other file write operations in this file

**Code Change**:
```python
# After: json.dump(creds_data, f, indent=2)
# Add:
os.chmod(creds_path, 0o600)
```

**Verification**:
```bash
ls -la ~/.google-workspace-mcp/credentials/
# Should show -rw------- (600) permissions
```

---

### 1.2 Add Token Expiry Check Before Refresh

**File**: `auth/google_auth.py`

**Problem**: Tokens are refreshed on every call even if still valid, causing unnecessary API calls.

**Implementation**:
1. Find `get_credentials()` function (around line 690-750)
2. Before attempting refresh, check if token expires within next 5 minutes
3. Add helper function `_is_token_expiring_soon(credentials, buffer_seconds=300)`

**Code Change**:
```python
def _is_token_expiring_soon(credentials, buffer_seconds=300):
    """Check if token expires within buffer_seconds."""
    if not credentials.expiry:
        return True  # No expiry info, assume needs refresh
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    expiry = credentials.expiry.replace(tzinfo=timezone.utc) if credentials.expiry.tzinfo is None else credentials.expiry
    return (expiry - now).total_seconds() < buffer_seconds

# In get_credentials(), change:
# FROM: if credentials.valid:
# TO:   if credentials.valid and not _is_token_expiring_soon(credentials):
```

---

### 1.3 Redact Tokens from Log Messages

**Files**:
- `auth/google_auth.py`
- `auth/service_decorator.py`

**Problem**: Refresh tokens may appear in error messages and logs.

**Implementation**:
1. Create a utility function `redact_sensitive_data(obj)` in `core/utils.py`
2. Use it before logging any credentials-related objects
3. Search for all `logger.warning`, `logger.error`, `logger.debug` calls that might contain tokens

**Code Change** (add to `core/utils.py`):
```python
def redact_sensitive_data(data):
    """Redact sensitive fields from data before logging."""
    if isinstance(data, dict):
        sensitive_keys = {'refresh_token', 'access_token', 'client_secret', 'token'}
        return {
            k: '***REDACTED***' if k in sensitive_keys else redact_sensitive_data(v)
            for k, v in data.items()
        }
    elif isinstance(data, str):
        # Redact anything that looks like a token (long base64-ish strings)
        import re
        return re.sub(r'(ya29\.[A-Za-z0-9_-]{50,})', '***ACCESS_TOKEN_REDACTED***', data)
    return data
```

**Files to update**:
- `auth/google_auth.py`: Lines ~693, ~751 (credential logging)
- `auth/service_decorator.py`: Lines ~633 (RefreshError handling)

---

## Phase 2: Robustness Improvements (Priority: HIGH)

### 2.1 Add Rate Limit (429) Retry Handling

**File**: `core/utils.py`

**Problem**: Rate limit errors fail immediately instead of retrying with backoff.

**Implementation**:
1. Find `@handle_http_errors` decorator (around line 244-341)
2. Add 429 to the list of retryable status codes
3. Use `Retry-After` header if present, else exponential backoff

**Code Change**:
```python
# In the retry logic, add:
if error.resp.status == 429:
    retry_after = error.resp.headers.get('Retry-After', None)
    if retry_after:
        wait_time = int(retry_after)
    else:
        wait_time = (2 ** attempt) + random.uniform(0, 1)
    logger.warning(f"Rate limited (429). Waiting {wait_time}s before retry {attempt + 1}")
    await asyncio.sleep(wait_time)
    continue
```

---

### 2.2 Add API Call Timeouts

**File**: `auth/google_auth.py`

**Problem**: Google API calls can hang indefinitely with no timeout.

**Implementation**:
1. Find `get_authenticated_google_service()` (around line 770-790)
2. Wrap the `build()` call and subsequent API operations with timeout
3. Add configurable timeout via environment variable `GOOGLE_API_TIMEOUT` (default: 60)

**Code Change**:
```python
import asyncio

GOOGLE_API_TIMEOUT = int(os.environ.get('GOOGLE_API_TIMEOUT', '60'))

# Wrap API calls:
try:
    result = await asyncio.wait_for(
        asyncio.to_thread(api_call),
        timeout=GOOGLE_API_TIMEOUT
    )
except asyncio.TimeoutError:
    raise TransientNetworkError(f"Google API call timed out after {GOOGLE_API_TIMEOUT}s")
```

---

### 2.3 Prune Expired OAuth States

**File**: `auth/oauth21_session_store.py`

**Problem**: OAuth states are never cleaned up, causing memory leak.

**Implementation**:
1. Add `created_at` timestamp when storing OAuth state
2. Add `prune_expired_states()` method that removes states older than 10 minutes
3. Call prune on every `get_state()` or `store_state()` call

**Code Change**:
```python
from datetime import datetime, timedelta

STATE_EXPIRY_MINUTES = 10

def store_state(self, state: str, data: dict):
    data['_created_at'] = datetime.utcnow().isoformat()
    self._states[state] = data
    self._prune_expired_states()

def _prune_expired_states(self):
    """Remove states older than STATE_EXPIRY_MINUTES."""
    now = datetime.utcnow()
    expired = []
    for state, data in self._states.items():
        created = datetime.fromisoformat(data.get('_created_at', now.isoformat()))
        if (now - created) > timedelta(minutes=STATE_EXPIRY_MINUTES):
            expired.append(state)
    for state in expired:
        del self._states[state]
        logger.debug(f"Pruned expired OAuth state: {state[:8]}...")
```

---

## Phase 3: Code Quality Improvements (Priority: MEDIUM)

### 3.1 Consolidate Scope Definitions

**Files**:
- `auth/scopes.py`
- `auth/service_decorator.py`

**Problem**: SCOPE_GROUPS defined in two places, can get out of sync.

**Implementation**:
1. Keep canonical SCOPE_GROUPS in `auth/scopes.py`
2. Import and use in `service_decorator.py` instead of redefining
3. Remove duplicate definition from `service_decorator.py` (around lines 397-438)

**Code Change** in `service_decorator.py`:
```python
# Remove the local SCOPE_GROUPS definition
# Add import:
from auth.scopes import SCOPE_GROUPS
```

---

### 3.2 Consolidate OAuth Config Initialization

**Files**:
- `main.py`
- `fastmcp_server.py`

**Problem**: OAuth configuration initialization duplicated.

**Implementation**:
1. Create `auth/oauth_init.py` with shared initialization function
2. Call from both `main.py` and `fastmcp_server.py`

**Code Change** (new file `auth/oauth_init.py`):
```python
"""Shared OAuth initialization logic."""
import os
import logging
from auth.oauth_config import OAuthConfig

logger = logging.getLogger(__name__)

def initialize_oauth_config() -> OAuthConfig:
    """Initialize OAuth configuration from environment."""
    client_id = os.environ.get('GOOGLE_OAUTH_CLIENT_ID')
    client_secret = os.environ.get('GOOGLE_OAUTH_CLIENT_SECRET')

    if not client_id or not client_secret:
        raise ValueError("GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET required")

    config = OAuthConfig(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=os.environ.get('GOOGLE_OAUTH_REDIRECT_URI'),
    )

    logger.info("OAuth configuration initialized")
    return config
```

---

### 3.3 Add Comprehensive Error Codes

**File**: `core/errors.py` (new file)

**Problem**: Error messages are strings without codes, hard to programmatically handle.

**Implementation**:
1. Create `core/errors.py` with error code enum
2. Update exception classes to include error codes
3. Use in error messages throughout

**Code Change** (new file):
```python
"""Error codes for Google Workspace MCP."""
from enum import Enum

class ErrorCode(Enum):
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
    """Base exception with error code."""
    def __init__(self, message: str, code: ErrorCode, details: dict = None):
        self.code = code
        self.details = details or {}
        super().__init__(f"[{code.name}] {message}")
```

---

## Phase 4: Feature Enhancements (Priority: LOW)

### 4.1 Add Gmail Batch Delete

**File**: `gmail/gmail_tools.py`

**Implementation**:
1. Add `batch_delete_messages` tool
2. Use Gmail API batch endpoint
3. Respect existing GMAIL_BATCH_SIZE (25)

**Code Change**:
```python
@mcp.tool()
@require_google_service("gmail", "gmail_modify")
async def batch_delete_messages(
    message_ids: list[str],
    permanent: bool = False
) -> dict:
    """Delete multiple Gmail messages in batch.

    Args:
        message_ids: List of message IDs to delete (max 100)
        permanent: If True, permanently delete. If False, move to trash.

    Returns:
        Dict with success count and any failures
    """
    if len(message_ids) > 100:
        raise UserInputError("Maximum 100 messages per batch")

    service = await get_gmail_service()

    if permanent:
        # Use batchDelete
        body = {'ids': message_ids}
        service.users().messages().batchDelete(userId='me', body=body).execute()
    else:
        # Use batchModify to add TRASH label
        body = {
            'ids': message_ids,
            'addLabelIds': ['TRASH']
        }
        service.users().messages().batchModify(userId='me', body=body).execute()

    return {"deleted": len(message_ids), "permanent": permanent}
```

---

### 4.2 Add Sheets Batch Update

**File**: `gsheets/sheets_tools.py`

**Implementation**:
1. Add `batch_update_cells` tool
2. Accept list of {range, values} objects
3. Use spreadsheets.values.batchUpdate

**Code Change**:
```python
@mcp.tool()
@require_google_service("sheets", "sheets_write")
async def batch_update_cells(
    spreadsheet_id: str,
    updates: list[dict]
) -> dict:
    """Update multiple ranges in a spreadsheet in one API call.

    Args:
        spreadsheet_id: The spreadsheet ID
        updates: List of {range: "Sheet1!A1:B2", values: [[...]]} objects

    Returns:
        Dict with updated cell counts
    """
    service = await get_sheets_service()

    body = {
        'valueInputOption': 'USER_ENTERED',
        'data': [
            {'range': u['range'], 'values': u['values']}
            for u in updates
        ]
    }

    result = service.spreadsheets().values().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body=body
    ).execute()

    return {
        "updatedCells": result.get('totalUpdatedCells', 0),
        "updatedRanges": len(updates)
    }
```

---

## Phase 5: Testing (Priority: MEDIUM)

### 5.1 Add Unit Tests for Auth Flow

**File**: `tests/test_auth.py` (new)

**Implementation**:
1. Create `tests/` directory
2. Add pytest as dev dependency
3. Write tests for:
   - `_is_token_expiring_soon()`
   - `redact_sensitive_data()`
   - OAuth state pruning
   - Credential file permissions

**Test File Structure**:
```python
"""Tests for authentication module."""
import pytest
from datetime import datetime, timezone, timedelta
from auth.google_auth import _is_token_expiring_soon
from core.utils import redact_sensitive_data

class TestTokenExpiry:
    def test_expired_token(self):
        # Mock credentials with past expiry
        ...

    def test_valid_token(self):
        # Mock credentials with future expiry
        ...

    def test_expiring_soon(self):
        # Mock credentials expiring in 2 minutes
        ...

class TestRedaction:
    def test_redacts_refresh_token(self):
        data = {"refresh_token": "secret123", "email": "test@test.com"}
        result = redact_sensitive_data(data)
        assert result["refresh_token"] == "***REDACTED***"
        assert result["email"] == "test@test.com"
```

---

## Execution Checklist

Run in order. Check off as completed:

```
Phase 1: Critical Security
[ ] 1.1 Credential file permissions (auth/credential_store.py)
[ ] 1.2 Token expiry check (auth/google_auth.py)
[ ] 1.3 Redact tokens from logs (core/utils.py, auth/*.py)

Phase 2: Robustness
[ ] 2.1 Rate limit retry (core/utils.py)
[ ] 2.2 API timeouts (auth/google_auth.py)
[ ] 2.3 OAuth state pruning (auth/oauth21_session_store.py)

Phase 3: Code Quality
[ ] 3.1 Consolidate scope definitions
[ ] 3.2 Consolidate OAuth init
[ ] 3.3 Add error codes (core/errors.py)

Phase 4: Features
[ ] 4.1 Gmail batch delete
[ ] 4.2 Sheets batch update

Phase 5: Testing
[ ] 5.1 Add unit tests
```

---

## Verification Commands

After implementation, run:

```bash
# Check credential permissions
ls -la ~/.google-workspace-mcp/credentials/

# Run the MCP server
cd ~/code/google-workspace-mcp
uv run main.py --tools gmail drive

# Test a simple operation
# (In Claude Code, try listing emails)

# Run tests (after Phase 5)
cd ~/code/google-workspace-mcp
uv run pytest tests/ -v
```

---

## Git Workflow

After each phase:

```bash
cd ~/code/google-workspace-mcp
git add -A
git commit -m "Phase X: <description>

- Item 1
- Item 2

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
git push origin main
```

---

## Notes

- All file paths are relative to `~/code/google-workspace-mcp/`
- Use `uv` for running Python (already configured)
- Existing OAuth credentials in `~/.config/gcp/` - do not modify
- MCP is already registered at user level via `claude mcp add-json`
- After changes, restart Claude Code to reload MCP server
