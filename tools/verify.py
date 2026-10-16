#!/usr/bin/env python3
"""Verify generated theme files against BOTH ground truths:

1. The Theme Builder's own import validator (replicates `eu()` from
   zed.dev/theme-builder, extracted 2026-10-16) — exact branch order.
2. Zed v1.23.2 schema (crates/settings_content/src/theme.rs =
   ThemeFamilyContent/ThemeContent/ThemeStyleContent) via key-set equality
   against tools/one-v1.23.2.json + schema-derived key blacklist.
"""
import json, hashlib, sys, re, tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REF = json.load(open(ROOT / "tools" / "one-v1.23.2.json"))
STYLE = REF["themes"][0]["style"]
REF_UI = set(k for k in STYLE if k != "syntax")          # includes players
REF_SYN = set(STYLE["syntax"].keys())

ANSI_SCHEMA = {f"terminal.ansi.{n}" for n in
    ("black", "red", "green", "yellow", "blue", "magenta", "cyan", "white",
     "bright_black", "bright_red", "bright_green", "bright_yellow",
     "bright_blue", "bright_magenta", "bright_cyan", "bright_white",
     "dim_black", "dim_red", "dim_green", "dim_yellow", "dim_blue",
     "dim_magenta", "dim_cyan", "dim_white")}

def builder_eu(data):
    """Exact replication of the builder validator branch order."""
    if not isinstance(data, dict):
        return "Invalid theme JSON: Data must be an object"
    if not isinstance(data.get("name"), str):
        return "Invalid theme JSON: Missing or invalid 'name' field"
    if not isinstance(data.get("author"), str):
        return "Invalid theme JSON: Missing or invalid 'author' field"
    themes = data.get("themes")
    if not isinstance(themes, list):
        return "Invalid theme JSON: 'themes' must be an array"
    for i, t in enumerate(themes):
        if not isinstance(t, dict):
            return f"Invalid theme JSON: Theme at index {i} must be an object"
        if not isinstance(t.get("name"), str):
            return f"Invalid theme JSON: Theme at index {i} missing or invalid 'name' field"
        if t.get("appearance") not in ("dark", "light"):
            return f"Invalid theme JSON: Theme at index {i} must have 'appearance' set to 'dark' or 'light'"
        if not isinstance(t.get("style"), dict):
            return f"Invalid theme JSON: Theme at index {i} missing or invalid 'style' field"
    return None  # PASS

def check_manifest():
    """extension.toml vs crates/extension/src/extension_manifest.rs (v1.23.2).
    Required: id, name, version, schema_version. packaging iterates
    manifest.themes, so listed paths MUST exist."""
    MANIFEST_KEYS = {"id", "name", "version", "schema_version", "description",
        "repository", "authors", "lib", "themes", "icon_themes", "languages",
        "grammars", "language_servers", "context_servers", "slash_commands",
        "snippets", "capabilities", "debug_adapters", "debug_locators",
        "language_model_providers"}
    path = ROOT / "extension.toml"
    m = tomllib.load(open(path, "rb"))
    problems = []
    for k in ("id", "name", "version", "schema_version"):
        if k not in m: problems.append(f"manifest missing required field {k!r}")
    unknown = set(m.keys()) - MANIFEST_KEYS
    if unknown: problems.append(f"manifest unknown fields: {sorted(unknown)}")
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", m.get("id", "")):
        problems.append(f"manifest id not lowercase-dash: {m.get('id')!r}")
    if not isinstance(m.get("schema_version"), int):
        problems.append("manifest schema_version must be an int (toml integer)")
    for rel in m.get("themes", []):
        if not (ROOT / rel).is_file():
            problems.append(f"manifest themes path missing: {rel}")
    listed = set(m.get("themes", []))
    on_disk = {f"themes/{f.name}" for f in (ROOT / "themes").glob("*.json")}
    if listed != on_disk:
        problems.append(f"manifest themes != themes/ on disk: listed {sorted(listed)}, disk {sorted(on_disk)}")
    print(f"{'PASS' if not problems else 'FAIL'}  extension.toml  id={m.get('id')}  themes={len(m.get('themes', []))}")
    return problems

problems = []
problems += check_manifest()
for f in sorted((ROOT / "themes").glob("*.json")) + sorted((ROOT / "builder").glob("*.json")):
    raw = f.read_bytes()
    try:
        doc = json.loads(raw)
    except Exception as e:
        print(f"FAIL  {f.name}: not valid JSON ({e})"); problems.append(f.name); continue

    err = builder_eu(doc)
    if err:
        print(f"FAIL  {f.name}: BUILDER {err}"); problems.append(f.name); continue

    for i, t in enumerate(doc["themes"]):
        style = t["style"]
        ui = set(style.keys()) - {"syntax"}
        ALLOWED = REF_UI | {"background.appearance", "element_selection_background"}   # schema-verified extras
        missing, extra = ALLOWED - ui, ui - ALLOWED
        if "background.appearance" in style and style["background.appearance"] not in ("opaque", "transparent", "blurred"):
            print(f"FAIL  {f.name}[{i}]: bad background.appearance {style['background.appearance']!r}")
            problems.append(f.name)
            continue
        syn = set(style["syntax"].keys())
        syn_missing, syn_extra = REF_SYN - syn, syn - REF_SYN
        bad_ansi = {k for k in ui if k.startswith("terminal.ansi.")} - ANSI_SCHEMA
        if missing or syn_missing or bad_ansi:
            print(f"FAIL  {f.name}[{i}]: missing={sorted(missing)} syn={sorted(syn_missing)} bad_ansi={sorted(bad_ansi)}")
            problems.append(f.name)
        if extra or syn_extra:
            print(f"FAIL  {f.name}[{i}]: extra={sorted(extra)} syn_extra={sorted(syn_extra)}")
            problems.append(f.name)
        # hex sanity: every leaf color is #rgb(±aa)
        bad_hex = []
        def walk(v, path=""):
            if path.split(".")[-1] in ("font_style", "font_weight"):
                return  # enum fields, not colors
            if path == "background.appearance":
                return  # enum field, not a color
            if isinstance(v, str):
                if re.fullmatch(r"#([0-9a-fA-F]{6})([0-9a-fA-F]{2})?", v) is None:
                    bad_hex.append(path)
            elif isinstance(v, dict):
                for k, vv in v.items(): walk(vv, f"{path}.{k}" if path else k)
            elif isinstance(v, list):
                for j, vv in enumerate(v): walk(vv, f"{path}[{j}]")
        walk(style)
        if bad_hex:
            print(f"FAIL  {f.name}[{i}] non-hex colors: {bad_hex[:6]}"); problems.append(f.name)

    h = hashlib.sha256(raw).hexdigest()
    status = "PASS" if f.name not in problems else "FAIL"
    print(f"{status}  {f.name}  {len(raw):6d}B  sha256 {h[:16]}…  themes={len(doc['themes'])}")

print("\nRESULT:", "ALL PASS" if not problems else f"{len(problems)} file(s) FAILED")
sys.exit(1 if problems else 0)