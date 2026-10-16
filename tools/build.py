#!/usr/bin/env python3
"""palettes.json -> local Zed theme JSON files.

Emits the COMPLETE style key set of Zed v1.23.2 one.json (140 UI + 46 syntax,
committed as tools/one-v1.23.2.json = the version running on this machine).
Derived tones are pure arithmetic: dims = 50% blend toward editor bg,
status borders = 45% blend, status backgrounds = color @ 1a, hovers/selections
= fixed alphas (one.json patterns 66/3d/1a/bf). No invented hues.
"""
import json, hashlib, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REF = json.load(open(ROOT / "tools" / "one-v1.23.2.json"))
REF_UI = set(k for k in REF["themes"][0]["style"] if k != "syntax")
REF_SYN = set(REF["themes"][0]["style"]["syntax"].keys())

def parse_hex(c):
    c = c.strip().lstrip("#")
    if len(c) == 6: return (int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16), 255)
    if len(c) == 8: return (int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16), int(c[6:8], 16))
    raise ValueError(c)

def parse_color(c):
    if c.startswith("rgba("):
        parts = c[5:-1].split(",")
        r, g, b, a = (float(p) for p in parts)
        return (int(r), int(g), int(b), round(a * 255))
    return parse_hex(c)

def to_hex(c):
    return "#%02x%02x%02x%02x" % c

def rgb_alpha(hex_color, alpha):
    r, g, b, _ = parse_hex(hex_color)
    return "#%02x%02x%02x%02x" % (r, g, b, alpha)

def mix(c1, c2, w1):
    """w1 = weight of c1 (0..1)."""
    a, b = parse_hex(c1), parse_hex(c2)
    out = tuple(round(a[i] * w1 + b[i] * (1 - w1)) for i in range(3))
    return "#%02x%02x%02x" % out[:3]

def dim(color, bg):
    return mix(color, bg, 0.5)

def status_triple(color, bg):
    return {
        "base": color,
        "background": rgb_alpha(color, 0x1A),
        "border": mix(color, bg, 0.45),
    }

