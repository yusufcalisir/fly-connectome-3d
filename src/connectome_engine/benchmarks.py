"""Empirical benchmark generator and validator for FlyConnectome 3D (Janelia MaleCNS v1.0).

Executes calibrated reference stimuli from isolated cold-starts and records
exact biophysical network telemetry to reproduce the README empirical benchmark table.
"""

import json

import numpy as np

from connectome_engine.brain import ConnectomeBrain
from connectome_engine.config import DATA_DIR, ROOT_DIR
from connectome_engine.data.circuits import load_malecns_v1_connectome

BENCHMARK_SCENARIOS = [
    {
        "name": "Pure White",
        "hex": "#FFFFFF",
        "rgba": (255, 255, 255, 255),
        "is_looming_transition": False,
    },
    {
        "name": "Pure Red",
        "hex": "#C80000",
        "rgba": (200, 0, 0, 255),
        "is_looming_transition": False,
    },
    {
        "name": "Pure Blue",
        "hex": "#0000E6",
        "rgba": (0, 0, 230, 255),
        "is_looming_transition": False,
    },
    {
        "name": "Rapid Dark / Looming",
        "hex": "#000000",
        "rgba": (0, 0, 0, 255),
        "is_looming_transition": True,
    },
]


def run_benchmarks() -> dict:
    """Execute all benchmark scenarios on isolated cold-start ConnectomeBrain instances."""
    graph_path = DATA_DIR / "malecns_v1_graph.npz"
    if not graph_path.exists():
        raise FileNotFoundError(f"Missing connectome graph at {graph_path}")

    print("[*] Loading Janelia MaleCNS v1.0 connectome graph...")
    n_nodes, adj, circuits, _ = load_malecns_v1_connectome(DATA_DIR)
    print(f"    Loaded {n_nodes:,} neurons, {adj.nnz:,} synapses.")

    results = {}

    for sc in BENCHMARK_SCENARIOS:
        # Guarantee a FRESH, isolated cold-start brain for each scenario
        brain = ConnectomeBrain(n_nodes, adj, circuits)
        duration_ms = 50.0

        if sc["is_looming_transition"]:
            # Baseline ambient light frame establishes pre-threat optical reference
            baseline_frame = np.full((160, 90, 4), 220, dtype=np.uint8)
            brain.observe_frame(baseline_frame, duration_ms=50.0)
            # Re-zero accumulated spike counters and simulation time so only the 50ms looming chunk is measured
            brain.snn.total_spikes_accumulated = 0
            brain.snn.total_sim_ms = 0.0

        frame = np.full((160, 90, 4), sc["rgba"], dtype=np.uint8)
        telemetry = brain.observe_frame(frame, duration_ms=duration_ms)

        res_entry = {
            "name": sc["name"],
            "hex": sc["hex"],
            "mean_luminance": round(float(telemetry.mean_luminance), 4),
            "color_temperature_k": round(float(telemetry.color_temperature_k), 1),
            "cct_duv": round(float(getattr(telemetry, "cct_duv", 0.0)), 4),
            "cct_valid": bool(getattr(telemetry, "cct_valid", True)),
            "total_spikes": int(telemetry.total_spikes),
            "mean_firing_rate_hz": round(float(telemetry.mean_firing_rate_hz), 2),
            "looming_threat_detected": bool(telemetry.looming_threat_detected),
            "giant_fiber_jump": bool(telemetry.giant_fiber_jump),
            "excitatory_spikes": int(telemetry.excitatory_spikes),
            "inhibitory_spikes": int(telemetry.inhibitory_spikes),
        }

        if sc["name"] == "Rapid Dark / Looming":
            spectrum_desc = "Contrast drop (Darkness baseline 6,500 K)"
        elif res_entry["cct_valid"]:
            spectrum_desc = f"Broad spectrum (~{res_entry['color_temperature_k']:,.0f} K, valid Planckian CCT)"
        else:
            wavelength = "Long wavelength" if "Red" in sc["name"] else "Short wavelength"
            spectrum_desc = f"{wavelength} (N/A — saturated color, not a blackbody-correlated temperature)"

        res_entry["dominant_spectrum"] = spectrum_desc
        res_entry["cct_status"] = (
            f"Valid CCT (Duv={res_entry['cct_duv']:+.4f})"
            if res_entry["cct_valid"]
            else f"N/A — saturated color (|Duv|={abs(res_entry['cct_duv']):.4f} > 0.05)"
        )
        results[sc["name"]] = res_entry

    return results


def main():
    """CLI execution for generating benchmarks and persisting output JSON."""
    results = run_benchmarks()

    print("\n" + "=" * 115)
    print("FLYCONNECTOME 3D — EMPIRICAL BENCHMARKS OUTPUT (Janelia MaleCNS v1.0)")
    print("=" * 115)
    header = f"{'Visual Stimulus':<24} | {'Lum (Y)':<9} | {'CCT (K)':<11} | {'CCT Status (|Duv| <= 0.05)':<38} | {'Spikes':<8} | {'Rate Hz':<8} | {'Looming'}"
    print(header)
    print("-" * 115)

    for d in results.values():
        cct_str = f"{d['color_temperature_k']:.1f} K"
        row = f"{d['name'] + ' (' + d['hex'] + ')':<24} | {d['mean_luminance']:<9.4f} | {cct_str:<11} | {d['cct_status']:<38} | {d['total_spikes']:<8,d} | {d['mean_firing_rate_hz']:<8.2f} | {d['looming_threat_detected']!s}"
        print(row)
    print("=" * 115 + "\n")

    # Output JSON file
    out_path = ROOT_DIR / "benchmarks_output.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"[+] Saved complete benchmark payload to {out_path}")


if __name__ == "__main__":
    main()
