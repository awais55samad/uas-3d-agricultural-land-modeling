# UAS 3D Agricultural Land Modeling

Three-dimensional agricultural land modeling from unmanned aerial system
(UAS) survey points — terrain grid, slope and volume estimation.

This is an **original, independent implementation inspired by** the 2019
paper *“Three dimensional agricultural land modeling using unmanned aerial
system (UAS)”*. It is **not** the official code from that paper, and it
does not claim to reproduce its results. It implements the core idea in a
small, readable form: scattered UAS survey points (x, y, elevation) are
interpolated onto a regular grid, from which slope and cut/fill volume
against a reference level can be estimated.

## What it does

- Loads survey points from CSV (`x,y,z`, metres).
- Interpolates them onto a regular grid with inverse-distance weighting.
- Computes slope (degrees) for every grid cell.
- Estimates volume above / below a reference elevation.
- Exports the grid as CSV and as a Wavefront OBJ mesh.
- Ships with a command-line tool and tests. No drone, no GIS library,
  and no external service are required.

## Quick start

```bash
python3 -m pip install -e .
python3 examples/demo.py
```

### Command line

```bash
# Build a grid from survey points
uas-land build --csv examples/sample_points.csv --out grid.csv --resolution 5

# Report slope and volume
uas-land report --csv examples/sample_points.csv --resolution 5 --reference 100.0

# Export an OBJ mesh
uas-land mesh --csv examples/sample_points.csv --resolution 5 --out land.obj
```

CSV columns: `x,y,z` — all in metres, same coordinate system.

## Project layout

```
src/uas_land/
  terrain.py  # Point, Grid, interpolation, slope, volume
  cli.py      # Command-line interface
examples/
  sample_points.csv
  demo.py
tests/
  test_terrain.py
```

## Tests

```bash
python3 -m pytest -q
# or, without pytest:
python3 -m unittest discover -s tests -v
```

## Author

**Engr. Muhammad Awais Khan** — Bahauddin Zakariya University, Multan (Pakistan)

Google Scholar profile: https://scholar.google.com/citations?hl=en&user=c4UawvgAAAAJ

## Status

Experimental research code, version 0.1.0. It is a teaching and
prototyping implementation, not a production surveying tool, and it has
not been validated against survey-grade data.

## License

MIT — see `LICENSE`.
