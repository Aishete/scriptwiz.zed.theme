# PLAN.md — Scriptwiz themes for Zed

Date: 2026-10-16 · Status: **preview gate** (build + install happen only after he picks)

## 0. What this is

Three local Zed themes (dark, appearance `dark`) built from his REAL palettes —
zero invented hues outside arithmetic blends of existing tokens. Follows the
`terminal-themed-web-dev` design language (DESIGN.md) and the
`obsidian-theme-building` procedure (kitty harvest → HTML variant preview →
pick → build → install → verify).

## 1. Provenance (harvested, not remembered)

| Source | Path | Used for |
|---|---|---|
| kitty live theme | `~/.config/kitty/kitty.conf` → include → `/nix/store/6ikd9k…-kitty-themes…/Catppuccin-Mocha.conf` | variant B text + full ANSI 16 |
| portfolio tokens | `~/projects/portfolio/portfolioblog/DESIGN.md` §2 + `design-tests/theme.css :root` | variant A + syntax law |
| approved "fusion" table | `~/projects/obsidian-theme/preview/index.html` variant C | variant B base |
| magi skin | `design-tests/theme.css [data-theme="magi"]` | variant C |
| Zed key ground truth | `github.com/zed-industries/zed raw v1.23.2 assets/themes/one/one.json` | exact style key set |
| Installed binary check | `/nix/store/6qgdyx…-zed-editor-1.23.2/libexec/.zed-editor-wrapped` | all 140 UI key strings verified present in HIS binary; syntax keys parsed as nested paths (not literal) — validated against the v1.23.2 one.json instead |
| His zed settings | `~/.config/zed/settings.json` | dark mode, vim_mode, Caelusevka Nerd Font, project/outline panels left, agent right |

## 2. The three variants

| | A `Scriptwiz` | B `Scriptwiz Mocha` | C `Scriptwiz Magi` |
|---|---|---|---|
| Soul | the site, pure | his kitty terminal, site grammar (approved "fusion") | NERV red-on-black |
| editor bg | `#0a0a17` | `#1e1e2e` (kitty) | `#000000` |
| panels | `#0d0d1f` (card) | `#181825` (mantle) | `#0a0a0a` |
| bars/title/tab/status | `#101024` (pill bg) | `#11111b` (crust) | `#101010` |
| text | `#c1c1c5` | `#cdd6f4` (kitty fg) | `#e0e0e0` |
| accent (interactive/links/cursor) | `#9dc34f` | `#9dc34f` | `#ff0000` |
| syntax law | site: kw `#cb3d96`, fn/type/operator/enum `#446f84`, str `#92b159`, num/const/bool/`variable.special` `#cb3d96`, comment `#59596d`, comment.doc `#92b159`, punctuation `#59596d`, title `#9dc34f` | same site law, but text/primary on mocha `#cdd6f4`, comments mocha overlay `#6c7086` | magi: kw `#ff0000`, fn `#ff6666`, str `#ffd700`, num `#ffd700`, comment `#888888`, type `#ff6666`, op `#997a00` |
| terminal ANSI | closed-palette collapse: `black #0d0d1f · bright_black #59596d · red/magenta/yellow #cb3d96 · green #9dc34f · blue/cyan #446f84 · white #c1c1c5` (brights = normals per kitty law; dims = 50% blend to bg) | **kitty mocha 16 verbatim** (`#45475A…#A6ADC8`, brights=normals per his conf) | magi collapse: `red #ff0000 · green #997a00 · yellow #ffd700 · blue/magenta #663399 · cyan #997a00 · white #e0e0e0` |
| diagnostics | error `#cb3d96` · warning `#92b159` · success/info/accent greens | error `#f38ba8` · warning `#f9e2af` · success `#a6e3a1` (mocha ecosystem states; UI interaction stays site-green) | error `#ff0000` · warning `#ffd700` · success/created `#997a00` |
| **git blame** (gutter + inline + FileGit icon) | `#9dc34f` accent | `#9dc34f` accent (green, same as other variants — the mocha-gray default was the complaint) | `#ff0000` accent (follows the NERV highlight) |
| ↳ mechanism | `status.hint` → accent | verified: `git_ui/blame_ui.rs` paints gutter (line 209) + inline (line 293) blame with `.text_color(status().hint)`; syntax `hint` stays muted so hint-severity diagnostics don't shift |
| git | created `#9dc34f` · modified `#92b159` · deleted `#cb3d96` | created `#a6e3a1` · modified `#f9e2af` · deleted `#f38ba8` | created `#997a00` · modified `#ffd700` · deleted `#ff6666` |
| borders | `#3a3a55` (blueDim) · focused `#9dc34f` · selected `#446f84` | `#3a3a55` on mocha → `#585b70`-family blend · focused `#9dc34f` · selected `#446f84` | `#1a0000` · focused `#ff0000` · selected `#663399` |

