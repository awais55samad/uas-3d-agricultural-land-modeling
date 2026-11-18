"""Command-line interface: ``uas-land build|report|mesh``."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

from .terrain import build_grid, grid_to_obj, load_points


def _grid(args) -> object:
    points = load_points(args.csv)
    return build_grid(points, resolution=args.resolution)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="uas-land",
        description="3D agricultural land modeling from UAS survey points.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    for name, help_text in [
        ("build", "Build a grid CSV from survey points"),
        ("report", "Report slope and volume"),
        ("mesh", "Export an OBJ mesh"),
    ]:
        p = sub.add_parser(name, help=help_text)
        p.add_argument("--csv", required=True)
        p.add_argument("--resolution", required=True, type=float)
        if name == "build":
            p.add_argument("--out", required=True)
        if name == "report":
            p.add_argument("--reference", required=True, type=float)
        if name == "mesh":
            p.add_argument("--out", required=True)

    args = parser.parse_args(argv)
    try:
        grid = _grid(args)
        if args.command == "build":
            with open(args.out, "w", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle)
                writer.writerow(["row", "col", "x", "y", "z"])
                for r in range(grid.rows):
                    for c in range(grid.cols):
                        writer.writerow([r, c, grid.x0 + c * grid.cell, grid.y0 + r * grid.cell, grid.values[r][c]])
            print(f"grid {grid.rows}x{grid.cols} -> {args.out}")
        elif args.command == "report":
            slopes = grid.slope_degrees()
            flat = [v for row in slopes for v in row]
            print(f"grid {grid.rows}x{grid.cols}, cell {grid.cell} m")
            print(f"mean slope: {sum(flat) / len(flat):.2f} degrees, max slope: {max(flat):.2f} degrees")
            print(f"volume above {args.reference}: {grid.volume_above(args.reference):.1f} m^3")
            print(f"volume below {args.reference}: {grid.volume_below(args.reference):.1f} m^3")
        elif args.command == "mesh":
            Path(args.out).write_text(grid_to_obj(grid), encoding="utf-8")
            print(f"mesh -> {args.out}")
        return 0
    except (ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
