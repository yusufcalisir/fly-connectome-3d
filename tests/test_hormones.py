"""Unit tests for hormone kinetics (Dopamine, Octopamine, Serotonin)."""

from connectome_engine.config import HORMONE_CONFIG
from connectome_engine.simulation.hormones import HormoneDynamicsEngine


def test_dopamine_synthesis_and_decay():
    """Verify dopamine concentration rises with PAM11 spikes and decays toward baseline."""
    engine = HormoneDynamicsEngine()
    initial_da = engine.da_conc
    assert initial_da == HORMONE_CONFIG.da_baseline_nm

    # Step with 10 PAM11 spikes
    telemetry = engine.update(
        pam11_spikes=10,
        num_pam11=15,
        threat_spikes=0,
        num_threat_nodes=10,
        total_excitatory_spikes=100,
        total_inhibitory_spikes=50,
        kc_spikes=20,
        duration_ms=50.0,
    )

    assert telemetry.dopamine_conc_nm > initial_da
    assert telemetry.dopamine_hz > 0.0

    # Step repeatedly with zero spikes: concentration must decay toward baseline
    for _ in range(50):
        telemetry = engine.update(
            pam11_spikes=0,
            num_pam11=15,
            threat_spikes=0,
            num_threat_nodes=10,
            total_excitatory_spikes=0,
            total_inhibitory_spikes=0,
            kc_spikes=0,
            duration_ms=50.0,
        )

    assert abs(telemetry.dopamine_conc_nm - HORMONE_CONFIG.da_baseline_nm) < 0.5


def test_wirehead_surge():
    """Verify artificial wireheading injection produces rapid dopamine surge."""
    engine = HormoneDynamicsEngine()
    baseline = engine.da_conc

    engine.trigger_wirehead_surge(current_mv=20.0)
    assert engine.da_conc > baseline + 40.0