Dashed law (DESIGN §5) cannot render in Zed — the v1.23.2 theme schema has no
border-style key (verified: 1526 lines, color fields only). Border COLOR GRAMMAR
carries instead: dim structural lines, green focused, blue selected, pink/gold
warnings, and focused borders snap to accent like the gallery's dashed-green
separators. The dashed voice stays in the HTML preview and the site; in Zed the
lines are solid but hold the same tokens.

Border map (gallery → Zed):

| gallery token | Zed keys |
|---|---|
| `--t-line` / `--t-border` (card/box edges) | `border`, `border.variant` (50% dim), `border.disabled` (75% dim) |
| green dashed card-header separators (`--t-accent`) | `border.focused`, `panel.focused_border`, `pane.focused_border` |
| `--t-blue` pill borders | `border.selected` |
| traffic dots / spinner solids | n/a (mockup-only; Zed has no dots) |

## 2b. Transparency — ported from the running theme

He currently runs **`Duskfox - blurred`** (nvim-nightfox ext). That theme does
blurring with NO user setting: `background.appearance: "blurred"` + a themed
alpha ladder over an otherwise identical key set (`window_background_opacity`
no longer exists in v1.23.2 settings). Ladder ported verbatim by role:

| role | alpha | keys |
|---|---|---|
| view surfaces | `00` | editor, gutter, terminal, panel backgrounds |
| chrome / bars | `E3` | background, title/status bar, surface, subheader |
| tab bands | `57` | tab_bar, tab inactive/active, toolbar |
| active line | `36` | editor.active_line |
| elevated surfaces | opaque | elevated_surface (modals must occlude) |
| lines / focused borders / search | keep | crisp lines over blur, per the gallery |

`window.appearance` per variant in palettes.json (flip to `"opaque"` to emit
solid variants; Nightfox ships -opaque/-blurred pairs — we can emit pairs too
if wanted).

## 2c. Style capability matrix (v1.23.2, verified in source 2026-10-16)

| design-language element | status | evidence / where |
|---|---|---|
| border color grammar (dim/green/blue/pink) | ✅ theme JSON | `border.*` keys (§2 table) |
| **dashed** lines | ❌ not reachable in stock Zed | gpui HAS the primitive (`border_style: BorderStyle`, paints through `paint_quad` — gpui/src/style.rs:285,736) but `ThemeStyleContent` + ALL settings_content files (editor/terminal/workspace/title_bar/project: 4639 lines) expose ZERO border-style keys. Stock Zed only draws dashes where elements hardcode them. A source patch could re-style chrome — separate exercise, not a theme |
| window blur | ✅ theme JSON | `background.appearance` + alpha ladder (§2b) |
| fonts (Caelusevka) | ✅ his settings | ui/buffer/agent font_family already set by him |
| line height ≈ site 1.65 | ✅ built-in default | `BufferLineHeight::Comfortable = 1.618` is Zed's default |
| vim NORMAL hollow cursor | ✅ built-in | vim_mode already set by him |
| wrap guides on / soft_wrap | ✅ his settings | `show_wrap_guides: true`, `soft_wrap: editor_width` already |
| **focused-pane accent frame** | ✅ TOP-LEVEL SETTING | `active_pane_modifiers: {"border_size": 1.0}` → 1px inset frame in `pane.focused_border` (= accent) — the closest Zed gets to the gallery's green frame. Key path verified on the all-settings page + 4 string hits in his binary |
| inactive-pane dim | ✅ setting, opt-out while blurred | `active_pane_modifiers.inactive_opacity` (skip: stacking with blur muddies) |
| centered tabs | ✅ built-in | — |
| `$`-command chrome headers | ❌ | panel headers are code-drawn strings |
| traffic dots | ❌ | system/Wayland titlebar owns that chrome |
| panel corner radius | ❌ | `CLIENT_SIDE_DECORATION_ROUNDING` is a compiled constant |

Settings patch queued for install time (needs his pick first):
```json
"active_pane_modifiers": { "border_size": 1.0 }
```

## 3. Zed key mapping strategy

- Emit the FULL key set of v1.23.2 `one.json` (140 UI + 46 syntax) per theme —
  complete coverage, nothing left to theme defaults silently. NO extra keys:
  `tab.hover_background` / `tab.border` / `terminal.ansi.dim_bright_*` are NOT
  in the `settings_content` `ThemeStyleContent` schema (verified in source) —
  one.json-identical key sets only.
