import unittest
from pathlib import Path

from uas_land import build_grid, grid_to_obj, load_points

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"


class TestTerrain(unittest.TestCase):
    def test_load_points(self):
        points = load_points(EXAMPLES / "sample_points.csv")
        self.assertEqual(len(points), 9)

    def test_grid_at_survey_point(self):
        points = load_points(EXAMPLES / "sample_points.csv")
        grid = build_grid(points, resolution=10.0)
        # A grid node exactly on a survey point reproduces its elevation.
        self.assertAlmostEqual(grid.values[0][0], 100.0, places=6)

    def test_flat_terrain_zero_slope(self):
        from uas_land import Point

        flat = [Point(x, y, 50.0) for x in (0, 10, 20) for y in (0, 10, 20)]
        grid = build_grid(flat, resolution=10.0)
        slopes = grid.slope_degrees()
        self.assertTrue(all(v == 0.0 for row in slopes for v in row))

    def test_volume(self):
        from uas_land import Point

        flat = [Point(x, y, 102.0) for x in (0, 10, 20) for y in (0, 10, 20)]
        grid = build_grid(flat, resolution=10.0)
        # 3x3 cells of 100 m^2, 2 m above reference 100.
        self.assertAlmostEqual(grid.volume_above(100.0), 9 * 100 * 2, places=6)
        self.assertAlmostEqual(grid.volume_below(100.0), 0.0, places=6)

    def test_obj_export(self):
        points = load_points(EXAMPLES / "sample_points.csv")
        grid = build_grid(points, resolution=10.0)
        obj = grid_to_obj(grid)
        self.assertIn("v ", obj)
        self.assertIn("f ", obj)


if __name__ == "__main__":
    unittest.main()
