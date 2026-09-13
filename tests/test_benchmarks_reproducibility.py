"""Reproducibility test validating that simulated connectome benchmarks match published README values."""

import re
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parents[1]

from connectome_engine.benchmarks import run_benchmarks
from connectome_engine.config import DATA_DIR


def _parse_readme_benchmarks() -> dict[str, dict]:
    readme_path = ROOT_DIR / "README.md"
    content = readme_path.read_text(encoding="utf-8")

    # Match rows: | **Pure White** (`#FFFFFF`) | 1.000 | Broad spectrum (~6,504 K, valid Planckian CCT) | 25,578 | 3.07 Hz | ❌ Inactive | ...
    pattern = re.compile(
        r"\|\s*\*\*([^*]+)\*\*\s*\(`([^`]+)`\)\s*\|\s*([\d.]+)\s*\|\s*([^|]+)\|\s*([\d,]+)\s*\|\s*([\d.]+)\s*Hz\s*\|\s*([^|]+)\|"
    )

    rows = {}
    for match in pattern.finditer(content):
        name = match.group(1).strip()
        hex_code = match.group(2).strip()
        lum = float(match.group(3).strip())
        spectrum = match.group(4).strip()
        spikes = int(match.group(5).replace(",", "").strip())
        rate = float(match.group(6).strip())
        looming_str = match.group(7).strip()
        looming = "Active" in looming_str or "True" in looming_str

        rows[name] = {
            "hex": hex_code,
            "luminance": lum,
            "dominant_spectrum": spectrum,
            "spikes": spikes,
            "rate_hz": rate,
            "looming": looming,
        }
    return rows


def test_benchmarks_reproducibility_against_readme():
    """Verify that live simulation reproduces README published values within ±5% tolerance."""
    graph_path = DATA_DIR / "malecns_v1_graph.npz"
    if not graph_path.exists():
        pytest.skip("MaleCNS v1.0 graph file not found, skipping benchmark verification.")

    readme_table = _parse_readme_benchmarks()
    assert len(readme_table) == 4, f"Expected 4 benchmark rows in README, found {len(readme_table)}: {list(readme_table.keys())}"

    sim_results = run_benchmarks()

    for name, table_vals in readme_table.items():
        assert name in sim_results, f"Scenario '{name}' from README missing in simulation results"
        sim = sim_results[name]

        # 1. Total spikes (±5% tolerance)
        table_spikes = table_vals["spikes"]
        sim_spikes = sim["total_spikes"]
        if table_spikes == 0:
            assert sim_spikes == 0, f"Expected 0 spikes for {name}, got {sim_spikes}"
        else:
            rel_diff = abs(sim_spikes - table_spikes) / table_spikes
            assert rel_diff <= 0.05, (
                f"{name} spikes diverged from README by {rel_diff*100:.2f}% (README: {table_spikes:,}, Sim: {sim_spikes:,})"
            )

        # 2. Mean firing rate (±0.1 Hz or ±5%)
        table_rate = table_vals["rate_hz"]
        sim_rate = sim["mean_firing_rate_hz"]
        assert abs(sim_rate - table_rate) <= max(0.1, 0.05 * table_rate), (
            f"{name} firing rate diverged (README: {table_rate} Hz, Sim: {sim_rate} Hz)"
        )

        # 3. Looming threat boolean
        assert sim["looming_threat_detected"] == table_vals["looming"], (
            f"{name} looming trigger mismatch: README={table_vals['looming']}, Sim={sim['looming_threat_detected']}"
        )

        # 4. Dominant Spectrum & CCT Validity Verification
        table_spectrum = table_vals["dominant_spectrum"]
        if not sim["cct_valid"]:
            assert "N/A" in table_spectrum and "saturated color" in table_spectrum, (
                f"{name} has cct_valid=False, so README dominant spectrum must indicate N/A saturated color. "
                f"Found: '{table_spectrum}'"
            )
        elif name != "Rapid Dark / Looming":
            assert "valid Planckian CCT" in table_spectrum or "6,504 K" in table_spectrum, (
                f"{name} has cct_valid=True, so README dominant spectrum must indicate valid CCT. "
                f"Found: '{table_spectrum}'"
            )
