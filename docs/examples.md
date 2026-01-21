# Examples

## Write and read a stream

```python
from eventide_python.message_db import PostgresMessageDBClient

client = PostgresMessageDBClient("postgresql://message_store@localhost/message_store")

client.write({"type": "Deposited", "data": {"amount": 100}}, "account-123")

for message in client.iter_stream_messages("account-123"):
    print(message.type, message.data)
```

## Category read with consumer group

```python
for message in client.iter_category_messages(
    "account",
    consumer_group_member=0,
    consumer_group_size=2,
):
    print(message.stream_name, message.global_position)
```
