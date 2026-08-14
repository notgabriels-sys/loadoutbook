"""Command-line interface for offline declared Loadoutbook packing checklists."""

import argparse
import sys
import tomllib
from collections.abc import Sequence
from pathlib import Path

from loadoutbook.config import LoadoutPlan, load_plan
from loadoutbook.report import DECLARED_BOUNDARY, PACKING_BOUNDARY, write_bundle
from loadoutbook.service import Assessment, assess


def build_parser() -> argparse.ArgumentParser:
    """Build Loadoutbook's deliberately compact, physical-world-independent CLI."""
    parser = argparse.ArgumentParser(
        prog="loadoutbook",
        description="Validate and render a declared live-performance packing checklist.",
    )
    subcommands = parser.add_subparsers(dest="command", required=True)

    check = subcommands.add_parser(
        "check",
        help="read a declared loadout and report its packing-declaration status",
    )
    check.add_argument("plan", type=Path, help="path to a loadout TOML file")

    build = subcommands.add_parser(
        "build",
        help="write a new printable declared loadout checklist folder",
    )
    build.add_argument("plan", type=Path, help="path to a loadout TOML file")
    build.add_argument(
        "--output",
        "-o",
        type=Path,
        required=True,
        help="new output directory for Markdown, CSV, and manifest",
    )
    return parser


def load_declared_plan(path: Path) -> LoadoutPlan | None:
    """Load human-authored TOML and translate ordinary authoring errors for the CLI."""
    try:
        return load_plan(path)
    except (KeyError, OSError, TypeError, ValueError, tomllib.TOMLDecodeError) as error:
        print(f"loadoutbook: invalid plan: {error}", file=sys.stderr)
        return None


def render_status(plan: LoadoutPlan, assessment: Assessment) -> str:
    """Describe declared packing status without asserting physical item or transport readiness."""
    boundary = PACKING_BOUNDARY if assessment.status == "needs-packing" else DECLARED_BOUNDARY
    lines = [
        f"Declared status: {assessment.status}",
        f"Declared loadout items: {len(plan.items)}",
        f"Boundary: {boundary}",
    ]
    if assessment.unpacked_item_ids:
        lines.append("Unpacked declared items: " + ", ".join(assessment.unpacked_item_ids))
    if assessment.unpacked_critical_item_ids:
        lines.append(
            "Unpacked critical declared items: " + ", ".join(assessment.unpacked_critical_item_ids)
        )
    return "\n".join(lines)


def status_code(assessment: Assessment) -> int:
    """Return an attention exit status until every declared item is packed or not needed."""
    return 0 if assessment.status == "declared" else 2


def main(argv: Sequence[str] | None = None) -> int:
    """Run Loadoutbook without seeing, moving, packing, or transporting physical equipment."""
    arguments = build_parser().parse_args(argv)
    plan = load_declared_plan(arguments.plan)
    if plan is None:
        return 1

    assessment = assess(plan)
    if arguments.command == "check":
        print(render_status(plan, assessment))
        return status_code(assessment)

    try:
        write_bundle(plan, assessment, arguments.output)
    except OSError as error:
        print(f"loadoutbook: unable to write loadout bundle: {error}", file=sys.stderr)
        return 1
    print(render_status(plan, assessment))
    print(f"Wrote declared loadout bundle: {arguments.output}")
    return status_code(assessment)


if __name__ == "__main__":
    raise SystemExit(main())
