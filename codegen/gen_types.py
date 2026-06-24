"""Generate src/moonlygram/_types_generated.py from the vendored Bot API spec.

This is a build-time tool, not a runtime dependency: it reads codegen/api.json
and emits dataclasses for the received "data-only" types listed in
overrides.GENERATE, matching the hand-written house style (slots dataclass,
plain-prose docstring, a from_dict that parses nested types and keeps the
original dict in `raw`). Behavior-bearing types (shortcut methods, binding) and
the bespoke sent types stay hand-written in types.py.

Run ``python codegen/gen_types.py`` after editing overrides.py or refreshing the
spec. The output is deterministic, so re-running on an unchanged spec leaves the
file byte-for-byte identical.
"""
from __future__ import annotations

import json
import textwrap
from pathlib import Path
from typing import Any

import overrides as ov

ROOT = Path(__file__).resolve().parent.parent
SPEC_PATH = Path(__file__).resolve().parent / "api.json"
OUT_PATH = ROOT / "src" / "moonlygram" / "_types_generated.py"

_PRIMITIVES = {
    "String": "str",
    "Integer": "int",
    "Boolean": "bool",
    "Float": "float",
    "Float number": "float",
    "True": "bool",
}


def parseable(spec: dict[str, Any]) -> set[str]:
    """Type names a generated from_dict may parse with ``<Name>.from_dict(...)``."""
    return (
        set(ov.GENERATE)
        | set(ov.FLAT_UNIONS)
        | set(ov.BEHAVIOR_TYPES)
        | set(ov.HANDWRITTEN_PARSEABLE)
    )


def split_array(token: str) -> tuple[int, str]:
    """Return (array depth, innermost base token) for a spec type string."""
    depth = 0
    while token.startswith("Array of "):
        token = token[len("Array of ") :]
        depth += 1
    return depth, token


def annotate(types: list[str], known: set[str]) -> str:
    """Map a field's spec `types` list to its Python annotation.

    A field whose innermost token is a modelled object keeps that class as its
    type; one we do not model is stored verbatim, so it is typed dict[str, Any]
    (truthfully — that is what from_dict leaves in place).
    """
    if len(types) > 1:
        # The spec only ever unions primitives (e.g. Integer|String); anything
        # exotic degrades to Any rather than guessing.
        mapped = [_PRIMITIVES.get(t) for t in types]
        if all(mapped):
            return " | ".join(dict.fromkeys(mapped))  # type: ignore[arg-type]
        return "Any"

    depth, base = split_array(types[0])
    if base in _PRIMITIVES:
        inner = _PRIMITIVES[base]
    elif base in known:
        inner = base
    else:
        inner = "dict[str, Any]"
    ann = inner
    for _ in range(depth):
        ann = f"list[{ann}]"
    return ann


def parse_expr(api: str, types: list[str], known: set[str]) -> str:
    """Build the from_dict right-hand side that produces this field's value.

    Parsing is lenient by design (mirroring the hand-written types and tolerant
    of a server whose payload omits a field the spec already lists): scalars and
    unmodelled objects fall back to ``.get``, and modelled objects are parsed
    only when present. The declared field type still reflects the spec (required
    fields are non-Optional); the generated de-serialization is exempt from
    mypy's arg-type check (see the per-module override in pyproject.toml), since
    a missing field should degrade to None rather than crash.
    """
    depth, base = split_array(types[0])
    is_object = len(types) == 1 and base not in _PRIMITIVES and base in known

    if not is_object:
        # Primitive, primitive union, or an object we do not model (kept raw).
        return f'd.get("{api}")'

    src = f'd["{api}"]'
    if depth == 0:
        inner = f"{base}.from_dict({src})"
    elif depth == 1:
        inner = f"[{base}.from_dict(i) for i in {src}]"
    else:  # depth == 2 (rare)
        inner = f"[[{base}.from_dict(j) for j in i] for i in {src}]"
    return f'{inner} if "{api}" in d else None'


def field_default(required: bool) -> str:
    return "" if required else " = None"


def wrap_doc(description: list[str]) -> list[str]:
    text = " ".join(line.strip() for line in description).strip()
    if not text:
        return []
    return textwrap.wrap(text, width=79)


def merge_union_fields(
    entry: dict[str, Any], spec: dict[str, Any]
) -> list[dict[str, Any]]:
    """Flatten an abstract subtypes union into one field list.

    Fields are collected across every concrete subtype in first-seen order. A
    field is required only when it appears in ALL subtypes and is required in
    each — so the discriminator (type / status / source) stays required and the
    variant-specific fields become optional.
    """
    subtypes = entry["subtypes"]
    occurrences: dict[str, list[dict[str, Any]]] = {}
    order: list[str] = []
    for sub_name in subtypes:
        for f in spec["types"][sub_name].get("fields", []):
            if f["name"] not in occurrences:
                order.append(f["name"])
                occurrences[f["name"]] = []
            occurrences[f["name"]].append(f)

    merged: list[dict[str, Any]] = []
    for fname in order:
        occ = occurrences[fname]
        required = len(occ) == len(subtypes) and all(
            f.get("required", False) for f in occ
        )
        field = dict(occ[0])
        field["required"] = required
        merged.append(field)
    return merged


