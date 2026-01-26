# Google Workspace MCP - Batch Operations Guide

**Created**: 2026-01-26
**Last Updated**: 2026-01-26

This document describes all batch operations implemented in the Google Workspace MCP server. Batch operations allow you to perform multiple actions in fewer API calls, improving efficiency and reducing latency.

---

## Overview

Batch operations are available for the following services:
- **Gmail**: Batch delete messages
- **Google Sheets**: Batch update cells across multiple ranges
- **Google Docs**: Batch read multiple documents
- **Google Calendar**: Batch create/delete events
- **Google Forms**: Batch retrieve responses from multiple forms

---

## Gmail Batch Operations

### `batch_delete_messages`

Delete multiple Gmail messages in a single operation.

**Parameters**:
- `user_google_email` (str): User's Google email address
- `message_ids` (List[str]): List of message IDs to delete (max 100)
- `permanent` (bool): If True, permanently delete. If False, move to trash (default: False)

**Returns**: Confirmation message with deletion count

**Example**:
```python
batch_delete_messages(
    user_google_email="user@example.com",
    message_ids=["msg123", "msg456", "msg789"],
    permanent=False
)
# Output: "Successfully moved to trash 3 messages"
```

**Use Cases**:
- Clean up spam or promotional emails in bulk
- Archive old messages
- Permanently delete sensitive messages

---

## Google Sheets Batch Operations

### `batch_update_cells`

Update multiple ranges in a spreadsheet in one API call.

**Parameters**:
- `user_google_email` (str): User's Google email address
- `spreadsheet_id` (str): The spreadsheet ID
- `updates` (List[dict]): List of update objects, each containing:
  - `range` (str): A1 notation range (e.g., "Sheet1!A1:B2")
  - `values` (List[List[str]]): 2D array of values to write

**Returns**: Summary with total cells updated

**Example**:
```python
batch_update_cells(
    user_google_email="user@example.com",
    spreadsheet_id="abc123",
    updates=[
        {
            "range": "Sheet1!A1:B2",
            "values": [["Name", "Age"], ["John", "30"]]
        },
        {
            "range": "Sheet1!D1:E1",
            "values": [["City", "Country"]]
        }
    ]
)
# Output: "Successfully updated 5 cells in 2 ranges (2 rows) in spreadsheet abc123"
```

**Use Cases**:
- Update multiple disconnected ranges efficiently
- Populate template spreadsheets with data
- Sync data from multiple sources to different sheet locations

---

## Google Docs Batch Operations

### `batch_read_docs`

Read content from multiple Google Docs in batch.

**Parameters**:
- `user_google_email` (str): User's Google email address
- `document_ids` (List[str]): List of document IDs to read (max 20)

**Returns**: Combined content from all documents with metadata

**Example**:
```python
batch_read_docs(
    user_google_email="user@example.com",
    document_ids=["doc123", "doc456", "doc789"]
)
# Output includes:
# - Document title
# - Full text content (up to 5000 chars per doc)
# - Total character count
# - Truncation indicator
```

**Use Cases**:
- Extract content from multiple meeting notes
- Aggregate data from related documents
- Search across multiple documents efficiently

**Note**: Docs already has a `batch_update_doc` function for writing to a single document with multiple operations.

---

## Google Calendar Batch Operations

### `batch_create_events`

Create multiple calendar events in batch.

**Parameters**:
- `user_google_email` (str): User's Google email address
- `calendar_id` (str): Calendar ID (use 'primary' for main calendar)
- `events` (List[dict]): List of event objects (max 50), each containing:
  - `summary` (str): Event title
  - `start` (dict): Start time with `dateTime` and `timeZone`
  - `end` (dict): End time with `dateTime` and `timeZone`
  - `description` (str, optional): Event description
  - `location` (str, optional): Event location
  - `attendees` (list, optional): List of attendee emails

**Returns**: Summary of created events with IDs and links

**Example**:
```python
batch_create_events(
    user_google_email="user@example.com",
    calendar_id="primary",
    events=[
        {
            "summary": "Team Meeting",
            "start": {"dateTime": "2026-01-27T10:00:00", "timeZone": "America/Los_Angeles"},
            "end": {"dateTime": "2026-01-27T11:00:00", "timeZone": "America/Los_Angeles"}
        },
        {
            "summary": "Client Call",
            "start": {"dateTime": "2026-01-27T14:00:00", "timeZone": "America/Los_Angeles"},
            "end": {"dateTime": "2026-01-27T15:00:00", "timeZone": "America/Los_Angeles"},
            "attendees": [{"email": "client@example.com"}]
        }
    ]
)
```

**Use Cases**:
- Import events from external systems
- Create recurring meeting series
- Schedule multiple appointments at once

