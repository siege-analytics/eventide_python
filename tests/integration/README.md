# Integration Tests

Integration tests expect a running Message DB instance.

## Quick setup

1. Start Postgres:

```bash
docker compose -f tests/integration/docker-compose.yml up -d
```

2. Install Message DB schema/functions into the database.
   You can do this by cloning the Message DB repo and running:

```bash
DATABASE_NAME=message_store message-db/database/install.sh
```

3. Run integration tests:

```bash
MESSAGE_DB_DSN=postgresql://message_store@localhost/message_store pytest -m integration
```
