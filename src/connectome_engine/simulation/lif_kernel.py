"""High-performance Leaky Integrate-and-Fire (LIF) Spiking Neural Network simulation kernel."""

from dataclasses import dataclass
from typing import Dict, Optional, Tuple
import numpy as np
import scipy.sparse as sp

from ..config import CONFIG, BiophysicalConstants


@dataclass
class SNNTelemetry:
    """Telemetry payload produced per simulation step chunk."""

    total_spikes: int
    mean_firing_rate_hz: float
    voltage_mean_mv: float
    voltage_min_mv: float
    voltage_max_mv: float
    spiking_neuron_indices: np.ndarray
    simulated_time_ms: float


class SpikingConnectomeEngine:
    """Vectorized Leaky Integrate-and-Fire (LIF) engine for large connectomes.

    Differential equation integrated via Euler method with sub-step dt:
        dV/dt = -(V - V_rest) / tau_m + (I_syn + I_ext) * R_m

    Spike generation:
        If V >= V_thresh and refractory_timer == 0:
            emit spike (S = 1)
            V = V_reset
            refractory_timer = tau_ref / dt
    """

    def __init__(
        self,
        num_neurons: int,
        synaptic_weights: sp.csr_matrix,
        constants: BiophysicalConstants = CONFIG,
    ):
        self.n = num_neurons
        self.weights = synaptic_weights.tocsr().astype(np.float32)
        self.cfg = constants

        # Membrane states
        self.v = np.full(self.n, self.cfg.v_rest_mv, dtype=np.float32)
        self.refractory_steps = np.zeros(self.n, dtype=np.int32)
        self.spikes = np.zeros(self.n, dtype=bool)

        # Persistent external current injection buffer (pA / mV-equiv)
        self.i_ext = np.zeros(self.n, dtype=np.float32)

        # Precomputed integration constants for numerical speed
        self.decay_factor = np.float32(np.exp(-self.cfg.dt_ms / self.cfg.tau_m_ms))
        self.v_rest = np.float32(self.cfg.v_rest_mv)
        self.v_thresh = np.float32(self.cfg.v_thresh_mv)
        self.v_reset = np.float32(self.cfg.v_reset_mv)
        self.ref_steps_const = int(round(self.cfg.tau_ref_ms / self.cfg.dt_ms))

        # Simulation clock
        self.total_sim_ms = 0.0
        self.total_spikes_accumulated = 0

    def inject_current(self, neuron_indices: np.ndarray, current_values: np.ndarray):
        """Inject external sensory or experimental currents into designated neurons."""
        self.i_ext[neuron_indices] = current_values

    def clear_injected_currents(self):
        """Zero out all external current injections."""
        self.i_ext.fill(0.0)

    def step_substep(self) -> np.ndarray:
        """Advance one fine-grained integration step (dt = 0.1 ms)."""
        # Decrement refractory counters
        in_refractory = self.refractory_steps > 0
        self.refractory_steps[in_refractory] -= 1

        # Calculate postsynaptic currents: I_syn = W * S(t-1)
        # Note: only spiking neurons contribute; if no spikes, I_syn is 0
        if np.any(self.spikes):
            # Sparse matrix-vector product with boolean spike vector
            spiking_indices = np.flatnonzero(self.spikes)
            # Efficient slice: sum incoming weights from spiked neurons
            i_syn = np.asarray(self.weights[:, spiking_indices].sum(axis=1)).ravel()
        else:
            i_syn = np.zeros(self.n, dtype=np.float32)

        # Total input current
        total_input = i_syn + self.i_ext

        # Voltage integration for non-refractory neurons
        non_ref = ~in_refractory
        self.v[non_ref] = (
            self.v_rest
            + (self.v[non_ref] - self.v_rest) * self.decay_factor
            + total_input[non_ref] * (1.0 - self.decay_factor) * self.cfg.r_membrane_mohm
        )

        # Threshold detection & spike generation
        new_spikes = non_ref & (self.v >= self.v_thresh)
        if np.any(new_spikes):
            self.v[new_spikes] = self.v_reset
            self.refractory_steps[new_spikes] = self.ref_steps_const

        self.spikes = new_spikes
        self.total_sim_ms += self.cfg.dt_ms
        return self.spikes

    def step_chunk(self, chunk_ms: Optional[float] = None) -> SNNTelemetry:
        """Advance the biological simulation by one visual frame chunk (default 50 ms)."""
        target_ms = chunk_ms if chunk_ms is not None else self.cfg.chunk_ms
        substeps = int(round(target_ms / self.cfg.dt_ms))

        chunk_spike_counts = np.zeros(self.n, dtype=np.int32)

        for _ in range(substeps):
            spk = self.step_substep()
            if np.any(spk):
                chunk_spike_counts[spk] += 1

        total_chunk_spikes = int(chunk_spike_counts.sum())
        self.total_spikes_accumulated += total_chunk_spikes

        # Active neurons during this 50 ms chunk
        spiking_indices = np.flatnonzero(chunk_spike_counts)
        mean_rate_hz = (total_chunk_spikes / (self.n * (target_ms / 1000.0))) if self.n > 0 else 0.0

        return SNNTelemetry(
            total_spikes=total_chunk_spikes,
            mean_firing_rate_hz=float(mean_rate_hz),
            voltage_mean_mv=float(np.mean(self.v)),
            voltage_min_mv=float(np.min(self.v)),
            voltage_max_mv=float(np.max(self.v)),
            spiking_neuron_indices=spiking_indices,
            simulated_time_ms=self.total_sim_ms,
        )

    def get_cluster_firing_rate(self, cluster_indices: np.ndarray, duration_ms: float = 50.0) -> float:
        """Calculate the average firing rate (Hz) for a specific biological neuron cluster."""
        if len(cluster_indices) == 0:
            return 0.0
        # Instantaneous rate estimate from active membrane potential proximity to threshold
        # and active refractory states
        active_spiking = np.count_nonzero(self.refractory_steps[cluster_indices] == self.ref_steps_const)
        return float(active_spiking / (len(cluster_indices) * (duration_ms / 1000.0)))

    def save_checkpoint(self) -> Dict[str, np.ndarray]:
        """Create a complete serializable state snapshot."""
        return {
            "v": self.v.copy(),
            "refractory_steps": self.refractory_steps.copy(),
            "spikes": self.spikes.copy(),
            "total_sim_ms": np.array([self.total_sim_ms], dtype=np.float64),
        }

    def load_checkpoint(self, state: Dict[str, np.ndarray]):
        """Restore engine state from checkpoint."""
        self.v[:] = state["v"]
        self.refractory_steps[:] = state["refractory_steps"]
        self.spikes[:] = state["spikes"]
        self.total_sim_ms = float(state["total_sim_ms"][0])
