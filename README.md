# eventide_python

Python client and tooling for the Eventide Message DB.

## Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
ruff check .
mypy src
pytest
```