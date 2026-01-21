# Migration Notes (Ruby -> Python)

## Contract alignment

The Python client targets the same Message DB SQL functions as Ruby. Behavior
differences are treated as breaking changes unless explicitly documented.

## Naming and structure

- Ruby mixins and template methods map to explicit Python classes and protocols.
- Ruby `MessageData` structures become Python dataclasses.
- Logging is via Python's `logging` module rather than Eventide's log mixins.

## Expected version semantics

Ruby uses `:no_stream` to denote stream absence. Python accepts `-1` or the
string `"no_stream"` for the same behavior.

## Async usage

Ruby offers async utilities in the wider Eventide ecosystem. Python starts with
sync APIs; async adapters will be layered later.