- Elevation gradient (One Dark law, `background` lightest → editor darkest):
  A `#101024` / B `#181825` / C `#0a0a0a` chrome → panels A `#0d0d1f` B `#181825`
  C `#0a0a0a` → editor A `#0a0a17` B `#1e1e2e` C `#000000`. Active tab always
  matches editor bg (Zed law), tab bar matches panel bar bg.
- Derived tones are arithmetic only: dims = 50% blend toward bg, hovers =
  fixed alpha rgba of text/accent (one.json alpha style `…66/…3d`).
- `players[0]` (his cursor): cursor + selection = accent `…3d` selection alpha.
- `editor.active_line.background` = panel bg at `bf` alpha (One Dark pattern).
- `search.match_background` accent @66; active match pink/gold @66.
- `editor.wrap_guide` text alpha `0d`, active `1a` (One Dark pattern).

## 4. Procedure / status

1. [x] Harvest palettes → this file
2. [→] **Preview gate**: `preview/index.html` — full Zed-window mockup,
   switchable A/B/C (keys `1/2/3`, autoplay, pink toast, draggable palette),
   traffic dots + `$` headers + `grep: no matches found` empty state.
   He reviews visually and picks. NOTHING is installed before the pick.
3. [ ] Build: `tools/build.py` → `themes/{scriptwiz,scriptwiz-mocha,scriptwiz-magi}.json`
   (top-level `name`/`author` + one theme per file; verified JSON + key-set
   equality vs v1.23.2 one.json).
4. [ ] Install: copy picked file(s) → `~/.config/zed/themes/` with sha256
   compare; previous theme (`Duskfox - blurred`) stays as rollback — installing
   never deletes anything; switch = one-line `theme.dark` change in
   `~/.config/zed/settings.json` (he confirms before it is touched).
5. [ ] Verify + report; optional blur pairing snippet (`window_background_opacity`)
   documented, not applied.

## 4b. External contracts (extracted 2026-10-16, source-verified)

- **zed.dev/theme-builder import validator** (minified `eu()` in its JS,
  extracted): top-level object must have string `name`, string `author`,
  array `themes`; each theme needs string `name`, `appearance` exactly
  `"dark"`/`"light"`, object `style`. No style-key validation. Drag-drop takes
  .json/.jsonc/.zip (zip needs `themes/<name>.json` inside).
- **Zed local themes** (`theme_settings::deserialize_user_theme`,
  `ThemeFamilyContent`): `{name, author, themes[{name, appearance, style}]}`
  parsed with serde_json_lenient; `ThemeStyleContent` = colors flatten +
  status flatten + `players[{cursor,background,selection}]` + syntax free map
  + accents + window background appearance. Unknown style keys are silently
  ignored — hence reference-identical key sets, never more.
- `tools/verify.py` replicates the builder validator + checks key-set equality
  and hex sanity; `tools/build.py` emits per-theme files AND
  `themes/scriptwiz-family.json` (the builder-importable artifact).

## 5. File map

```
zed-theme/
├── extension.toml               ← extension manifest (root, ExtensionManifest schema)
├── palettes.json                ← single source of truth for all three variant tables
├── PLAN.md
├── themes/                      ← exactly what the manifest lists / what installs
│   ├── scriptwiz.json
│   ├── scriptwiz-mocha.json
│   └── scriptwiz-magi.json
├── builder/
│   └── scriptwiz-family.json    ← all three in one family; drag into zed.dev/theme-builder
│                                  (kept OUT of themes/ so packaging never double-loads)
├── preview/
│   └── index.html               ← the pick gate (self-contained, no CDN/fonts)
└── tools/
    ├── build.py                 ← palettes.json → Zed JSON (derives dims/blends/alphas)
    ├── one-v1.23.2.json         ← committed key-set reference (his exact Zed version)
    └── verify.py                ← manifest schema + builder validator + key sets + hex + sha
```

## 5b. Extension manifest contract (v1.23.2, crates/extension/src/extension_manifest.rs)

`extension.toml` = `ExtensionManifest`. Required: `id` (lowercase-dash),
`name`, `version`, `schema_version` (TOML int, current = 1). Packaging walks
`manifest.themes` literally — themes are NEVER auto-discovered, so verify.py
asserts manifest.themes == themes/ on disk. Canonical reference: the installed
nvim-nightfox extension.toml on this machine.

Install paths at build time (he picks ONE — names collide in the registry if
both are used):
1. **Dev extension**: `zed: extensions` → Install Dev Extension → select
   `~/projects/zed-theme` (manifest route; updates land on rebuild; rollback =
   uninstall, keep `Duskfox - blurred`).
2. **Local themes**: copy `themes/*.json` → `~/.config/zed/themes/` with sha256
   compare (skill-law route).