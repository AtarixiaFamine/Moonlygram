"""Guards that keep the generated types honest against the vendored spec.

These run offline against codegen/api.json. They fail loudly if (a) a generated
type drifts from the spec's field set, or (b) src/moonlygram/_types_generated.py
was hand-edited or left stale after a spec/override change — in either case the
fix is to edit codegen/overrides.py and re-run ``python codegen/gen_types.py``.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
CODEGEN = ROOT / "codegen"
sys.path.insert(0, str(CODEGEN))

import gen_types  # noqa: E402
import overrides as ov  # noqa: E402

import moonlygram.types as types  # noqa: E402

SPEC = json.loads((CODEGEN / "api.json").read_text(encoding="utf-8"))


def _spec_field_names(type_name: str) -> set[str]:
    entry = SPEC["types"][type_name]
    if type_name in ov.FLAT_UNIONS:
        fields = gen_types.merge_union_fields(entry, SPEC)
    else:
        fields = entry.get("fields", [])
    return {"from_user" if f["name"] == "from" else f["name"] for f in fields}


@pytest.mark.parametrize("name", sorted(ov.GENERATE | ov.FLAT_UNIONS))
def test_generated_type_matches_spec_fields(name: str) -> None:
    cls = getattr(types, name)
    modelled = set(cls.__dataclass_fields__) - {"raw"}
    assert modelled == _spec_field_names(name), (
        f"{name} fields drifted from the spec; re-run codegen/gen_types.py"
    )


def test_generated_file_is_up_to_date() -> None:
    on_disk = gen_types.OUT_PATH.read_text(encoding="utf-8")
    assert on_disk == gen_types.generate(), (
        "_types_generated.py is stale or hand-edited; "
        "run `python codegen/gen_types.py`"
    )