def build_theme(v, pal):
    base = pal["base"]
    editor, panel, bar = base["editor_bg"], base["panel_bg"], base["bar_bg"]
    text, muted, accent = base["text"], base["muted"], base["accent"]
    blue, pink, cursor = base["blue"], base["pink"], base["cursor"]
    gold = base.get("gold")
    hover_src = parse_color(base["hover"])
    hover = to_hex(hover_src)
    hover2x = "#%02x%02x%02x%02x" % (*hover_src[:3], max(0, hover_src[3] * 2))
    warn = base["warning"]

    ansi_normals = {n: pal["ansi"][n] for n in ("black", "red", "green", "yellow",
                                               "blue", "magenta", "cyan", "white")}
    term_fg = pal["terminal"]["fg"]

    er, em = status_triple(base["error"], editor), status_triple(base["warning"], editor)
    su = status_triple(base["success"], editor)

    # git + diagnostics share the variant's ecosystem colors (PLAN §2)
    git = pal.get("git", {"created": base["success"], "modified": warn, "deleted": base["error"]})
    created, modified, deleted = git["created"], git["modified"], git["deleted"]

    syn = {k: val for k, val in pal["syntax"].items() if val and k != "hint2"}
    italic_keys = {"link_text", "predictive", "comment.doc"}
    bold_keys = {"emphasis.strong"}

    st = {}

    # --- borders ---
    st["border"]                    = base["border"]
    st["border.variant"]            = mix(base["border"], editor, 0.5)
    st["border.focused"]            = base["border_focused"]
    st["border.selected"]           = base["border_selected"]
    st["border.transparent"]        = "#00000000"
    st["border.disabled"]           = mix(base["border"], editor, 0.75)

    # --- elevation gradient (One Dark law; B keeps mocha elevation) ---
    st["background"]                = bar
    st["elevated_surface.background"] = panel
    st["surface.background"]        = panel
    st["element.background"]        = panel
    st["element.hover"]             = hover
    st["element.active"]            = hover2x
    st["element.selected"]          = hover2x
    st["element.disabled"]          = panel
    st["ghost_element.background"]  = "#00000000"
    st["ghost_element.hover"]       = hover
    st["ghost_element.active"]      = hover2x
    st["ghost_element.selected"]    = hover2x
    st["ghost_element.disabled"]    = "#00000000"
    st["drop_target.background"]    = rgb_alpha(accent, 0x50)

    # --- text + icons ---
    st["text"]                      = text
    st["text.muted"]                = muted
    st["text.placeholder"]          = muted
    st["text.disabled"]             = muted
    st["text.accent"]               = accent
    st["icon"]                      = text
    st["icon.muted"]                = muted
    st["icon.disabled"]             = muted
    st["icon.placeholder"]          = muted
    st["icon.accent"]               = accent

    # --- bars / tabs / panels ---
    st["status_bar.background"]     = bar
    st["title_bar.background"]      = bar
    st["title_bar.inactive_background"] = mix(bar, editor, 0.6)
    st["toolbar.background"]        = editor
    st["tab_bar.background"]        = bar
    st["tab.inactive_background"]   = bar
    st["tab.active_background"]     = editor
    st["panel.background"]          = panel
    st["panel.focused_border"]      = base["border_focused"]
    st["pane.focused_border"]       = base["border_focused"]
    st["search.match_background"]   = rgb_alpha(accent, 0x66)
    st["search.active_match_background"] = rgb_alpha(gold if gold else pink, 0x66)

    # --- scrollbar ---
    st["scrollbar.thumb.background"] = rgb_alpha(text, 0x4C)
    st["scrollbar.thumb.hover_background"] = hover2x
    st["scrollbar.thumb.border"]    = panel
    st["scrollbar.track.background"] = "#00000000"
    st["scrollbar.track.border"]    = panel

    # --- editor ---
    st["editor.foreground"]         = text
    st["editor.background"]         = editor
    st["editor.gutter.background"]  = editor
    st["editor.subheader.background"] = panel
    st["editor.active_line.background"] = rgb_alpha(panel, 0xBF)
    st["editor.highlighted_line.background"] = hover
    st["editor.line_number"]        = mix(muted, editor, 0.55)
    st["editor.active_line_number"] = text
    st["editor.hover_line_number"]  = mix(text, muted, 0.5)
    st["editor.invisible"]          = mix(muted, editor, 0.6)
    st["editor.wrap_guide"]         = rgb_alpha(text, 0x0D)
    st["editor.active_wrap_guide"]  = rgb_alpha(text, 0x1A)
    st["editor.document_highlight.read_background"] = rgb_alpha(accent, 0x1A)
    st["editor.document_highlight.write_background"] = rgb_alpha(muted, 0x40)

    # --- terminal (variant B = kitty 16 verbatim; exactly the 24 schema keys) ---
    st["terminal.background"]       = editor
    st["terminal.foreground"]       = term_fg
    st["terminal.bright_foreground"] = pal["terminal"]["bright_fg"]
    st["terminal.dim_foreground"]   = dim(term_fg, editor)
    for name, val in ansi_normals.items():
        st[f"terminal.ansi.{name}"] = val
        st[f"terminal.ansi.bright_{name}"] = pal["ansi"].get(f"bright_{name}", val)
        st[f"terminal.ansi.dim_{name}"] = dim(val, editor)

    st["link_text.hover"] = accent

    # --- vcs + status families ---
    st["version_control.added"]     = rgb_alpha(created, 0xFF)
    st["version_control.modified"]  = rgb_alpha(modified, 0xFF)
    st["version_control.deleted"]   = rgb_alpha(deleted, 0xFF)
    st["version_control.word_added"] = rgb_alpha(created, 0x59)
    st["version_control.word_deleted"] = rgb_alpha(deleted, 0xCC)
    st["version_control.conflict_marker.ours"] = rgb_alpha(base["success"], 0x1A)
    st["version_control.conflict_marker.theirs"] = rgb_alpha(accent, 0x1A)

    families = [
        ("conflict", warn), ("created", created), ("deleted", deleted),
        ("error", base["error"]), ("hidden", muted), ("ignored", muted),
        ("modified", modified), ("predictive", muted), ("renamed", accent),
        ("success", base["success"]), ("warning", base["warning"]),
        ("info", pal.get("info", blue)),
    ]
    families.append(("hint", syn.get("hint", muted)))
    families.append(("unreachable", muted))
    for name, color in families:
        t = status_triple(color, editor)
        st[name] = t["base"]; st[f"{name}.background"] = t["background"]; st[f"{name}.border"] = t["border"]

    # --- players: [0] = his cursor; extras for collab ---
    players = [
        {"cursor": cursor, "background": cursor, "selection": rgb_alpha(cursor, 0x3D)},
        {"cursor": pink, "background": pink, "selection": rgb_alpha(pink, 0x3D)},
        {"cursor": blue, "background": blue, "selection": rgb_alpha(blue, 0x3D)},
    ]

    # --- syntax (full 46-key set) ---
    syntax = {}
    for key in sorted(REF_SYN):
        color = syn.get(key, text)
        entry = {"color": color, "font_style": None, "font_weight": None}
        if key in italic_keys: entry["font_style"] = "italic"
        if key in bold_keys: entry["font_weight"] = 700
        syntax[key] = entry
    st["syntax"] = syntax

    return {"name": pal["name"], "appearance": "dark", "style": st}, players

