"""Configuration parsing for Loadoutbook declared live-performance loadouts."""

import tomllib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Loadout:
    """Declared context for one transport and packing checklist."""

    title: str
    project: str
    requirements_basis: str


@dataclass(frozen=True)
class Item:
    """One declared transport item and its human-declared packing state."""

    id: str
    position: int
    category: str
    label: str
    location: str
    critical: bool
    state: str
    notes: str


@dataclass(frozen=True)
class LoadoutPlan:
    """An ordered declared transport/loadout plan."""

    loadout: Loadout
    items: tuple[Item, ...]


def required_text(value: object, field: str) -> str:
    """Return nonempty declared text or reject an ambiguous packing-plan field."""
    if not isinstance(value, str) or not (text := value.strip()):
        raise ValueError(f"{field} must be a nonempty string")
    return text


def optional_text(value: object, field: str) -> str:
    """Return an optional human note, retaining an intentional blank but rejecting other types."""
    if not isinstance(value, str):
        raise TypeError(f"{field} must be a string")
    return value.strip()


def positive_position(value: object) -> int:
    """Return a positive ordering number while rejecting booleans and fractional values."""
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError("item position must be a positive integer")
    return value


def load_plan(path: Path) -> LoadoutPlan:
    """Load a checklist without checking physical items, transport, or venue access."""
    with Path(path).open("rb") as handle:
        document = tomllib.load(handle)

    loadout_document = document["loadout"]
    loadout = Loadout(
        title=required_text(loadout_document["title"], "loadout title"),
        project=required_text(loadout_document["project"], "loadout project"),
        requirements_basis=required_text(
            loadout_document["requirements_basis"], "loadout requirements_basis"
        ),
    )
    items = tuple(
        Item(
            id=required_text(item["id"], "item id"),
            position=positive_position(item["position"]),
            category=required_text(item["category"], "item category"),
            label=required_text(item["label"], "item label"),
            location=required_text(item["location"], "item location"),
            critical=item["critical"],
            state=required_text(item["state"], "item state"),
            notes=optional_text(item["notes"], "item notes"),
        )
        for item in document["items"]
    )
    if any(not isinstance(item.critical, bool) for item in items):
        raise TypeError("item critical must be a boolean")
    ordered_items = tuple(sorted(items, key=lambda item: item.position))
    if not ordered_items:
        raise ValueError("loadout requires at least one declared item")
    if len({item.id.casefold() for item in ordered_items}) != len(ordered_items):
        raise ValueError("item IDs must be unique without regard to case")
    if [item.position for item in ordered_items] != list(range(1, len(ordered_items) + 1)):
        raise ValueError("item positions must be contiguous and begin at 1")
    if any(
        item.category not in {"instrument", "cable", "power", "backup", "document", "other"}
        for item in ordered_items
    ):
        raise ValueError(
            "item category must be instrument, cable, power, backup, document, or other"
        )
    if any(item.state not in {"unpacked", "packed", "not-needed"} for item in ordered_items):
        raise ValueError("item state must be unpacked, packed, or not-needed")
    return LoadoutPlan(loadout=loadout, items=ordered_items)
