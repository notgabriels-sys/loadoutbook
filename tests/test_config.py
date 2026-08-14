"""Behavioral tests for Loadoutbook declared packing-plan parsing."""

import textwrap

import pytest

from loadoutbook import config


def item_block(
    identifier="drum-machine",
    position=1,
    category="instrument",
    label="Example drum machine",
    location="Main performance case",
    critical="true",
    state="packed",
    notes="",
):
    """Return one fictional transport-item declaration for parser behavior tests."""
    return textwrap.dedent(
        f"""
        [[items]]
        id = "{identifier}"
        position = {position}
        category = "{category}"
        label = "{label}"
        location = "{location}"
        critical = {critical}
        state = "{state}"
        notes = "{notes}"
        """
    ).strip()


def write_plan(directory, items=None):
    """Write a deliberately fictional live-performance loadout declaration."""
    plan_path = directory / "loadout.toml"
    plan_path.write_text(
        textwrap.dedent(
            f"""
            [loadout]
            title = "Example live loadout"
            project = "Example Artist"
            requirements_basis = "Artist-declared transport and packing checklist."

            {items or item_block()}
            """
        ).strip(),
        encoding="utf-8",
    )
    return plan_path


def test_load_plan_sorts_declared_items_by_position(tmp_path) -> None:
    """A printable packing list needs a stable, declared order even if TOML rows are reordered."""
    plan_path = write_plan(
        tmp_path,
        "\n\n".join(
            [
                item_block(identifier="power", position=2, category="power"),
                item_block(identifier="drum-machine", position=1),
            ]
        ),
    )

    plan = config.load_plan(plan_path)

    assert plan.loadout.title == "Example live loadout"
    assert [item.id for item in plan.items] == ["drum-machine", "power"]


def test_load_plan_rejects_case_insensitive_duplicate_ids_or_position_gaps(
    tmp_path,
) -> None:
    """A packing list cannot use an ambiguous ID or omit part of its declared sequence."""
    plan_path = write_plan(
        tmp_path,
        "\n\n".join(
            [
                item_block(identifier="power", position=1, category="power"),
                item_block(identifier="POWER", position=2, category="cable"),
            ]
        ),
    )

    with pytest.raises(ValueError, match="unique"):
        config.load_plan(plan_path)


def test_load_plan_rejects_unknown_category_or_pack_state(tmp_path) -> None:
    """An unclear category or state cannot silently look ready in a show-day checklist."""
    plan_path = write_plan(tmp_path, items=item_block(category="luggage", state="loaded"))

    with pytest.raises(ValueError, match="category"):
        config.load_plan(plan_path)


def test_load_plan_rejects_non_boolean_critical_flag(tmp_path) -> None:
    """Criticality must be explicit because it affects the visible show-day follow-up list."""
    plan_path = write_plan(tmp_path, items=item_block(critical='"mostly"'))

    with pytest.raises(TypeError, match="critical"):
        config.load_plan(plan_path)