def render_class(
    name: str, fields: list[dict[str, Any]], doc: list[str], known: set[str]
) -> str:
    # dataclass ordering: required (no default) first, then optional, then raw.
    ordered = sorted(fields, key=lambda f: not f.get("required", False))

    lines: list[str] = ["@dataclass(slots=True)", f"class {name}:"]
    if doc:
        if len(doc) == 1:
            lines.append(f'    """{doc[0]}"""')
        else:
            lines.append(f'    """{doc[0]}')
            lines.extend(f"    {line}" for line in doc[1:])
            lines.append('    """')
    lines.append("")

    field_specs = []  # (py_name, api_name, types, required, annotation)
    for f in ordered:
        api = f["name"]
        py = "from_user" if api == "from" else api
        required = bool(f.get("required", False))
        override = ov.FIELD_TYPE_OVERRIDES.get((name, api))
        ann = override.strip('"') if override else annotate(f["types"], known)
        field_specs.append((py, api, f["types"], required, ann))

    for py, _api, _types, required, ann in field_specs:
        annotation = ann if required else f"Optional[{ann}]"
        lines.append(f"    {py}: {annotation}{field_default(required)}")
    lines.append(
        "    raw: dict[str, Any] = "
        "field(default_factory=dict, repr=False, compare=False)"
    )
    lines.append("")

    lines.append("    @classmethod")
    lines.append(f'    def from_dict(cls, d: dict[str, Any]) -> "{name}":')
    lines.append("        return cls(")
    for py, api, types, _required, _ann in field_specs:
        override = ov.FIELD_PARSE_OVERRIDES.get((name, api))
        expr = (
            override.format(d="d", k=api)
            if override
            else parse_expr(api, types, known)
        )
        lines.append(f"            {py}={expr},")
    lines.append("            raw=d,")
    lines.append("        )")
    return "\n".join(lines)


def emit_type(name: str, entry: dict[str, Any], known: set[str]) -> str:
    return render_class(name, entry.get("fields", []), wrap_doc(entry["description"]), known)


def emit_flat_union(
    name: str, entry: dict[str, Any], spec: dict[str, Any], known: set[str]
) -> str:
    fields = merge_union_fields(entry, spec)
    return render_class(name, fields, wrap_doc(entry["description"]), known)


def _fields_of(name: str, spec: dict[str, Any]) -> list[dict[str, Any]]:
    entry = spec["types"][name]
    if name in ov.FLAT_UNIONS:
        return merge_union_fields(entry, spec)
    return entry.get("fields", [])


def referenced_handwritten(names: list[str], spec: dict[str, Any]) -> list[str]:
    """Hand-written/behavior type names that generated from_dict code calls."""
    wanted: set[str] = set()
    handwritten = set(ov.BEHAVIOR_TYPES) | set(ov.HANDWRITTEN_PARSEABLE)
    for name in names:
        for f in _fields_of(name, spec):
            if len(f["types"]) != 1:
                continue
            _, base = split_array(f["types"][0])
            if base in handwritten:
                wanted.add(base)
    return sorted(wanted | set(ov.EXTRA_IMPORTS_FROM_TYPES))


def generate() -> str:
    spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    known = parseable(spec)
    names = sorted(set(ov.GENERATE) | set(ov.FLAT_UNIONS))

    imports = referenced_handwritten(names, spec)
    header = [
        '"""Generated Bot API data types — do not edit by hand.',
        "",
        f"Produced by codegen/gen_types.py from {spec.get('version', '?')}.",
        "Edit codegen/overrides.py and re-run the generator instead.",
        '"""',
        "from __future__ import annotations",
        "",
        "from dataclasses import dataclass, field",
        "from typing import Any, Optional",
        "",
    ]
    if imports:
        header.append(
            "from .types import (  # noqa: E402\n"
            + "".join(f"    {n} as {n},\n" for n in imports)
            + ")"
        )
        header.append("")
    blocks = []
    for name in names:
        entry = spec["types"][name]
        if name in ov.FLAT_UNIONS:
            blocks.append(emit_flat_union(name, entry, spec, known))
        else:
            blocks.append(emit_type(name, entry, known))
    return "\n".join(header) + "\n\n" + "\n\n\n".join(blocks) + "\n"


def main() -> None:
    OUT_PATH.write_text(generate(), encoding="utf-8")
    total = len(ov.GENERATE) + len(ov.FLAT_UNIONS)
    print(f"wrote {OUT_PATH.relative_to(ROOT)} ({total} types)")


if __name__ == "__main__":
    main()
