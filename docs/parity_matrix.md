# Parity Matrix

| Feature | Ruby Eventide | Python | Notes |
| --- | --- | --- | --- |
| Stream name grammar | Yes | Yes | `stream_name.py` mirrors separators and parsing. |
| Message data types | Yes | Yes | `WriteMessage` and `ReadMessage` dataclasses. |
| Write with expected version | Yes | Yes | `PostgresMessageDBClient.write`. |
| Stream read | Yes | Yes | `get_stream_messages` + iterator. |
| Category read | Yes | Yes | `get_category_messages` + iterator. |
| Last message | Yes | Yes | `get_last_stream_message`. |
| Consumer group partition | Yes | Yes | Exposed via category read params. |
| Correlation filter | Yes | Yes | Exposed via category read params. |
| Async client | Yes | No | Planned adapter. |
