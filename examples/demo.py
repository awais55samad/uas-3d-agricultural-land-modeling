"""Demo: build a terrain grid from the sample UAS survey points."""

from pathlib import Path

from uas_land import build_grid, load_points

ROOT = Path(__file__).resolve().parent


def main() -> None:
    points = load_points(ROOT / "sample_points.csv")
    grid = build_grid(points, resolution=10.0)
    slopes = grid.slope_degrees()
    flat = [v for row in slopes for v in row]
    print(f"grid {grid.rows}x{grid.cols}, cell {grid.cell} m")
    print(f"mean slope: {sum(flat) / len(flat):.2f} degrees")
    print(f"volume above 100 m: {grid.volume_above(100.0):.1f} m^3")


if __name__ == "__main__":
    main()
