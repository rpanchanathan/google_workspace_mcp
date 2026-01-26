# Testing Log

Track your daily testing progress here.

---

## Day 1 - 2026-01-26 (Today)

### Tests Completed
- [ ] Check credential file permissions (600)
- [ ] Check credentials directory permissions (700)
- [ ] Verify token expiry check in logs
- [ ] Check logs for exposed tokens (should be redacted)
- [ ] Run unit tests (`uv run pytest tests/test_auth.py -v`)

### Issues Found
_None yet_

### Performance Observations
- API calls saved: _TBD_
- Response time improvements: _TBD_

### Notes
- Started testing period
-

---

## Day 2 - 2026-01-27

### Tests Completed
- [ ] Test rate limit handling (trigger 429 errors)
- [ ] Test API timeouts with slow operations
- [ ] Test Gmail batch delete (5 messages to trash)
- [ ] Test Sheets batch update (2-3 ranges)
- [ ] Use batch operations in real workflow

### Issues Found
_None yet_

### Performance Observations
-

### Notes
-

---

## Day 3 - 2026-01-28

### Tests Completed
- [ ] Test Gmail batch delete (50 messages)
- [ ] Test Sheets batch update with different data types
- [ ] Test Docs batch read (5 documents)
- [ ] Test Calendar batch create (10 events)

### Issues Found
_None yet_

### Performance Observations
-

### Notes
-

---

## Day 4 - 2026-01-29

### Tests Completed
- [ ] Test Gmail permanent deletion (10 messages)
- [ ] Test error handling (invalid message/doc IDs)
- [ ] Test Docs batch read (20 documents - max limit)
- [ ] Test Calendar batch delete (10 events)
- [ ] Test Forms batch responses (3-5 forms)

### Issues Found
_None yet_

### Performance Observations
-

### Notes
-

---

## Day 5 - 2026-01-30

### Tests Completed
- [ ] Final end-to-end workflow testing
- [ ] Re-run all unit tests
- [ ] Test with forms that have no responses
- [ ] Test with inaccessible resources (error handling)
- [ ] Performance benchmarking (before/after API call counts)
- [ ] Review all documentation for accuracy

### Issues Found
_None yet_

### Performance Observations
-

### Notes
-

---

## Pre-PR Review - 2026-01-31

### Final Checklist
- [ ] All critical tests passed
- [ ] All security features validated
- [ ] All batch operations tested successfully
- [ ] Documentation reviewed and accurate
- [ ] No breaking changes confirmed
- [ ] Performance improvements documented with metrics
- [ ] All unit tests passing
- [ ] Testing log complete

### Issues Summary
**Critical**: _None_
**High**: _None_
**Medium**: _None_
**Low**: _None_

### Metrics Summary
- Total API calls saved: _TBD_
- Average performance improvement: _TBD_
- Error rate: _TBD_

### Ready for PR?
- [ ] YES - Proceed with PR creation
- [ ] NO - Additional testing needed (document below)

### Additional Notes
-

---

## Quick Test Commands

### Check Credential Permissions
```bash
ls -la ~/.google-workspace-mcp/credentials/
stat ~/.google-workspace-mcp/credentials/  # Check directory
stat ~/.google-workspace-mcp/credentials/*.json  # Check files
```

### Check Logs for Token Leaks
```bash
grep -i "ya29\." ~/.google-workspace-mcp/logs/*.log
grep -i "refresh_token" ~/.google-workspace-mcp/logs/*.log
grep "***REDACTED***" ~/.google-workspace-mcp/logs/*.log
```

### Run Unit Tests
```bash
cd ~/code/google-workspace-mcp
uv run pytest tests/test_auth.py -v
```

### Test Batch Operations (Examples)
Use these in Claude Code sessions to test the batch operations in real scenarios.
