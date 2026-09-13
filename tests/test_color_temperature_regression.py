"""Regression test verifying color_temperature_k remains strictly within physical bounds [1000K, 40000K]
and accurately matches known photometric reference standards via McCamy's formula."""

import numpy as np
import pytest

from connectome_engine.simulation.visual_transduction import (
    VisualTransductionEngine,
    compute_mccamy_cct,
)


def test_color_temperature_photometric_literature_references():
    """Verify that standardized photometric color stimuli produce CCT matching literature benchmarks.

    Literature references:
    - Standard CIE D65 Daylight: ~6504 K
    - Incandescent tungsten lamp (domestic warm white): 2700 K - 3000 K (Illuminant A is 2856 K)
    - Clear daylight sky blue: 10,000 K - 20,000 K
    - Neutral baseline in total darkness: 6,500 K
    """
    engine = VisualTransductionEngine(num_r1_r6=50, num_r8=20, num_looming_lc4=10)

    # 1. D65 Standard Daylight (Pure White #FFFFFF) -> ~6504 K
    white_frame = np.full((160, 90, 4), [255, 255, 255, 255], dtype=np.uint8)
    t_white = engine.process_frame(white_frame)
    assert 6400.0 <= t_white.color_temperature_k <= 6600.0, (
        f"D65 white produced {t_white.color_temperature_k} K, expected ~6504 K"
    )

    # 2. Incandescent domestic warm lamp (#FFB46B, RGB 255, 180, 107) -> 2700 K - 3000 K
    incandescent_frame = np.full((160, 90, 4), [255, 180, 107, 255], dtype=np.uint8)
    t_inc = engine.process_frame(incandescent_frame)
    assert 2700.0 <= t_inc.color_temperature_k <= 3000.0, (
        f"Incandescent stimulus produced {t_inc.color_temperature_k} K, expected [2700, 3000] K"
    )

    # 3. Daylight Sky Blue (#87CEEB, RGB 135, 206, 235) -> 10,000 K - 20,000 K
    sky_frame = np.full((160, 90, 4), [135, 206, 235, 255], dtype=np.uint8)
    t_sky = engine.process_frame(sky_frame)
    assert 10000.0 <= t_sky.color_temperature_k <= 20000.0, (
        f"Sky blue stimulus produced {t_sky.color_temperature_k} K, expected [10000, 20000] K"
    )

    # 4. Total darkness (#000000) -> 6500.0 K neutral reference baseline
    dark_frame = np.full((160, 90, 4), [0, 0, 0, 255], dtype=np.uint8)
    t_dark = engine.process_frame(dark_frame)
    assert t_dark.color_temperature_k == 6500.0, (
        f"Darkness produced {t_dark.color_temperature_k} K, expected 6500.0 K"
    )


def test_color_temperature_physical_bounds_standard_stimuli():
    """Verify that standard stimuli (white, red, blue, green, black) yield physical CCT values."""
    engine = VisualTransductionEngine(num_r1_r6=50, num_r8=20, num_looming_lc4=10)

    stimuli = [
        ("Pure White", [255, 255, 255, 255]),
        ("Pure Red", [200, 0, 0, 255]),
        ("Pure Blue", [0, 0, 230, 255]),
        ("Pure Green", [0, 230, 0, 255]),
        ("Pure Black", [0, 0, 0, 255]),
        ("Deep Amber / Low Red", [20, 0, 0, 255]),
        ("Deep Cyan", [0, 180, 255, 255]),
        ("Near Black with Trace Blue", [0, 0, 1, 255]),
    ]

    for name, color in stimuli:
        frame = np.full((160, 90, 4), color, dtype=np.uint8)
        telemetry = engine.process_frame(frame)
        cct = telemetry.color_temperature_k

        assert 1000.0 <= cct <= 40000.0, f"Stimulus '{name}' produced CCT {cct} K outside [1000, 40000]"


