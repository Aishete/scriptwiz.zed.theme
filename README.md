# Scriptwis Themes

Terminal-native dark themes for [Zed](https://zed.dev) — built from the
[scriptwiz](https://scriptwiz.net) design language: the green-of-a-prompt as
the accent, dashed-law colors on solid lines, and an editor that reads like a
shell session.

Three variants × three appearance levels — nine themes total:

| Variant | Soul | |
|---|---|---|
| `Scriptwis` | the site, pure — site tokens | |
| `Scriptwis Mocha` | scriptwiz grammar on your kitty's Catppuccin Mocha base | |
| `Scriptwis Magi` | NERV control room — red on black | |

Plain names are **transparent**: same see-through ladder, but with
`background.appearance: "transparent"` — wallpaper shows through **sharp**,
zero blur requested. Around it, the full intensity set (15 themes):

| flavor | what you see | views | active line | tab bands | chrome | enum |
|---|---|---|---|---|---|---|
| `[Light]` | most blur-through — lightest chrome | `00` | `2B` | `46` | `B0` | transparent |
| (plain) | standard transparent | `00` | `36` | `57` | `E3` | transparent |
| `[Heavy]` | heaviest translucent chrome — least bleed | `00` | `4D` | `80` | `EE` | transparent |
| hazy | 55% wash over the wallpaper | `8C` | `57` | `8C` | `E3` | blurred |
| opaque | solid surfaces | solid | solid | solid | solid | opaque |

The `[Light]`/`[Heavy]` mechanic mirrors Catppuccin Blur: editor stays `00`,
only the chrome bars slide along one opacity axis. Popups note: Zed blanks popup backgrounds on
any non-opaque theme, so the `- opaque` twin is the readable-popups escape
hatch. Flavor switching is instant via the theme selector (`ctrl-k ctrl-t`).

## Install

**As a dev extension (recommended — updates land on rebuild):**

```
git clone <this repo>
zed: install dev extension
```

Run `extensions: rebuild dev extension` after pulling changes — Zed parses
themes once at install/rebuild time, not on file change.

**As plain local themes:**

```
cp themes/*.json ~/.config/zed/themes/
```

Then pick via `theme selector: toggle` (bound to `ctrl-k ctrl-t`).

## What's themed

- **Every color key Zed v1.23.2's theme schema defines** (189 colors — editor,
  terminal ANSI 16 Mocha-verbatim, panels, tabs, scrollbar, minimap, diff
  hunks, indent guides, code lens, debugger, overlays, drop targets) plus
  `players` and git-graph `accents` — nothing left on defaults.
- **46 syntax captures** — keywords pink, strings prompt-green, types/ops the
  structural blue; doc comments and hints carry the shell-comment voice.
- **Git surfaces**: tree entry colors (M/A/R/I/U), gutter + inline blame in the
  accent color, git graph branch lanes cycling the variant accents.
- **Vim mode pills** (NORMAL/INSERT/VISUAL/LINE/BLOCK/REPLACE/YANK) and the
  helix family.
- **Markdown preview + agent panel markdown**, with GFM alert callouts mapped
  to status colors.

Note: Zed's theme schema has no border-*style* key — the dashed law of the
design language carries through color grammar, not dash patterns. (Panels draw
solid lines in every Zed theme; the dashed voice lives in the site and
projects this palette feeds.)

## Palette provenance

No invented hues — everything is harvested or derived:

| source | feeds |
|---|---|
| kitty `Catppuccin-Mocha.conf` (live terminal theme) | Mocha variant text + full ANSI 16 |
| scriptwiz site design tokens | accent green, prompt green, pink, blue, muted |
| approved "fusion" table (earlier theme previews) | Mocha base |
| magi skin | Magi variant |
| `Duskfox - blurred` (nvim-nightfox) | alpha-ladder blur pattern |
| arithmetic blends (50% dims, documented alphas) | everything else |

## Tooling

Plain stdlib, no dependencies:

```
python3 tools/build.py    # palettes.json -> themes/*.json + builder family file
python3 tools/verify.py   # schema key coverage + builder-validator checks + hex sanity
```

`palettes.json` is the single source of truth; `tools/schema-color-keys.json`
is the committed list of every color key in Zed v1.23.2's `ThemeColorsContent`
(so `verify.py` can prove full coverage, not just absence of typos).

## Theme Builder users

`builder/scriptwiz-family.json` imports into
[zed.dev/theme-builder](https://zed.dev/theme-builder). Heads-up: the builder
keeps a **snapshot from import time** and only round-trips the fields it knows
— it drops the blur ladder, vim pills, diff hunks, and accents. Treat builder
exports as scratch, keep this repo canonical.

## Screenshots

todo — first proper run wins: open a PR with `assets/*.png` if you get there.