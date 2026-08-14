"""Behavioral tests for Loadoutbook human-readable packing outputs."""

import json

from loadoutbook import config, report, service


def example_plan() -> config.LoadoutPlan:
    """Create a fictional loadout with an unresolved critical transport item."""
    return config.LoadoutPlan(
        loadout=config.Loadout(
            title="Example live loadout",
            project="Example Artist",
            requirements_basis="Artist-declared transport and packing checklist.",
        ),
        items=(
            config.Item(
                id="drum-machine",
                position=1,
                category="instrument",
                label="Example drum machine",
                location="Main performance case",
                critical=True,
                state="unpacked",
                notes="Confirm the physical case latch manually.",
            ),
            config.Item(
                id="power-cable",
                position=2,
                category="power",
                label="Example power cable",
                location="Cable pouch",
                critical=True,
                state="packed",
                notes="",
            ),
        ),
    )


def test_render_markdown_keeps_unpacked_critical_items_and_physical_boundary_visible() -> None:
    """A packing sheet must expose human-declared gaps without asserting physical readiness."""
    plan = example_plan()

    content = report.render_markdown(plan, service.assess(plan))

    assert "# Loadout checklist: Example live loadout" in content
    assert "LOADOUT NEEDS DECLARED PACKING" in content
    assert "PHYSICAL PRESENCE, FUNCTION, TRANSPORT" in content
    assert "Unpacked declared items: drum-machine" in content
    assert "Unpacked critical declared items: drum-machine" in content
    assert "Main performance case" in content
    assert "Confirm the physical case latch manually." in content


def test_render_csv_makes_every_declared_pack_state_portable_for_a_spreadsheet() -> None:
    """The transport list should retain location, criticality, and state in a compact table."""
    content = report.render_csv(example_plan())

    assert content.splitlines()[0] == ("position,id,category,label,location,critical,state,notes")
    assert (
        "1,drum-machine,instrument,Example drum machine,Main performance case,true,unpacked,"
        in content
    )
    assert "2,power-cable,power,Example power cable,Cable pouch,true,packed," in content


def test_write_bundle_creates_a_portable_loadout_checklist_without_local_paths(
    tmp_path,
) -> None:
    """A show-day handoff must retain declared packing text, not local transport evidence."""
    output_dir = tmp_path / "loadout-checklist"
    plan = example_plan()

    report.write_bundle(plan, service.assess(plan), output_dir)

    assert sorted(path.name for path in output_dir.iterdir()) == [
        "LOADOUT_CHECKLIST.md",
        "loadout-items.csv",
        "manifest.json",
    ]
    manifest = json.loads((output_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["declared_status"] == "needs-packing"
    assert manifest["assessment"]["unpacked_critical_item_ids"] == ["drum-machine"]
    assert str(tmp_path) not in json.dumps(manifest)
