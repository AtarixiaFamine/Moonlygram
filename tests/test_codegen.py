"""Guards that keep the generated types honest against the vendored spec.

These run offline against codegen/api.json. They fail loudly if (a) a generated
type drifts from the spec's field set, or (b) src/moonlygram/_types_generated.py
was hand-edited or left stale after a spec/override change — in either case the
fix is to edit codegen/overrides.py and re-run ``python codegen/gen_types.py``.

The hand-written rich blocks are checked against the spec too, since it began
modelling them in Bot API 10.3; there the fix is to edit rich/blocks.py.
"""
from __future__ import annotations

import dataclasses
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
CODEGEN = ROOT / "codegen"
sys.path.insert(0, str(CODEGEN))

import gen_types  # noqa: E402
import overrides as ov  # noqa: E402

import moonlygram.rich as rich  # noqa: E402
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
    cls = getattr(types, ov.RENAMED_IN_TYPES.get(name, name))
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


# The rich blocks are hand-written rather than generated (they are sent, so they
# carry a to_dict), but the vendored spec has modelled them since 10.3. That is
# enough to hold them to the same standard as the generated types. Scanning the
# package namespace also covers the three types the spec shares across both
# directions, which live in types.py and are re-exported here.
BLOCKS = {
    name: obj
    for name in dir(rich)
    if dataclasses.is_dataclass(obj := getattr(rich, name)) and name in SPEC["types"]
}


@pytest.mark.parametrize("name", sorted(BLOCKS))
def test_rich_block_matches_spec_fields(name: str) -> None:
    # A required `type` is the block's discriminator, which to_dict stamps
    # rather than storing. An optional one (a list item's label style) is a
    # real field the caller sets.
    modelled = {
        f["name"]
        for f in SPEC["types"][name].get("fields", [])
        if not (f["name"] == "type" and f.get("required"))
    }
    assert set(BLOCKS[name].__dataclass_fields__) == modelled, (
        f"{name} drifted from the Bot API spec"
    )


# The keyboard types are hand-written too, and for the same reason: they are
# sent, so they carry a to_dict. Nothing generated them, so a new spec field
# lands nowhere unless someone notices; that is how copy_text sat unmodelled
# from Bot API 7.11 to 10.3 while the generated types stayed current. Each name
# maps to the required discriminator to_dict stamps rather than stores.
KEYBOARDS = {
    "InlineKeyboardButton": (),
    "InlineKeyboardMarkup": (),
    "CopyTextButton": (),
    "KeyboardButton": (),
    "ReplyKeyboardMarkup": (),
    "ReplyKeyboardRemove": ("remove_keyboard",),
    "ForceReply": ("force_reply",),
}


@pytest.mark.parametrize("name", sorted(KEYBOARDS))
def test_keyboard_type_matches_spec_fields(name: str) -> None:
    stamped = set(KEYBOARDS[name])
    modelled = set(getattr(types, name).__dataclass_fields__) | stamped
    assert modelled == _spec_field_names(name), (
        f"{name} drifted from the Bot API spec; add the field to types.py"
    )
