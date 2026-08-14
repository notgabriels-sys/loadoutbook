"""Behavioral tests for Loadoutbook's command-line interface."""

from pathlib import Path

from loadoutbook.cli import main


def write_plan(directory: Path, first_state: str = "packed") -> Path:
    """Write a deliberately fictional live-performance packing declaration."""
    plan_path = directory / "loadout.toml"
    plan_path.write_text(
        f"""
[loadout]
title = "Example live loadout"
project = "Example Artist"
requirements_basis = "Artist-declared transport and packing checklist."

[[items]]
id = "drum-machine"
position = 1
category = "instrument"
label = "Example drum machine"
location = "Main performance case"
critical = true
state = "{first_state}"
notes = ""

[[items]]
id = "power-cable"
position = 2
category = "power"
label = "Example power cable"
location = "Cable pouch"
critical = true
state = "packed"
notes = ""
""".strip(),
        encoding="utf-8",
    )
    return plan_path


def test_check_reports_a_declared_loadout_without_creating_a_bundle(tmp_path, capsys) -> None:
    """Check should read declared packing states and leave the plan directory unchanged."""
    plan_path = write_plan(tmp_path)

    exit_code = main(["check", str(plan_path)])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Declared status: declared" in captured.out
    assert "PHYSICAL PRESENCE, FUNCTION, TRANSPORT" in captured.out
    assert sorted(path.name for path in tmp_path.iterdir()) == ["loadout.toml"]


def test_build_writes_a_new_portable_loadout_bundle(tmp_path, capsys) -> None:
    """Build must produce the readable checklist, transport CSV, and manifest."""
    plan_path = write_plan(tmp_path)
    output_dir = tmp_path / "loadout-checklist"

    exit_code = main(["build", str(plan_path), "--output", str(output_dir)])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Wrote declared loadout bundle" in captured.out
    assert sorted(path.name for path in output_dir.iterdir()) == [
        "LOADOUT_CHECKLIST.md",
        "loadout-items.csv",
        "manifest.json",
    ]


def test_check_returns_attention_status_for_an_unpacked_declared_item(tmp_path, capsys) -> None:
    """A declared unpacked item must remain visible rather than appearing physically ready."""
    plan_path = write_plan(tmp_path, first_state="unpacked")

    exit_code = main(["check", str(plan_path)])

    captured = capsys.readouterr()
    assert exit_code == 2
    assert "Declared status: needs-packing" in captured.out
    assert "Unpacked critical declared items: drum-machine" in captured.out


def test_cli_reports_an_invalid_loadout_without_a_traceback(tmp_path, capsys) -> None:
    """Human-editable packing-state mistakes should yield one concise command-line error."""
    plan_path = write_plan(tmp_path, first_state="loaded")

    exit_code = main(["check", str(plan_path)])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert captured.out == ""
    assert "loadoutbook: invalid plan:" in captured.err
    assert "item state must be unpacked, packed, or not-needed" in captured.err
