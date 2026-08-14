"""Behavioral tests for Loadoutbook declared packing assessment."""

from loadoutbook import config, service


def make_plan(states: tuple[str, ...]) -> config.LoadoutPlan:
    """Create a fictional packing list with a critical first item and chosen declared states."""
    return config.LoadoutPlan(
        loadout=config.Loadout(
            title="Example live loadout",
            project="Example Artist",
            requirements_basis="Artist-declared transport and packing checklist.",
        ),
        items=tuple(
            config.Item(
                id=f"item-{position}",
                position=position,
                category="instrument" if position == 1 else "cable",
                label=f"Example item {position}",
                location="Example performance case",
                critical=position == 1,
                state=state,
                notes="",
            )
            for position, state in enumerate(states, start=1)
        ),
    )


def test_assess_keeps_every_unpacked_item_visible_and_flags_critical_ones() -> None:
    """A packing ledger must not conceal an unpacked item simply because it is non-critical."""
    assessment = service.assess(make_plan(("unpacked", "unpacked")))

    assert assessment.status == "needs-packing"
    assert assessment.unpacked_item_ids == ("item-1", "item-2")
    assert assessment.unpacked_critical_item_ids == ("item-1",)


def test_assess_marks_only_fully_settled_declared_items_as_declared() -> None:
    """Packed and explicitly not-needed rows are declared states, not physical evidence."""
    assessment = service.assess(make_plan(("packed", "not-needed")))

    assert assessment.status == "declared"
    assert assessment.unpacked_item_ids == ()
    assert assessment.unpacked_critical_item_ids == ()
