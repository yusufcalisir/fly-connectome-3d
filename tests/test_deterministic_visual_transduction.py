"""Deterministic tests for retinotopic visual transduction without random numbers.

Zero mock, zero random numbers. Validates spatial hemifield isolation,
directional contrast asymmetry, and exact biophysical current generation.
"""

import numpy as np

from connectome_engine.simulation.visual_transduction import (
    VisualTransductionEngine,
)


def test_zero_randomness_reproducibility():
    """Verify that multiple engine initializations produce bit-for-bit identical coordinates."""
    eng1 = VisualTransductionEngine(num_r1_r6_left=1112, num_r1_r6_right=2265, num_r8_left=625, num_r8_right=704)
    eng2 = VisualTransductionEngine(num_r1_r6_left=1112, num_r1_r6_right=2265, num_r8_left=625, num_r8_right=704)

    assert np.array_equal(eng1.r1_r6_l_x, eng2.r1_r6_l_x)
    assert np.array_equal(eng1.r1_r6_l_y, eng2.r1_r6_l_y)
    assert np.array_equal(eng1.r1_r6_r_x, eng2.r1_r6_r_x)
    assert np.array_equal(eng1.r1_r6_r_y, eng2.r1_r6_r_y)
    assert np.array_equal(eng1.r1_r6_x, eng2.r1_r6_x)
    assert np.array_equal(eng1.r1_r6_y, eng2.r1_r6_y)


def test_spatial_hemifield_isolation():
    """Verify that left eye never samples right pixels, and right eye never samples left pixels."""
    mid_x = 45  # for 90 width
    eng = VisualTransductionEngine(num_r1_r6_left=1112, num_r1_r6_right=2265, num_r8_left=625, num_r8_right=704)

    # Left eye photoreceptors (must all be < mid_x)
    assert np.all(eng.r1_r6_l_x >= 0)
    assert np.all(eng.r1_r6_l_x < mid_x)
    assert np.all(eng.r8_l_x >= 0)
    assert np.all(eng.r8_l_x < mid_x)

    # Right eye photoreceptors (must all be >= mid_x and < width)
    assert np.all(eng.r1_r6_r_x >= mid_x)
    assert np.all(eng.r1_r6_r_x < eng.width)
    assert np.all(eng.r8_r_x >= mid_x)
    assert np.all(eng.r8_r_x < eng.width)

    # Elevation coordinates within frame bounds
    assert np.all(eng.r1_r6_y >= 0)
    assert np.all(eng.r1_r6_y < eng.height)
    assert np.all(eng.r8_y >= 0)
    assert np.all(eng.r8_y < eng.height)


def test_left_illuminated_asymmetry():
    """Verify pure left illumination drives left photoreceptors and produces negative asymmetry."""
    eng = VisualTransductionEngine(num_r1_r6_left=1112, num_r1_r6_right=2265, num_r8_left=625, num_r8_right=704)

    # Frame: Left half 255 (white), Right half 0 (black)
    frame = np.zeros((160, 90, 4), dtype=np.uint8)
    frame[:, :45, :3] = 255
    frame[:, :, 3] = 255

    tel = eng.process_frame(frame)

    assert tel.left_luminance > 0.99
    assert tel.right_luminance < 0.01
    assert tel.hemispheric_asymmetry < -0.95, f"Expected near -1.0, got {tel.hemispheric_asymmetry}"

    # Injected currents
    assert tel.r1_r6_left_currents.mean() > 3.9
    assert np.all(tel.r1_r6_right_currents == 0.0)
    assert tel.r8_left_currents.mean() > 3.4
    assert np.all(tel.r8_right_currents == 0.0)


def test_right_illuminated_asymmetry():
    """Verify pure right illumination drives right photoreceptors and produces positive asymmetry."""
    eng = VisualTransductionEngine(num_r1_r6_left=1112, num_r1_r6_right=2265, num_r8_left=625, num_r8_right=704)

    # Frame: Right half 255 (white), Left half 0 (black)
    frame = np.zeros((160, 90, 4), dtype=np.uint8)
    frame[:, 45:, :3] = 255
    frame[:, :, 3] = 255

    tel = eng.process_frame(frame)

    assert tel.right_luminance > 0.99
    assert tel.left_luminance < 0.01
    assert tel.hemispheric_asymmetry > 0.95, f"Expected near +1.0, got {tel.hemispheric_asymmetry}"

    # Injected currents
    assert tel.r1_r6_right_currents.mean() > 3.9
    assert np.all(tel.r1_r6_left_currents == 0.0)
    assert tel.r8_right_currents.mean() > 3.4
    assert np.all(tel.r8_left_currents == 0.0)


def test_symmetric_illumination():
    """Verify balanced illumination produces neutral asymmetry near 0.0."""
    eng = VisualTransductionEngine(num_r1_r6_left=1112, num_r1_r6_right=2265, num_r8_left=625, num_r8_right=704)

    # Homogeneous 50% gray frame
    frame = np.full((160, 90, 4), 128, dtype=np.uint8)
    frame[:, :, 3] = 255

    tel = eng.process_frame(frame)

    assert abs(tel.left_luminance - tel.right_luminance) < 1e-4
    assert abs(tel.hemispheric_asymmetry) < 1e-3
    assert abs(tel.r1_r6_left_currents.mean() - tel.r1_r6_right_currents.mean()) < 0.05


def test_backward_compatibility_legacy_init():
    """Verify legacy single num_r1_r6 and num_r8 initialization remains supported."""
    eng = VisualTransductionEngine(num_r1_r6=3335, num_r8=811)

    assert eng.num_r1_r6 == 3335
    assert eng.num_r8 == 811
    assert len(eng.r1_r6_x) == 3335
    assert len(eng.r8_x) == 811

    frame = np.zeros((160, 90, 4), dtype=np.uint8)
    tel = eng.process_frame(frame)
    assert len(tel.r1_r6_currents) == 3335
    assert len(tel.r8_currents) == 811