def test_color_temperature_physical_bounds_random_rgb_matrices():
    """Verify that 100 random RGB frames never produce explosive/negative color temperatures."""
    engine = VisualTransductionEngine(num_r1_r6=50, num_r8=20, num_looming_lc4=10)
    rng = np.random.default_rng(seed=42)

    for i in range(100):
        frame = rng.integers(0, 256, size=(160, 90, 4), dtype=np.uint8)
        telemetry = engine.process_frame(frame)
        cct = telemetry.color_temperature_k

        assert 1000.0 <= cct <= 40000.0, f"Random frame {i} produced out-of-bounds CCT {cct} K"


def test_color_temperature_planckian_duv_and_validity():
    """Verify that Planckian locus deviation Duv identifies non-correlated saturated colors."""
    engine = VisualTransductionEngine(num_r1_r6=50, num_r8=20, num_looming_lc4=10)

    # 1. Authentic Planckian/Daylight colors: |Duv| <= 0.05 -> cct_valid = True
    cct_w, duv_w, valid_w = compute_mccamy_cct(1.0, 1.0, 1.0, return_metrics=True)
    assert valid_w is True, f"Pure White should be valid, got valid={valid_w}, Duv={duv_w}"
    assert abs(duv_w) <= 0.01, f"Pure White Duv should be near zero, got {duv_w}"

    cct_inc, duv_inc, valid_inc = compute_mccamy_cct(1.0, 180 / 255, 107 / 255, return_metrics=True)
    assert valid_inc is True, f"Incandescent should be valid, got valid={valid_inc}, Duv={duv_inc}"
    assert abs(duv_inc) <= 0.02, f"Incandescent Duv should be near zero, got {duv_inc}"

    cct_sky, duv_sky, valid_sky = compute_mccamy_cct(135 / 255, 206 / 255, 235 / 255, return_metrics=True)
    assert valid_sky is True, f"Sky Blue should be valid, got valid={valid_sky}, Duv={duv_sky}"
    assert abs(duv_sky) <= 0.05, f"Sky Blue Duv should be <= 0.05, got {duv_sky}"

    # 2. Pure saturated monochromatic / gamut corner colors: |Duv| > 0.05 -> cct_valid = False
    # Pure Blue (#0000E6, RGB 0, 0, 230): extreme blue corner far below Planckian locus
    cct_b, duv_b, valid_b = compute_mccamy_cct(0.0, 0.0, 230 / 255, return_metrics=True)
    assert valid_b is False, f"Pure Blue should be marked invalid (|Duv| > 0.05), got valid={valid_b}"
    assert duv_b < -0.20, f"Pure Blue should have large negative Duv (below locus), got {duv_b}"

    # Pure Red (#C80000, RGB 200, 0, 0): saturated red
    cct_r, duv_r, valid_r = compute_mccamy_cct(200 / 255, 0.0, 0.0, return_metrics=True)
    assert valid_r is False, f"Pure Red should be marked invalid (|Duv| > 0.05), got valid={valid_r}"
    assert abs(duv_r) > 0.10, f"Pure Red should have large Duv, got {duv_r}"

    # Pure Green (#00E600, RGB 0, 230, 0): saturated green (high above locus)
    cct_g, duv_g, valid_g = compute_mccamy_cct(0.0, 230 / 255, 0.0, return_metrics=True)
    assert valid_g is False, f"Pure Green should be marked invalid (|Duv| > 0.05), got valid={valid_g}"
    assert duv_g > 0.05, f"Pure Green should have positive Duv > 0.05 (above locus), got {duv_g}"

    # 3. Engine frame integration telemetry check
    blue_frame = np.full((160, 90, 4), [0, 0, 230, 255], dtype=np.uint8)
    t_blue = engine.process_frame(blue_frame)
    assert t_blue.cct_valid is False
    assert t_blue.cct_duv < -0.20

    white_frame = np.full((160, 90, 4), [255, 255, 255, 255], dtype=np.uint8)
    t_white = engine.process_frame(white_frame)
    assert t_white.cct_valid is True
    assert abs(t_white.cct_duv) <= 0.01