def apply_appearance(st, appearance):
    """Alpha ladder ported from 'Duskfox - blurred' (nvim-nightfox ext, the theme
    he runs today): view surfaces 00, chrome/bars E3, tab bands 57, active line
    36. Border/separator lines stay crisp; elevated_surface stays opaque so
    modals occlude. Opaque = no-op (plain solid colors as built)."""
    if appearance == "opaque":
        return
    st["background.appearance"] = appearance
    def a(color, alpha):
        return "%s%02x" % (color[:7], alpha)
    for k in ("editor.background", "editor.gutter.background",
              "terminal.background", "panel.background"):
        st[k] = a(st[k], 0x00)
    for k in ("background", "title_bar.background", "status_bar.background",
              "surface.background", "editor.subheader.background"):
        st[k] = a(st[k], 0xE3)
    for k in ("tab_bar.background", "tab.inactive_background",
              "tab.active_background", "toolbar.background"):
        st[k] = a(st[k], 0x57)
    st["editor.active_line.background"] = a(st["editor.active_line.background"], 0x36)


def main():
    pal = json.load(open(ROOT / "palettes.json"))
    problems, family_themes = [], []
    for vid, v in pal["variants"].items():
        theme, players = build_theme(vid, v)
        theme["style"]["players"] = players
        apply_appearance(theme["style"], v.get("window", {}).get("appearance", "opaque"))
        family_themes.append(theme)
        doc = {"name": v["name"], "author": pal["meta"]["author"], "themes": [theme]}
        ALLOWED_UI = REF_UI | {"background.appearance"}
        ui_emitted = set(theme["style"].keys()) - {"syntax"}
        missing = sorted(ALLOWED_UI - ui_emitted)
        extra = sorted(ui_emitted - ALLOWED_UI)
        syn_emitted = set(theme["style"]["syntax"].keys())
        syn_missing = sorted(REF_SYN - syn_emitted); syn_extra = sorted(syn_emitted - REF_SYN)
        if missing or syn_missing:
            problems.append(f"{vid} missing: UI {missing} SYN {syn_missing}")
        if extra or syn_extra:
            problems.append(f"{vid} extra (NOT in v1.23.2): UI {extra} SYN {syn_extra}")
        fname = v["name"].lower().replace(" ", "-") + ".json"
        out = ROOT / "themes" / fname
        json.dump(doc, open(out, "w"), indent=2)
        data = out.read_bytes()
        print(f"{out.relative_to(ROOT)}  {len(data):6d}B  sha256 {hashlib.sha256(data).hexdigest()[:16]}…"
              f"  ui={len(ui_emitted)} syn={len(syn_emitted)} players=3")
    if problems:
        print("PROBLEMS:"); [print(" -", p) for p in problems]; sys.exit(1)
    fam = {"name": "Scriptwiz", "author": pal["meta"]["author"], "themes": family_themes}
    bdir = ROOT / "builder"
    bdir.mkdir(exist_ok=True)
    fout = bdir / "scriptwiz-family.json"   # NOT in themes/: the extension must not double-load it
    json.dump(fam, open(fout, "w"), indent=2)
    data = fout.read_bytes()
    print(f"{fout.relative_to(ROOT)}  {len(data):6d}B  sha256 {hashlib.sha256(data).hexdigest()[:16]}…  "
          f"family with {len(family_themes)} themes (builder-importable)")
    print("ALL KEY SETS == v1.23.2 one.json reference: PASS")

if __name__ == "__main__":
    main()