"""Unit tests for visual transduction and looming threat detection."""

import numpy as np

from connectome_engine.simulation.visual_transduction import VisualTransductionEngine


def test_visual_looming_shadow_detection():
    """Verify that an expanding dark circle triggers the innate looming alarm."""
    engine = VisualTransductionEngine(num_r1_r6=500, num_r8=200, num_looming_lc4=32)

    # Frame 1: Bright uniform background
    bright_frame = np.full((160, 90, 4), 220, dtype=np.uint8)
    t1 = engine.process_frame(bright_frame)
    assert not t1.looming_threat_detected

    # Frame 2: Expanding dark circle in the center (approaching swatter/predator)
    looming_frame = bright_frame.copy()
    cy, cx = 80, 45
    radius = 35
    y, x = np.ogrid[:160, :90]
    mask = ((y - cy) ** 2 + (x - cx) ** 2) <= radius ** 2
    looming_frame[mask] = 10  # Dark shadow

    t2 = engine.process_frame(looming_frame)
    assert t2.looming_threat_detected
    assert t2.looming_expansion_rate > 0.0
    assert np.any(t2.looming_currents > 0.0)


def test_static_frame_no_looming():
    """Verify that a steady static frame does not trigger false threat alarms."""
    engine = VisualTransductionEngine(num_r1_r6=100, num_r8=50, num_looming_lc4=10)
    frame = np.full((160, 90, 4), 128, dtype=np.uint8)

    _ = engine.process_frame(frame)
    t2 = engine.process_frame(frame)

    assert not t2.looming_threat_detected
    assert t2.looming_expansion_rate == 0.0
