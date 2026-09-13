#!/usr/bin/env python3
"""CLI entrypoint to generate empirical benchmarks for FlyConnectome 3D.

Executes calibrated reference stimuli from isolated cold-starts and records
exact biophysical network telemetry to reproduce the README empirical benchmark table.
"""

import sys
from pathlib import Path

# Ensure project src is in sys.path
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR / "src") not in sys.path:
    sys.path.insert(0, str(ROOT_DIR / "src"))

from connectome_engine.benchmarks import main

if __name__ == "__main__":
    main()
