# 📐 RDM Beams – Python Library for Structural Analysis

A complete Python library for analyzing statically determinate beams in Strength of Materials (RDM). It computes internal forces, support reactions, and generates professional diagrams.

## 🚀 Features

### 📊 Supported Beam Types
- ✅ **Beams with two simple supports** — Classical statically determinate beams
- ✅ **Cantilever beams** — Fixed at the left or right end
- ✅ **Beams with simple support + roller** — With overhang

### ⚖️ Load Types
- ✅ **Point loads** — Vertical forces (positive downward)
- ✅ **Distributed loads** — Uniform over a given interval
- ✅ **Concentrated moments** — Couples (positive counterclockwise)

### 📈 Structural Calculations (RDM)
- ✅ **Support reactions** — Automatically calculated
- ✅ **Shear force V(x)** — Full diagram with critical values
- ✅ **Bending moment M(x)** — Diagram with extrema identification
- ✅ **Axial force N(x)** — Ready for future extensions

### 🎨 Visualization
- ✅ **Professional diagrams** — Using matplotlib for high-quality output
- ✅ **Beam and loads** — Graphical representation of the structural system
- ✅ **Key points** — Zeros and extrema automatically identified
- ✅ **CSV export** — Export results for further analysis

## 📋 Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

## 🔧 Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/rdm-beams.git
cd rdm-beams
