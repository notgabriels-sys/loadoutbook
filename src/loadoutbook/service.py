"""Declared packing assessment for Loadoutbook."""

from dataclasses import dataclass

from loadoutbook.config import LoadoutPlan


@dataclass(frozen=True)
class Assessment:
    """Narrow declared packing state with all unpacked and critical-unpacked IDs visible."""

    status: str
    unpacked_item_ids: tuple[str, ...]
    unpacked_critical_item_ids: tuple[str, ...]


def assess(plan: LoadoutPlan) -> Assessment:
    """Assess written packing states without confirming physical items or transport readiness."""
    unpacked_item_ids = tuple(item.id for item in plan.items if item.state == "unpacked")
    unpacked_critical_item_ids = tuple(
        item.id for item in plan.items if item.critical and item.state == "unpacked"
    )
    status = "needs-packing" if unpacked_item_ids else "declared"
    return Assessment(
        status=status,
        unpacked_item_ids=unpacked_item_ids,
        unpacked_critical_item_ids=unpacked_critical_item_ids,
    )
