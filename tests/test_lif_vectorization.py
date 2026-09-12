"""
Tests specific to the vectorized mini-chunk LIF kernel (lif_kernel.py refactor).

Covers:
1. Mini-chunk produces biophysically sound voltage (stays in physical bounds)
2. Refractory period is honoured across mini-chunk boundaries
3. Spike accumulator is monotonically non-decreasing
4. Zero-current -> zero spikes at resting state
5. Sim time advances correctly per chunk
6. Performance budget: 5K-neuron chunk must complete < 500ms on CI
7. Mini-chunk is faster than sequential step-by-step
"""

import time
import numpy as np
import scipy.sparse as sp
import pytest

from connectome_engine.config import CONFIG
from connectome_engine.simulation.lif_kernel import SpikingConnectomeEngine


def _make_engine(n: int, density: float = 0.04, seed: int = 42):
    rng = np.random.default_rng(seed)
    data = rng.random(int(n * n * density)).astype(np.float32) * 0.5
    rows = rng.integers(0, n, len(data))
    cols = rng.integers(0, n, len(data))
    adj = sp.csr_matrix((data, (rows, cols)), shape=(n, n), dtype=np.float32)
    return SpikingConnectomeEngine(n, adj, CONFIG)


# ── 1. Physical voltage bounds ────────────────────────────────────────────

def test_voltage_within_physical_bounds():
    """After stimulation, membrane potential must stay in [V_reset, V_thresh]."""
    n = 100
    engine = _make_engine(n)
    engine.inject_current(np.arange(20, dtype=np.int32), np.full(20, 12.0, dtype=np.float32))
    for _ in range(5):
        t = engine.step_chunk(50.0)
        assert t.voltage_min_mv >= CONFIG.v_reset_mv - 0.5
        assert t.voltage_max_mv <= CONFIG.v_thresh_mv + 1.0


def test_resting_state_no_current():
    """Without external current, all neurons must stay at V_rest after one chunk."""
    engine = _make_engine(50)
    t = engine.step_chunk(50.0)
    assert t.total_spikes == 0
    np.testing.assert_allclose(engine.v, CONFIG.v_rest_mv, atol=0.01)


# ── 2. Refractory period ─────────────────────────────────────────────────

def test_refractory_suppresses_consecutive_spikes():
    """Strong constant current: spikes must not exceed refractory rate limit."""
    n = 10
    engine = _make_engine(n)
    engine.inject_current(np.arange(n, dtype=np.int32), np.full(n, 20.0, dtype=np.float32))
    t = engine.step_chunk(50.0)
    max_possible = n * int(50.0 / CONFIG.tau_ref_ms)
    assert t.total_spikes <= max_possible, (
        f"Refractory violated: {t.total_spikes} > max allowed {max_possible}"
    )


# ── 3. Spike accumulator monotonicity ────────────────────────────────────

def test_spike_accumulator_monotone():
    """total_spikes_accumulated must never decrease across consecutive chunks."""
    engine = _make_engine(200)
    engine.inject_current(np.arange(40, dtype=np.int32), np.full(40, 10.0, dtype=np.float32))
    prev = 0
    for _ in range(8):
        engine.step_chunk(50.0)
        assert engine.total_spikes_accumulated >= prev
        prev = engine.total_spikes_accumulated


def test_zero_current_zero_spikes():
    """No injected current at resting potential must produce zero spikes."""
    engine = _make_engine(100)
    t = engine.step_chunk(50.0)
    assert t.total_spikes == 0


# ── 4. Sim time advancement ───────────────────────────────────────────────

def test_sim_time_monotone():
    """total_sim_ms must increase after each chunk call."""
    engine = _make_engine(50)
    prev_t = 0.0
    for _ in range(4):
        engine.step_chunk(50.0)
        assert engine.total_sim_ms > prev_t
        prev_t = engine.total_sim_ms


# ── 5. Checkpoint round-trip ──────────────────────────────────────────────

def test_checkpoint_after_mini_chunk():
    """State saved after a mini-chunk step must be exactly restored."""
    engine = _make_engine(80)
    engine.inject_current(np.array([0, 1], dtype=np.int32), np.array([10.0, 10.0], dtype=np.float32))
    engine.step_chunk(50.0)

    ckpt = engine.save_checkpoint()

    restored = _make_engine(80)
    restored.load_checkpoint(ckpt)

    np.testing.assert_allclose(restored.v, engine.v)
    np.testing.assert_array_equal(restored.refractory_steps, engine.refractory_steps)
    assert restored.total_sim_ms == engine.total_sim_ms


# ── 6. Performance budget ─────────────────────────────────────────────────

def test_5k_neuron_chunk_under_500ms():
    """5K-neuron 50ms chunk must complete in under 500ms (CI budget)."""
    n = 5000
    engine = _make_engine(n, density=0.04)
    engine.inject_current(np.arange(80, dtype=np.int32), np.full(80, 12.0, dtype=np.float32))
    engine.step_chunk(10.0)  # warm-up
    t0 = time.perf_counter()
    engine.step_chunk(50.0)
    elapsed_ms = (time.perf_counter() - t0) * 1000
    assert elapsed_ms < 500.0, f"5K-neuron chunk took {elapsed_ms:.1f}ms (budget: 500ms)"


def test_mini_chunk_faster_than_sequential():
    """Mini-chunk vectorization must be faster than sequential step-by-step."""
    n = 1000
    engine_fast = _make_engine(n)
    engine_slow = _make_engine(n)
    curr = np.full(50, 8.0, dtype=np.float32)
    idx  = np.arange(50, dtype=np.int32)
    engine_fast.inject_current(idx, curr)
    engine_slow.inject_current(idx, curr)

    engine_fast.step_chunk(10.0)  # warm-up

    t0 = time.perf_counter()
    engine_fast.step_chunk(50.0)
    fast_ms = (time.perf_counter() - t0) * 1000

    substeps = int(round(50.0 / CONFIG.dt_ms))
    t0 = time.perf_counter()
    for _ in range(substeps):
        engine_slow.step_substep()
    slow_ms = (time.perf_counter() - t0) * 1000

    assert fast_ms < slow_ms, (
        f"Mini-chunk ({fast_ms:.1f}ms) should beat sequential ({slow_ms:.1f}ms)"
    )
