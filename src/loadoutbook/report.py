"""Human-readable declared loadout-checklist rendering for Loadoutbook."""

import csv
import hashlib
import json
from io import StringIO
from pathlib import Path

from loadoutbook.config import LoadoutPlan
from loadoutbook.service import Assessment

DECLARED_BOUNDARY = (
    "DECLARED LOADOUT CHECKLIST - PHYSICAL PRESENCE, FUNCTION, TRANSPORT, VENUE ACCESS, "
    "DEVICE RECALL, PERFORMANCE, AND SHOW STATUS UNVERIFIED"
)
PACKING_BOUNDARY = (
    "LOADOUT NEEDS DECLARED PACKING - ONE OR MORE ITEMS REMAIN UNPACKED; PHYSICAL PRESENCE, "
    "FUNCTION, TRANSPORT, VENUE ACCESS, DEVICE RECALL, PERFORMANCE, AND SHOW STATUS UNVERIFIED"
)


def markdown_cell(value: str) -> str:
    """Keep declared packing text within one portable Markdown table cell."""
    return (
        value.replace("\\", "\\\\")
        .replace("|", "\\|")
        .replace("\r\n", "\n")
        .replace("\r", "\n")
        .replace("\n", "<br>")
    )


def render_markdown(plan: LoadoutPlan, assessment: Assessment) -> str:
    """Render a declared checklist without seeing or manipulating any physical item."""
    boundary = PACKING_BOUNDARY if assessment.status == "needs-packing" else DECLARED_BOUNDARY
    lines = [
        f"# Loadout checklist: {plan.loadout.title}",
        "",
        "## Declared packing status",
        "",
        f"**Status:** {assessment.status}",
        "",
        f"**Boundary:** {boundary}",
        "",
        f"**Project:** {plan.loadout.project}",
        f"**Declared basis:** {plan.loadout.requirements_basis}",
        "",
    ]
    if assessment.unpacked_item_ids:
        lines.extend(
            [
                "**Unpacked declared items: " + ", ".join(assessment.unpacked_item_ids) + "**",
                "",
            ]
        )
    if assessment.unpacked_critical_item_ids:
        lines.extend(
            [
                "**Unpacked critical declared items: "
                + ", ".join(assessment.unpacked_critical_item_ids)
                + "**",
                "",
            ]
        )
    lines.extend(
        [
            "## Declared loadout items",
            "",
            "| Position | Category | Item | Declared location | "
            "Critical | Declared state | Notes |",
            "| ---: | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for item in plan.items:
        lines.append(
            "| "
            f"{item.position} | {markdown_cell(item.category)} | {markdown_cell(item.label)} | "
            f"{markdown_cell(item.location)} | {str(item.critical).lower()} | "
            f"{markdown_cell(item.state)} | {markdown_cell(item.notes)} |"
        )
    return "\n".join(lines) + "\n"


def render_csv(plan: LoadoutPlan) -> str:
    """Render every declared transport item in a spreadsheet-ready portable table."""
    fields = (
        "position",
        "id",
        "category",
        "label",
        "location",
        "critical",
        "state",
        "notes",
    )
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for item in plan.items:
        writer.writerow(
            {
                "position": item.position,
                "id": item.id,
                "category": item.category,
                "label": item.label,
                "location": item.location,
                "critical": str(item.critical).lower(),
                "state": item.state,
                "notes": item.notes,
            }
        )
    return buffer.getvalue()


def artifact_record(content: str) -> dict[str, int | str]:
    """Describe a generated checklist artifact without including its local output location."""
    encoded = content.encode("utf-8")
    return {"sha256": hashlib.sha256(encoded).hexdigest(), "bytes": len(encoded)}


def write_bundle(plan: LoadoutPlan, assessment: Assessment, output_dir: Path) -> None:
    """Write a new portable declared-loadout bundle and never overwrite a prior checklist."""
    output_path = Path(output_dir)
    if output_path.exists():
        raise FileExistsError(f"refusing to overwrite existing output: {output_path}")

    loadout_checklist = render_markdown(plan, assessment)
    loadout_items = render_csv(plan)
    boundary = PACKING_BOUNDARY if assessment.status == "needs-packing" else DECLARED_BOUNDARY
    manifest = {
        "schema_version": 1,
        "tool": "loadoutbook",
        "declared_status": assessment.status,
        "boundary": boundary,
        "loadout": {
            "title": plan.loadout.title,
            "project": plan.loadout.project,
            "requirements_basis": plan.loadout.requirements_basis,
        },
        "assessment": {
            "unpacked_item_ids": list(assessment.unpacked_item_ids),
            "unpacked_critical_item_ids": list(assessment.unpacked_critical_item_ids),
        },
        "artifacts": {
            "LOADOUT_CHECKLIST.md": artifact_record(loadout_checklist),
            "loadout-items.csv": artifact_record(loadout_items),
        },
    }

    output_path.mkdir(parents=True)
    (output_path / "LOADOUT_CHECKLIST.md").write_text(
        loadout_checklist,
        encoding="utf-8",
    )
    (output_path / "loadout-items.csv").write_text(loadout_items, encoding="utf-8")
    (output_path / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
