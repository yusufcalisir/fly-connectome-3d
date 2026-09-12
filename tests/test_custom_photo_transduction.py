"""Unit and integration tests for custom photo visual transduction and spectral valence."""

import numpy as np
from PIL import Image

from connectome_engine.simulation.visual_transduction import VisualTransductionEngine


def test_custom_appetitive_photo_transduction():
    """Verify that a high-red sugary photo elevates chromatic R8 photoreceptor currents."""
    engine = VisualTransductionEngine(num_r1_r6=80, num_r8=40, num_looming_lc4=30)

    # Synthetic high-red sugary fruit photo (160x90 RGBA)
    img = np.zeros((160, 90, 4), dtype=np.uint8)
    img[:, :, 0] = 230  # High Red
    img[:, :, 1] = 40   # Low Green
    img[:, :, 2] = 50   # Low Blue
    img[:, :, 3] = 255

    telemetry = engine.process_frame(img)

    assert len(telemetry.r1_r6_currents) == 80
    assert len(telemetry.r8_currents) == 40
    # In VisualTransductionEngine, chromatic R8 responds to color ratios
    assert np.mean(telemetry.r8_currents) > 0.05
    # Looming should not trigger on a static frame
    assert not telemetry.looming_threat_detected
    assert np.max(telemetry.looming_currents) == 0.0


def test_custom_looming_shadow_photo_series():
    """Verify that an expanding dark shadow series triggers LC4 looming currents."""
    engine = VisualTransductionEngine(num_r1_r6=80, num_r8=40, num_looming_lc4=30)

    # Frame 1: Bright arena with tiny dark center
    f1 = np.full((160, 90, 4), 240, dtype=np.uint8)
    f1[75:85, 40:50, :3] = 10

    # Frame 2: Expanding dark shadow covering 70% of screen
    f2 = np.full((160, 90, 4), 240, dtype=np.uint8)
    f2[30:130, 15:75, :3] = 10

    engine.process_frame(f1)
    telemetry2 = engine.process_frame(f2)

    # Expanding dark shadow must inject current into LC4 threat circuit
    assert telemetry2.looming_threat_detected is True
    assert np.max(telemetry2.looming_currents) > 0.0
