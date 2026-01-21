# eventide_python

Python client and tooling for the Eventide Message DB.

## Install

```bash
pip install -e ".[dev,postgres]"
```

## Quickstart

```python
from eventide_python.message_db import PostgresMessageDBClient

client = PostgresMessageDBClient("postgresql://message_store@localhost/message_store")

client.write({"type": "Deposited", "data": {"amount": 100}}, "account-123")

messages = client.get_stream_messages("account-123")
```

## Docs

- `docs/message_db_contract.md`
- `docs/examples.md`
- `docs/parity_matrix.md`
- `docs/migration_notes.md`

## Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
ruff check .
mypy src
pytest
```