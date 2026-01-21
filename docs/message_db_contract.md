# Message DB Contract

This project targets the public Message DB server functions and their semantics.
The contract is versioned by the database function `message_store_version()` and
is currently `1.3.0` in the upstream SQL. The Python client will pin to the
Message DB public interface and treat all behavior changes as breaking unless
explicitly documented.

## Scope

We only depend on the public SQL functions defined under the `message_store`
schema. We do not access the `messages` table directly.

## Core functions

Write:
- `message_store.write_message(id, stream_name, type, data, metadata, expected_version)`
  - Performs advisory lock by stream category.
  - Enforces optimistic concurrency via `expected_version`.
  - Returns stream position for the message.

Read:
- `message_store.get_stream_messages(stream_name, position, batch_size, condition)`
  - Rejects category names (must be a stream).
  - `position` is stream position (default 0).
  - Optional SQL `condition` gated by `message_store.sql_condition` setting.
- `message_store.get_category_messages(category, position, batch_size, correlation, consumer_group_member, consumer_group_size, condition)`
  - Requires a category name.
  - `position` is global position (default 1).
  - Supports correlation stream filtering and consumer group partitioning.
  - Optional SQL `condition` gated by `message_store.sql_condition` setting.
- `message_store.get_last_stream_message(stream_name, type)`
  - Returns last message in stream (optionally filtered by type).

Utility:
- `message_store.stream_version(stream_name)`
- `message_store.acquire_lock(stream_name)`
- `message_store.id(stream_name)`
- `message_store.cardinal_id(stream_name)`
- `message_store.category(stream_name)`
- `message_store.is_category(stream_name)`
- `message_store.hash_64(value)`
- `message_store.message_store_version()`

## Error semantics

- `write_message` raises on wrong expected version.
- `get_stream_messages` raises if a category is provided.
- `get_category_messages` raises if a non-category is provided, or if consumer
  group parameters are inconsistent.
- SQL `condition` usage raises unless `message_store.sql_condition` is enabled.

## Python API boundary

Initial implementation is synchronous and blocking:

- `MessageDBClient.write(...)`
- `MessageDBClient.get_stream_messages(...)`
- `MessageDBClient.get_category_messages(...)`
- `MessageDBClient.get_last_stream_message(...)`

Async support will be layered later via a separate adapter using the same core
types and errors.
