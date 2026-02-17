📐 RDM Beams – Python Library for Structural Analysis

A complete Python library for analyzing statically determinate beams in Strength of Materials (RDM).
It computes internal forces, support reactions, and generates diagrams.

🚀 Features
📊 Supported Beam Types

✅ Beams with two simple supports — Classical statically determinate beams
✅ Cantilever beams — Fixed at the left or right end
✅ Beams with simple support + roller — With overhang

⚖️ Load Types

✅ Point loads — Vertical forces (positive downward)
✅ Distributed loads — Uniform over a given interval
✅ Concentrated moments — Couples (positive counterclockwise)

📈 Structural Calculations (RDM)

✅ Support reactions — Automatically calculated
✅ Shear force V(x) — Full diagram
✅ Bending moment M(x) — Diagram with extrema
✅ Axial force N(x) — For future extensions

🎨 Visualization

✅ Professional diagrams — Using matplotlib
✅ Beam and loads — Graphical representation
✅ Key points — Zeros and extrema identified
✅ CSV export

Prerequisites

Python 3.7 or higher

pip (Python package manager)

Installing Dependencies
pip install numpy matplotlib
