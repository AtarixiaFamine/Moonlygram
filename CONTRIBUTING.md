# Contributing

Thanks for your interest in Moonlygram. This guide covers the local workflow and
the one piece that is unusual: the type generator.

## Setup

```bash
pip install -e ".[dev]"
```

Run the checks the way CI does:

```bash
ruff check src tests codegen
mypy
pytest -q
```

All three must pass. Tests are offline (no network, no real bot token).

## House style

- Docstrings and comments are **plain prose** — no Sphinx cross-references
  (`:class:`, `:meth:`), and no formal Args/Returns blocks beyond the few that
  already exist. Explain the *why* of a non-obvious choice in a short comment.
- Public API is re-exported through the package `__init__` files, each with an
  explicit `__all__`.
- The package ships `py.typed` and must stay `mypy --strict` clean.

## The type generator (important)

The data-only Bot API *received* types in `src/moonlygram/_types_generated.py`
are **generated** from a vendored copy of the Bot API spec. **Do not edit that
file by hand** — CI regenerates it and fails if it differs.

To change what is modelled:

1. Edit `codegen/overrides.py` (the allowlist, flat unions, and per-field
   overrides) — and, for a new API version, refresh the spec:
   ```bash
   python codegen/refresh.py
   ```
2. Regenerate:
   ```bash
   python codegen/gen_types.py
   ```
3. Run the suite. The drift guards in `tests/test_codegen.py` check that every
   generated type matches the spec and that the file is up to date.

Behavior-bearing types (those with shortcut methods or custom binding, such as
`Message`, `Chat`, `User`) and the *sent* types (keyboards, input media, inline
query results) stay hand-written in `src/moonlygram/types.py`.

## Docs

```bash
pip install -e ".[docs]"
mkdocs serve
```

The API reference is generated from docstrings by `mkdocstrings`, so keeping
docstrings accurate keeps the docs accurate.