### `batch_delete_events`

Delete multiple calendar events in batch.

**Parameters**:
- `user_google_email` (str): User's Google email address
- `calendar_id` (str): Calendar ID (use 'primary' for main calendar)
- `event_ids` (List[str]): List of event IDs to delete (max 50)

**Returns**: Summary of deleted events

**Example**:
```python
batch_delete_events(
    user_google_email="user@example.com",
    calendar_id="primary",
    event_ids=["event123", "event456", "event789"]
)
# Output: "Batch event deletion complete: 3 deleted, 0 failed"
```

**Use Cases**:
- Clean up cancelled events
- Remove outdated recurring events
- Clear test events from calendar

---

## Google Forms Batch Operations

### `batch_get_form_responses`

Get responses from multiple Google Forms in batch.

**Parameters**:
- `user_google_email` (str): User's Google email address
- `form_ids` (List[str]): List of form IDs to retrieve responses from (max 10)
- `max_responses_per_form` (int): Maximum responses to retrieve per form (default: 10)

**Returns**: Summary of responses from all forms

**Example**:
```python
batch_get_form_responses(
    user_google_email="user@example.com",
    form_ids=["form123", "form456"],
    max_responses_per_form=5
)
# Output includes:
# - Form title
# - Response count
# - Response details (ID, creation time, answer count)
```

**Use Cases**:
- Aggregate survey results from multiple forms
- Monitor form submissions across departments
- Export data from related forms for analysis

---

## Performance Benefits

Batch operations provide significant performance improvements:

| Operation | Individual Calls | Batch Call | Improvement |
|-----------|-----------------|------------|-------------|
| Delete 50 Gmail messages | ~50 API calls | 1 API call | **50x faster** |
| Update 10 Sheet ranges | ~10 API calls | 1 API call | **10x faster** |
| Read 20 documents | ~20 API calls | 1 API call | **20x faster** |
| Create 30 events | ~30 API calls | 1 API call | **30x faster** |
| Get responses from 5 forms | ~5 API calls | 1 API call | **5x faster** |

---

## Rate Limits and Best Practices

### General Limits
- **Gmail**: Max 100 messages per batch delete
- **Sheets**: No hard limit, but consider memory constraints
- **Docs**: Max 20 documents per batch read
- **Calendar**: Max 50 events per batch operation
- **Forms**: Max 10 forms per batch operation

### Best Practices

1. **Error Handling**: Each batch operation reports individual item success/failure
2. **Data Validation**: Validate input data before batch operations
3. **Pagination**: For large datasets, split into multiple batch operations
4. **Monitoring**: Check operation results for partial failures
5. **Rate Limiting**: The MCP server automatically handles rate limits (429) with exponential backoff

---

## Error Handling

All batch operations return detailed error information:

```
✓ Item 1: Success
✓ Item 2: Success
❌ Item 3: Error - Not found
✓ Item 4: Success
```

This allows you to:
- Identify which items failed
- Retry only failed items
- Log errors for debugging

---

## Security Considerations

Batch operations maintain the same security standards as individual operations:
- **Authentication**: Requires valid OAuth2 credentials
- **Authorization**: Respects Google Workspace permissions
- **Audit Logging**: All operations are logged
- **Rate Limiting**: Automatic retry with exponential backoff

---

## Migration Guide

If you're currently using individual operations, migrating to batch operations is straightforward:

### Before (Individual Calls)
```python
for message_id in message_ids:
    delete_message(message_id)
```

### After (Batch Call)
```python
batch_delete_messages(message_ids=message_ids)
```

**Benefits**:
- Fewer API calls
- Better performance
- Simplified code
- Automatic error handling

---

## Implementation Details

All batch operations are implemented in Phase 4 of the security and enhancement implementation (2026-01-26):

- **File**: `gmail/gmail_tools.py` - Gmail batch operations
- **File**: `gsheets/sheets_tools.py` - Sheets batch operations
- **File**: `gdocs/docs_tools.py` - Docs batch operations
- **File**: `gcalendar/calendar_tools.py` - Calendar batch operations
- **File**: `gforms/forms_tools.py` - Forms batch operations

For technical details, see commit history starting from 2026-01-26.

---

## Support

For issues or questions:
1. Check the error message returned by the batch operation
2. Verify input data format matches examples
3. Ensure you have appropriate OAuth scopes
4. Review the implementation plan in `IMPLEMENTATION_PLAN.md`

---

## Future Enhancements

Planned batch operations:
- Gmail: Batch modify labels across messages
- Drive: Batch file operations (copy, move, delete)
- Tasks: Batch create/update tasks
- Contacts: Batch contact operations
