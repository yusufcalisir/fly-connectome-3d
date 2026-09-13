"""Regression tests validating bounded synaptic plasticity saturation and decay."""

import numpy as np

from connectome_engine.config import HORMONE_CONFIG
from connectome_engine.simulation.hormones import HormoneDynamicsEngine


def test_plasticity_monotonic_saturation_bound():
    """Verify that sustained associative pairing saturates asymptotically without exceeding plasticity_max."""
    engine = HormoneDynamicsEngine()
    p_max = HORMONE_CONFIG.plasticity_max
    assert p_max == 2.00
    assert engine.learned_weight_drift == 0.0

    history = []
    # Step 50 consecutive chunks with high dopamine and robust Kenyon cell firing
    for step in range(50):
        t = engine.update(
            pam11_spikes=150,
            num_pam11=15,
            threat_spikes=0,
            num_threat_nodes=10,
            total_excitatory_spikes=1000,
            total_inhibitory_spikes=500,
            kc_spikes=4000,
            duration_ms=50.0,
        )
        history.append(t.learned_knowledge_index)
        assert t.learned_knowledge_index <= p_max, (
            f"Step {step}: plasticity_index {t.learned_knowledge_index} exceeded ceiling {p_max}"
        )
        assert not np.isnan(t.learned_knowledge_index)

    # Verify that the value reaches or approaches the ceiling and NEVER exceeds it
    assert all(val <= p_max for val in history)
    assert history[-1] == p_max

    # 2. Test graded/moderate stimulation to verify diminishing marginal gain (headroom scaling)
    graded_engine = HormoneDynamicsEngine()
    graded_history = []
    for step in range(30):
        t = graded_engine.update(
            pam11_spikes=30,
            num_pam11=15,
            threat_spikes=0,
            num_threat_nodes=10,
            total_excitatory_spikes=500,
            total_inhibitory_spikes=250,
            kc_spikes=1000,
            duration_ms=50.0,
        )
        graded_history.append(t.learned_knowledge_index)

    # All values must remain bounded by p_max
    assert all(val <= p_max for val in graded_history)
    # Check that after initial ramp-up, marginal delta decreases
    deltas = [graded_history[i] - graded_history[i - 1] for i in range(1, len(graded_history))]
    assert deltas[5] > deltas[15] > deltas[25]


def test_plasticity_passive_decay_toward_baseline():
    """Verify that in the absence of reinforcement, plasticity relaxes exponentially toward 0.0."""
    engine = HormoneDynamicsEngine()
    engine.learned_weight_drift = 1.95

    # Step repeatedly with zero spikes / baseline conditions
    drift_values = [engine.learned_weight_drift]
    for _ in range(100):  # 5000 ms = 0.5 * tau
        t = engine.update(
            pam11_spikes=0,
            num_pam11=15,
            threat_spikes=0,
            num_threat_nodes=10,
            total_excitatory_spikes=0,
            total_inhibitory_spikes=0,
            kc_spikes=0,
            duration_ms=50.0,
        )
        drift_values.append(t.learned_knowledge_index)

    # Verify strictly decreasing decay
    for i in range(1, len(drift_values)):
        assert drift_values[i] < drift_values[i - 1]

    # At t = 5000 ms (0.5 * 10,000 ms tau), expected value is ~ 1.95 * exp(-0.5) ≈ 1.18
    expected_half_tau = 1.95 * np.exp(-5000.0 / HORMONE_CONFIG.plasticity_decay_tau_ms)
    assert abs(drift_values[-1] - expected_half_tau) < 0.02


def test_plasticity_zero_baseline_stability():
    """Verify resting baseline remains strictly 0.0 without going negative."""
    engine = HormoneDynamicsEngine()
    for _ in range(20):
        t = engine.update(
            pam11_spikes=0,
            num_pam11=15,
            threat_spikes=0,
            num_threat_nodes=10,
            total_excitatory_spikes=0,
            total_inhibitory_spikes=0,
            kc_spikes=0,
            duration_ms=50.0,
        )
        assert t.learned_knowledge_index == 0.0
