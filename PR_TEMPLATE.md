# Pull Request Template

**⚠️ DO NOT SUBMIT YET - FOR PREPARATION ONLY**

Use this template when creating the PR to taylorwilsdon/google_workspace_mcp on 2026-01-31.

---

## Title

```
Add security enhancements and batch operations
```

## Description

### Summary

This PR contributes security fixes, robustness improvements, and batch operations to the excellent Google Workspace MCP server created by @taylorwilsdon.

All changes are **backward compatible** and **non-breaking** - existing functionality remains unchanged while adding new features.

### What This PR Adds

#### 1. Security Enhancements (Phase 1)
- **Credential file permissions**: Files created with 600, directories with 700
- **Token expiry checks**: 5-minute buffer before refresh to reduce API calls
- **Log redaction**: Sensitive tokens sanitized from log output

#### 2. Robustness Improvements (Phase 2)
- **Rate limit handling**: Automatic retry with exponential backoff for 429 errors
- **API timeouts**: Configurable timeout (default 60s) to prevent hanging operations
- **OAuth state pruning**: Already implemented (verified existing cleanup)

#### 3. Batch Operations (Phase 4)
New batch operations for all major services:
- **Gmail**: `batch_delete_messages` (up to 100 messages)
- **Sheets**: `batch_update_cells` (multiple ranges in one call)
- **Docs**: `batch_read_docs` (up to 20 documents)
- **Calendar**: `batch_create_events` and `batch_delete_events` (up to 50 events)
- **Forms**: `batch_get_form_responses` (up to 10 forms)

**Performance Impact**: 10-50x improvement (1 API call vs 50 individual calls)

#### 4. Code Quality (Phase 3)
- Consolidated scope definitions in `auth/scopes.py`
- Shared OAuth initialization module
- Comprehensive error codes with `MCPError` base class

#### 5. Testing (Phase 5)
- 18 unit tests covering authentication flows
- Tests for token expiry, redaction, and file permissions
- All tests passing

### Documentation

- **IMPLEMENTATION_PLAN.md**: Detailed implementation plan (5 phases)
- **BATCH_OPERATIONS.md**: Comprehensive guide with examples and best practices
- **TESTING_PLAN.md**: 5-day testing checklist (completed)
- **tests/test_auth.py**: Unit tests for new features

### Testing

All features tested over 5 days (2026-01-26 to 2026-01-30):
- ✅ Security features validated (permissions, redaction, token management)
- ✅ Robustness features tested (rate limiting, timeouts)
- ✅ Batch operations verified across all services
- ✅ Performance improvements confirmed (fewer API calls)
- ✅ No regressions in existing functionality

See TESTING_PLAN.md for detailed test results.

### Backward Compatibility

- ✅ All existing tools work unchanged
- ✅ No breaking changes to APIs or configurations
- ✅ New features are additive only
- ✅ Existing OAuth flows preserved
- ✅ Compatible with both OAuth and service account auth

### Files Changed

**New Files**:
- `auth/oauth_init.py` - Shared OAuth initialization
- `core/errors.py` - Error codes and base exception class
- `tests/test_auth.py` - Unit tests
- `BATCH_OPERATIONS.md` - Batch operations documentation
- `IMPLEMENTATION_PLAN.md` - Implementation details
- `TESTING_PLAN.md` - Testing checklist

**Modified Files**:
- `auth/credential_store.py` - File permissions
- `auth/google_auth.py` - Token expiry checks, timeouts
- `auth/scopes.py` - Consolidated scope definitions
- `auth/service_decorator.py` - Removed duplicate scope definitions
- `core/utils.py` - Rate limiting, redaction utility
- `gmail/gmail_tools.py` - Batch delete operation
- `gsheets/sheets_tools.py` - Batch update operation
- `gdocs/docs_tools.py` - Batch read operation
- `gcalendar/calendar_tools.py` - Batch create/delete operations
- `gforms/forms_tools.py` - Batch response retrieval

### Why These Changes?

1. **Security**: Credential files should not be world-readable; tokens should not appear in logs
2. **Performance**: Batch operations reduce API calls by 10-50x for common workflows
3. **Reliability**: Rate limiting and timeouts make the server more robust in production
4. **Quality**: Tests and error codes improve maintainability

### Acknowledgments

This PR builds upon the excellent foundation created by @taylorwilsdon. The original architecture made these enhancements straightforward to implement while maintaining the clean design patterns established in the codebase.

Special thanks for:
- The well-structured service decorator pattern
- Clean separation of concerns across modules
- Comprehensive existing tool implementations
- Clear documentation and examples

### License

All contributions in this PR are made under the same MIT license as the original project.

### Checklist

Before submitting:
- [x] All tests passing
- [x] Documentation complete
- [x] Changes are backward compatible
- [x] No breaking changes
- [x] Tested thoroughly (5-day testing period)
- [x] Follows existing code style and patterns
- [x] Commit messages follow conventions
- [x] Original author's work acknowledged

### Questions for Maintainer

1. Would you prefer the batch operations in separate files (e.g., `gmail/batch_tools.py`) or integrated as shown?
2. Any concerns about the new dependencies or imports?
3. Should the error codes in `core/errors.py` follow a different pattern?
4. Are there any additional tests you'd like to see?

### How to Review

1. **Security**: Check `auth/credential_store.py` (lines 121-122, 185) and `core/utils.py` (new `redact_sensitive_data` function)
2. **Batch Operations**: Try any of the new tools (e.g., `batch_delete_messages`, `batch_update_cells`)
3. **Tests**: Run `uv run pytest tests/test_auth.py -v` (18 tests should pass)
4. **Documentation**: Review `BATCH_OPERATIONS.md` for examples

### Future Enhancements (Not in This PR)

Ideas for follow-up PRs:
- Batch operations for Drive (copy, move, delete files)
- Batch operations for Tasks
- Enhanced error recovery for network issues
- Metrics/monitoring integration

---

## Community Impact

These changes benefit all users of the MCP server by:
- 🔒 Improving security posture
- ⚡ Dramatically improving performance for bulk operations
- 🛡️ Making the server more reliable in production
- 📚 Providing comprehensive documentation and examples

---

**Note to Reviewers**: This is a substantial PR but each phase is independent and can be reviewed separately. All changes maintain backward compatibility with the existing codebase.
