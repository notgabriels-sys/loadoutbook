# Loadoutbook

Loadoutbook turns a human-authored TOML file into a practical transport and
packing ledger for a hardware performance: a readable Markdown checklist, a
spreadsheet-ready item CSV, and a path-free manifest with hashes for both
generated files.

It complements the rest of a live workflow without replacing it:

- [Recallbook](https://github.com/notgabriels-sys/recallbook) records declared
  preset/backup recall steps.
- [Patchplot](https://github.com/notgabriels-sys/patchplot) records a declared
  stage layout and signal plan.
- [Showgrid](https://github.com/notgabriels-sys/showgrid) records a declared
  show-day plan.
- Loadoutbook records what you intend to pack and where you expect it to be.

It does **not** see physical equipment, confirm a case is loaded, inspect a
device, test function, verify a backup, assess electrical/transport safety,
contact a venue, establish access, validate a device recall, or decide that a
performance/show is ready.

## What it gives you

- Validates ordered, case-insensitively unique transport items.
- Requires a declared category, case/location cue, criticality flag, and
  packing state for every item.
- Makes every `unpacked` item visible, with critical unpacked items separately
  highlighted.
- Renders `LOADOUT_CHECKLIST.md`, `loadout-items.csv`, and a path-free
  `manifest.json`.
- Refuses to overwrite an existing output folder.

## What `declared` means

`declared` means every listed item is written as `packed` or `not-needed`. All
states are human-entered TOML fields. They do **not** prove a device or cable
is present, in the stated case, charged, compatible, working, safe to travel,
permitted at the venue, recalled correctly, or ready for a show.

## Install and try it

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install .

loadoutbook check examples/loadoutbook-example.toml
loadoutbook build examples/loadoutbook-example.toml --output ./loadout-checklist
```

The example is entirely fictional. Copy it to a new TOML file and replace the
declared item labels/locations with the current performance plan; it contains
no real equipment, venue, travel, or show data.

## Commands and exit codes

```text
loadoutbook check LOADOUT.toml
loadoutbook build LOADOUT.toml --output NEW_DIRECTORY
```

`check` is read-only. `build` creates one new checklist folder and fails
instead of replacing a prior loadout record.

| Exit code | Meaning |
| ---: | --- |
| `0` | Every item has a declared settled state; physical packing/function/transport/show readiness remain unverified. |
| `2` | The plan parsed, but one or more items remain `unpacked`. |
| `1` | The TOML is invalid, unreadable, or a new bundle could not be written. |

## Output bundle

```text
loadout-checklist/
├── LOADOUT_CHECKLIST.md
├── loadout-items.csv
└── manifest.json
```

The manifest contains only declared loadout text, unpacked item IDs, and
generated-file hashes/byte counts. It intentionally has no local media paths,
physical inventory data, serial numbers, transport route, venue confirmation,
device state, proof of packing, or show status.

## TOML shape

Every loadout has one `[loadout]` table and one or more `[[items]]` rows:

```toml
[loadout]
title = "Example live loadout"
project = "Example Artist"
requirements_basis = "Artist-declared transport and packing checklist."

[[items]]
id = "drum-machine"
position = 1
category = "instrument" # instrument, cable, power, backup, document, or other
label = "Example drum machine"
location = "Main performance case"
critical = true
state = "unpacked" # unpacked, packed, or not-needed
notes = "Optional human context."
```

Positions must be contiguous beginning at `1`; IDs are unique without regard
to case. `location` is an expected human cue, not a tracked position or proof
that an object is really there. `critical` is a visibility flag: it makes an
unpacked item stand out, but it does not certify an item as essential or safe.

## Development

```sh
python -m pip install -e '.[dev]'
python -m pytest -q
python -m ruff check src tests
python -m ruff format --check src tests
```

Released under the [MIT License](LICENSE).

---

<!-- funnel-footer -->
Part of a set of small, offline, local-first tools — [see all of them](https://github.com/notgabriels-sys).

Free and open source: [theme-contrast](https://github.com/notgabriels-sys/theme-contrast) (WCAG contrast checking for colour themes) · [htmlshot](https://github.com/notgabriels-sys/htmlshot) (HTML → exact-size PNG/PDF) · [50 dark themes for Claude Code](https://github.com/notgabriels-sys/claude-code-50-dark-themes).

Dark templates for documents, decks and app screens — [live demos](https://notgabriels-sys.github.io/dark-templates-demo/).
