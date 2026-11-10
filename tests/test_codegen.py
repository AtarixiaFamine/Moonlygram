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
from typing import Any

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


# Everything above covers one family at a time, which is how InputMediaVideo
# still ended up seven fields short: nothing listed it. A sent type is the one
# place a missing field is unreachable rather than merely unmodelled, because
# it has no raw dict to fall back on and slots=True leaves nowhere to put the
# value. So rather than a list to keep current, find them: any dataclass the
# spec names, carrying a to_dict and no raw, that the generator does not own.
# A new hand-written sent type is covered the day it lands.
STAMPED = {
    # required spec fields that to_dict writes rather than stores
    "ForceReply": {"force_reply"},
    "ReplyKeyboardRemove": {"remove_keyboard"},
}


def _sent_types() -> dict[str, type]:
    found: dict[str, type] = {}
    for module in (types, rich):
        for attr in dir(module):
            obj = getattr(module, attr)
            if not dataclasses.is_dataclass(obj) or attr not in SPEC["types"]:
                continue
            if attr in ov.GENERATE | ov.FLAT_UNIONS:
                continue  # the generator owns it, checked above
            if not hasattr(obj, "to_dict") or "raw" in obj.__dataclass_fields__:
                continue  # received: unmodelled fields stay reachable via raw
            found.setdefault(attr, obj)
    return found


SENT_TYPES = _sent_types()


def test_the_sent_type_scan_finds_something() -> None:
    # guards the guard: a filter that silently matches nothing would pass
    assert "InputMediaVideo" in SENT_TYPES and len(SENT_TYPES) > 20


# Modelling a field is only half of it: to_dict has to write it out too. Both
# halves failed together on InputMediaVideo, and the field check alone would
# pass on a dataclass whose to_dict quietly ignored it. Setting every field and
# reading the payload back covers the other half. Nested objects need a real
# value rather than a placeholder string.
NESTED = {
    "mask_position": types.MaskPosition(point="forehead", x_shift=0.0, y_shift=0.0, scale=1.0),
    "price": types.SuggestedPostPrice(currency="XTR", amount=1),
}


def _placeholder(field: dataclasses.Field[Any]) -> Any:
    if field.name in NESTED:
        return NESTED[field.name]
    annotation = str(field.type)
    if "bool" in annotation:
        return True
    if "list" in annotation:
        return []
    if "int" in annotation and "str" not in annotation:
        return 7
    return "x"


@pytest.mark.parametrize("name", sorted(SENT_TYPES))
def test_sent_type_writes_every_field_it_models(name: str) -> None:
    cls = SENT_TYPES[name]
    values = {
        f.name: _placeholder(f)
        for f in dataclasses.fields(cls)
        if not f.name.startswith("_")
    }
    payload = cls(**values).to_dict()
    dropped = sorted(k for k in values if k not in payload)
    assert not dropped, f"{name}.to_dict() silently drops {dropped}"


@pytest.mark.parametrize("name", sorted(SENT_TYPES))
def test_sent_type_matches_spec_fields(name: str) -> None:
    cls = SENT_TYPES[name]
    stamped = STAMPED.get(name, set())
    # a required `type` is the discriminator to_dict stamps; an optional one
    # (a list item's label style) is a real field the caller sets
    if any(
        f["name"] == "type" and f.get("required")
        for f in SPEC["types"][name].get("fields", [])
    ):
        stamped = stamped | {"type"}
    modelled = {f for f in cls.__dataclass_fields__ if not f.startswith("_")}
    assert modelled | stamped == _spec_field_names(name), (
        f"{name} drifted from the Bot API spec; add the field to types.py. "
        "A sent type has no raw dict, so an unmodelled field is unreachable."
    )
