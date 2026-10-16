#!/usr/bin/env python3
"""Verify generated theme files against BOTH ground truths:

1. The Theme Builder's own import validator (replicates `eu()` from
   zed.dev/theme-builder, extracted 2026-10-16) — exact branch order.
2. Zed v1.23.2 schema (crates/settings_content/src/theme.rs =
   ThemeFamilyContent/ThemeContent/ThemeStyleContent) via key-set equality
   against tools/one-v1.23.2.json + schema-derived key blacklist.
"""
import json, hashlib, sys, re
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

problems = []
for f in sorted((ROOT / "themes").glob("*.json")):
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
        missing, extra = REF_UI - ui, ui - REF_UI
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