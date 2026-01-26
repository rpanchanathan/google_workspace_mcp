# Testing Plan for Google Workspace MCP Enhancements

**Created**: 2026-01-26
**Testing Period**: 2026-01-26 to 2026-01-30 (5 days)
**PR Target Date**: 2026-01-31

---

## Testing Checklist

### Phase 1: Security Features (Priority: Critical)

#### 1.1 Credential File Permissions
- [ ] **Day 1**: Create new OAuth credentials and verify file permissions
  ```bash
  ls -la ~/.google-workspace-mcp/credentials/
  # Should show -rw------- (600) for credential files
  # Should show drwx------ (700) for credentials directory
  ```
- [ ] **Validation**: Run `stat` command to confirm octal permissions
- [ ] **Expected**: Files = 600, Directory = 700

#### 1.2 Token Expiry Check
- [ ] **Day 1-2**: Monitor token refresh behavior in logs
  ```bash
  # Look for log messages indicating token refresh decisions
  grep "expiring soon" ~/.google-workspace-mcp/logs/*.log
  ```
- [ ] **Validation**: Verify tokens are NOT refreshed when >5 minutes until expiry
- [ ] **Expected**: Fewer refresh API calls, better performance

#### 1.3 Log Redaction
- [ ] **Day 1**: Check logs for any exposed tokens
  ```bash
  grep -i "ya29\." ~/.google-workspace-mcp/logs/*.log
  grep -i "refresh_token" ~/.google-workspace-mcp/logs/*.log
  ```
- [ ] **Validation**: All sensitive values should show as ***REDACTED***
- [ ] **Expected**: No actual token values in log files

---

### Phase 2: Robustness Features (Priority: High)

#### 2.1 Rate Limit Handling (429)
- [ ] **Day 2-3**: Intentionally trigger rate limits with high-volume operations
  - Try rapid-fire Gmail message fetches
  - Monitor retry behavior in logs
- [ ] **Validation**: Check for "Rate limited (429)" log messages with backoff times
- [ ] **Expected**: Automatic retry with exponential backoff, eventual success

#### 2.2 API Timeouts
- [ ] **Day 2**: Test with slow network conditions
  ```bash
  # Set custom timeout (test with 10s for faster testing)
  export GOOGLE_API_TIMEOUT=10
  ```
- [ ] **Validation**: Operations timeout after configured seconds
- [ ] **Expected**: Clear timeout error messages, no hanging operations

---

### Phase 3: Batch Operations (Priority: High)

#### 3.1 Gmail Batch Delete
- [ ] **Day 3**: Test with small batch (5 messages to trash)
- [ ] **Day 3**: Test with larger batch (50 messages to trash)
- [ ] **Day 4**: Test permanent deletion (10 test messages)
- [ ] **Day 4**: Test error handling (include invalid message IDs)
- [ ] **Validation**:
  - Messages moved to trash/deleted as expected
  - Clear success/failure reporting per message
  - Performance: Single API call for entire batch

#### 3.2 Sheets Batch Update
- [ ] **Day 3**: Test updating 2-3 disconnected ranges
- [ ] **Day 3**: Test with different data types (numbers, text, formulas)
- [ ] **Day 4**: Test error handling (invalid range notation)
- [ ] **Validation**:
  - All ranges updated correctly
  - Total cell count matches expected
  - Single API call for all ranges

#### 3.3 Docs Batch Read
- [ ] **Day 4**: Test reading 5 documents
- [ ] **Day 4**: Test reading 20 documents (max limit)
- [ ] **Day 4**: Test with mix of accessible and inaccessible docs
- [ ] **Validation**:
  - Content extracted correctly from all docs
  - Truncation indicator for long docs
  - Individual error messages for failed docs

#### 3.4 Calendar Batch Operations
- [ ] **Day 4**: Create 10 test events in batch
- [ ] **Day 4**: Delete same events in batch
- [ ] **Day 5**: Test with invalid event data (missing required fields)
- [ ] **Validation**:
  - Events created with correct times/details
  - Event IDs and links returned
  - Clean deletion confirmation

#### 3.5 Forms Batch Responses
- [ ] **Day 5**: Test with 3-5 forms
- [ ] **Day 5**: Test with forms that have no responses
- [ ] **Day 5**: Test with forms you don't have access to
- [ ] **Validation**:
  - Response data retrieved correctly
  - Graceful handling of empty forms
  - Clear error messages for access issues

---

### Phase 4: Unit Tests (Priority: Medium)

- [ ] **Day 1**: Run initial test suite
  ```bash
  cd ~/code/google-workspace-mcp
  uv run pytest tests/test_auth.py -v
  ```
- [ ] **Day 5**: Re-run tests to ensure no regressions
- [ ] **Expected**: All 18 tests passing

---

### Phase 5: Integration Testing (Priority: Medium)

#### 5.1 Real-World Workflows
- [ ] **Day 2-5**: Use in actual Claude Code sessions
  - Gmail: Clean up old promotional emails
  - Sheets: Update multiple data ranges
  - Docs: Read meeting notes from multiple documents
  - Calendar: Schedule recurring meetings
  - Forms: Collect survey responses

#### 5.2 Performance Monitoring
- [ ] **Track metrics**:
  - API call count (should be lower with batch operations)
  - Response times (should be faster)
  - Error rates (should be same or lower)

---

## Daily Log Template

```markdown
## Testing Log - Day X (2026-01-XX)

### Tests Completed
- [ ] Test name
  - Result: Pass/Fail
  - Notes:

### Issues Found
1. Issue description
   - Severity: Critical/High/Medium/Low
   - Steps to reproduce:
   - Expected vs Actual:

### Performance Observations
- API calls saved:
- Response time improvements:
- Any bottlenecks:

### Next Steps
-
```

---

## Success Criteria

Before creating PR, ALL of the following must be true:

✅ **Security**
- [ ] No credential files have world-readable permissions
- [ ] No tokens visible in logs
- [ ] Token refresh only when needed (not on every call)

✅ **Robustness**
- [ ] Rate limit errors retry successfully
- [ ] Operations timeout appropriately
- [ ] No hanging/frozen operations

✅ **Batch Operations**
- [ ] All 5 services (Gmail, Sheets, Docs, Calendar, Forms) working
- [ ] Performance improvements validated (fewer API calls)
- [ ] Error handling works for partial failures

✅ **Quality**
- [ ] All unit tests passing
- [ ] No new bugs introduced
- [ ] Documentation accurate and complete

✅ **Compatibility**
- [ ] Existing tools still work (no breaking changes)
- [ ] Works with both OAuth and service account auth

---

## Issue Tracking

### Critical Issues (Must Fix Before PR)
_None yet_

### High Priority Issues (Should Fix Before PR)
_None yet_

### Medium Priority Issues (Can Fix in PR Review)
_None yet_

### Low Priority Issues (Future Enhancement)
_None yet_

---

## PR Readiness Checklist

Before creating PR on 2026-01-31:

- [ ] All critical tests passed
- [ ] All security features validated
- [ ] All batch operations tested successfully
- [ ] Documentation reviewed and accurate
- [ ] Commit history cleaned up (if needed)
- [ ] PR description prepared (see PR_TEMPLATE.md)
- [ ] Original maintainer's contribution acknowledged
- [ ] Changes non-breaking and backward compatible

---

## Notes

- Test in a safe environment (use test Google Workspace account if available)
- Keep detailed logs of any issues found
- Document performance improvements with metrics
- Take screenshots of successful operations for PR documentation
