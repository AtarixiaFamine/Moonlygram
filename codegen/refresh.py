"""Re-pull the vendored Bot API spec and record its version.

Downloads the latest api.json from the telegram-bot-api-spec project to
codegen/api.json (the single source the generator reads). After refreshing,
run ``python codegen/gen_types.py`` and the test suite: the drift guards in
tests/test_codegen.py will flag any field that moved.

    python codegen/refresh.py
"""
from __future__ import annotations

import json
import urllib.request
from pathlib import Path

SPEC_URL = (
    "https://raw.githubusercontent.com/PaulSonOfLars/"
    "telegram-bot-api-spec/main/api.json"
)
SPEC_PATH = Path(__file__).resolve().parent / "api.json"


def main() -> None:
    with urllib.request.urlopen(SPEC_URL) as resp:  # noqa: S310 (trusted host)
        data = resp.read()
    spec = json.loads(data)
    SPEC_PATH.write_bytes(data)
    print(
        f"wrote {SPEC_PATH.name}: {spec.get('version', '?')} "
        f"({spec.get('release_date', '?')}), "
        f"{len(spec['types'])} types, {len(spec['methods'])} methods"
    )


if __name__ == "__main__":
    main()
