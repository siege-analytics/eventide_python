# Contributing

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Quality gates

```bash
ruff check .
mypy src
pytest
```

## Guidelines

- Keep APIs small and explicit.
- Prefer composition over inheritance.
- Match Message DB semantics before extending behavior.
