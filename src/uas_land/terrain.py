"""3D terrain modeling from scattered UAS survey points.

Points are interpolated onto a regular grid with inverse-distance
weighting (IDW, power 2). Slope is the steepest gradient from finite
differences, and volume is estimated against a reference elevation
using the trapezoidal rule over grid cells.
"""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Point:
    x: float
    y: float
    z: float


@dataclass
class Grid:
    """A regular grid of elevations."""

    x0: float
    y0: float
    cell: float
    rows: int
    cols: int
    values: list[list[float]]  # values[row][col], row = y, col = x

    def slope_degrees(self) -> list[list[float]]:
        """Slope in degrees for every cell, by central differences."""
        out: list[list[float]] = []
        for r in range(self.rows):
            row: list[float] = []
            for c in range(self.cols):
                left = self.values[r][c - 1] if c > 0 else self.values[r][c]
                right = self.values[r][c + 1] if c < self.cols - 1 else self.values[r][c]
                down = self.values[r - 1][c] if r > 0 else self.values[r][c]
                up = self.values[r + 1][c] if r < self.rows - 1 else self.values[r][c]
                dz_dx = (right - left) / (2 * self.cell) if self.cols > 1 else 0.0
                dz_dy = (up - down) / (2 * self.cell) if self.rows > 1 else 0.0
                row.append(math.degrees(math.atan(math.hypot(dz_dx, dz_dy))))
            out.append(row)
        return out

    def volume_above(self, reference: float) -> float:
        """Volume (m^3) of terrain above a reference elevation."""
        total = 0.0
        for row in self.values:
            for z in row:
                total += max(0.0, z - reference)
        return total * self.cell * self.cell

    def volume_below(self, reference: float) -> float:
        """Volume (m^3) of terrain below a reference elevation."""
        total = 0.0
        for row in self.values:
            for z in row:
                total += max(0.0, reference - z)
        return total * self.cell * self.cell


def load_points(path: str | Path) -> list[Point]:
    """Load survey points from a CSV with columns ``x,y,z``."""
    points: list[Point] = []
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or not {"x", "y", "z"}.issubset(reader.fieldnames):
            raise ValueError("CSV must have columns: x,y,z")
        for line_no, row in enumerate(reader, start=2):
            try:
                points.append(Point(float(row["x"]), float(row["y"]), float(row["z"])))
            except (ValueError, KeyError) as exc:
                raise ValueError(f"CSV line {line_no}: {exc}") from exc
    if len(points) < 4:
        raise ValueError("need at least 4 survey points")
    return points


def build_grid(points: list[Point], resolution: float) -> Grid:
    """Interpolate points onto a regular grid with IDW (power 2)."""
    if resolution <= 0:
        raise ValueError("resolution must be positive")
    xs = [p.x for p in points]
    ys = [p.y for p in points]
    x0, x1 = min(xs), max(xs)
    y0, y1 = min(ys), max(ys)
    cols = max(2, int((x1 - x0) / resolution) + 1)
    rows = max(2, int((y1 - y0) / resolution) + 1)

    values: list[list[float]] = []
    for r in range(rows):
        y = y0 + r * resolution
        row: list[float] = []
        for c in range(cols):
            x = x0 + c * resolution
            numerator = 0.0
            denominator = 0.0
            for p in points:
                dist2 = (x - p.x) ** 2 + (y - p.y) ** 2
                if dist2 == 0.0:
                    numerator = p.z
                    denominator = 1.0
                    break
                weight = 1.0 / dist2
                numerator += weight * p.z
                denominator += weight
            row.append(numerator / denominator)
        values.append(row)
    return Grid(x0=x0, y0=y0, cell=resolution, rows=rows, cols=cols, values=values)


def grid_to_obj(grid: Grid) -> str:
    """Export the grid as a Wavefront OBJ mesh (vertices + faces)."""
    lines: list[str] = []
    for r in range(grid.rows):
        for c in range(grid.cols):
            x = grid.x0 + c * grid.cell
            y = grid.y0 + r * grid.cell
            lines.append(f"v {x:.3f} {y:.3f} {grid.values[r][c]:.3f}")
    for r in range(grid.rows - 1):
        for c in range(grid.cols - 1):
            a = r * grid.cols + c + 1
            b = a + 1
            d = (r + 1) * grid.cols + c + 1
            e = d + 1
            lines.append(f"f {a} {b} {e}")
            lines.append(f"f {a} {e} {d}")
    return "\n".join(lines) + "\n"
