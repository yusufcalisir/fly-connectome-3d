"""Thread-safe state manager and rolling telemetry history buffer."""

import threading
from collections import deque
from dataclasses import asdict
from typing import Any

from ..brain import CompleteObservationTelemetry


class ServerStateManager:
    """Manages active brain instance, real-time telemetry buffer, and client control events."""

    def __init__(self, history_len: int = 120):
        self.lock = threading.Lock()
        self.history_len = history_len

        # Rolling telemetry records
        self.history_records = deque(maxlen=history_len)

        # Baseline resting telemetry
        self.latest_telemetry: dict[str, Any] = {
            "sim_time_ms": 0.0,
            "total_spikes": 0,
            "mean_firing_rate_hz": 0.0,
            "dopamine_hz": 0.0,
            "dopamine_conc_nm": 5.0,
            "octopamine_hz": 0.0,
            "octopamine_conc_nm": 2.0,
            "serotonin_hz": 0.0,
            "serotonin_conc_nm": 8.0,
            "ei_balance_ratio": 1.0,
            "learned_knowledge_index": 0.0,
            "steering_deflection": 0.0,
            "forward_drive_pct": 0.0,
            "moonwalker_retreat": False,
            "giant_fiber_jump": False,
            "front_leg_swipe_angle": 0.0,
            "compass_heading_deg": 0.0,
            "mean_luminance": 0.5,
            "color_temperature_k": 5500.0,
            "looming_threat_detected": False,
            "left_luminance": 0.5,
            "right_luminance": 0.5,
            "hemispheric_asymmetry": 0.0,
            "dna02_left_spikes": 0,
            "dna02_right_spikes": 0,
            "active_landmarks": [],
            "active_neurons": [],
            "visual": {
                "mean_luminance": 0.5,
                "color_temperature_k": 5500.0,
                "looming_threat_detected": False,
                "left_luminance": 0.5,
                "right_luminance": 0.5,
                "hemispheric_asymmetry": 0.0,
            },
            "hormones": {
                "dopamine_nm": 5.0,
                "octopamine_nm": 2.0,
                "serotonin_nm": 8.0,
                "ei_balance": 1.0,
                "plasticity_index": 0.0,
            },
            "motor": {
                "steering_deflection": 0.0,
                "forward_drive_pct": 0.0,
                "moonwalker_retreat": False,
                "giant_fiber_jump": False,
                "front_leg_swipe_angle": 0.0,
                "compass_heading_deg": 0.0,
            },
            "spike_counts": {
                "total_spikes": 0,
                "excitatory_spikes": 0,
                "inhibitory_spikes": 0,
                "dopamine_hz": 0.0,
                "octopamine_hz": 0.0,
                "serotonin_hz": 0.0,
            },
            "vnc_legs": {
                "t1_left_hz": 0.0,
                "t1_right_hz": 0.0,
                "t2_left_hz": 0.0,
                "t2_right_hz": 0.0,
                "t3_left_hz": 0.0,
                "t3_right_hz": 0.0,
                "tripod_phase": 0.0,
            },
        }
        self.history_records.append(
            {
                "sim_time_ms": 0.0,
                "dopamine_hz": 0.0,
                "octopamine_hz": 0.0,
                "serotonin_hz": 0.0,
                "total_spikes": 0,
            }
        )
        self.is_paused = False
        self.pending_wirehead_boost_mv = 0.0

    def push_telemetry(self, t: CompleteObservationTelemetry):
        """Append fresh telemetry from engine chunk."""
        with self.lock:
            data = asdict(t)
            # Add nested groups for UI ergonomics
            structured = {
                **data,
                "visual": {
                    "mean_luminance": data["mean_luminance"],
                    "color_temperature_k": data["color_temperature_k"],
                    "looming_threat_detected": data["looming_threat_detected"],
                    "left_luminance": data.get("left_luminance", 0.0),
                    "right_luminance": data.get("right_luminance", 0.0),
                    "hemispheric_asymmetry": data.get("hemispheric_asymmetry", 0.0),
                },
                "hormones": {
                    "dopamine_nm": data["dopamine_conc_nm"],
                    "octopamine_nm": data["octopamine_conc_nm"],
                    "serotonin_nm": data["serotonin_conc_nm"],
                    "ei_balance": data["ei_balance_ratio"],
                    "plasticity_index": data["learned_knowledge_index"],
                },
                "motor": {
                    "steering_deflection": data["steering_deflection"],
                    "forward_drive_pct": data["forward_drive_pct"],
                    "moonwalker_retreat": data["moonwalker_retreat"],
                    "giant_fiber_jump": data["giant_fiber_jump"],
                    "front_leg_swipe_angle": data["front_leg_swipe_angle"],
                    "compass_heading_deg": data["compass_heading_deg"],
                },
                "spike_counts": {
                    "total_spikes": data["total_spikes"],
                    "excitatory_spikes": data.get("excitatory_spikes", 0),
                    "inhibitory_spikes": data.get("inhibitory_spikes", 0),
                    "dopamine_hz": data["dopamine_hz"],
                    "octopamine_hz": data["octopamine_hz"],
                    "serotonin_hz": data["serotonin_hz"],
                },
                "vnc_legs": {
                    "t1_left_hz": data.get("t1_left_hz", 0.0),
                    "t1_right_hz": data.get("t1_right_hz", 0.0),
                    "t2_left_hz": data.get("t2_left_hz", 0.0),
                    "t2_right_hz": data.get("t2_right_hz", 0.0),
                    "t3_left_hz": data.get("t3_left_hz", 0.0),
                    "t3_right_hz": data.get("t3_right_hz", 0.0),
                    "tripod_phase": data.get("tripod_phase", 0.0),
                },
            }
            self.latest_telemetry = structured

            # Rolling history for frontend graphs
            self.history_records.append(
                {
                    "sim_time_ms": data["sim_time_ms"],
                    "dopamine_hz": data["dopamine_hz"],
                    "octopamine_hz": data["octopamine_hz"],
                    "serotonin_hz": data["serotonin_hz"],
                    "total_spikes": data["total_spikes"],
                    "ei_balance": data.get("ei_balance_ratio", 0.644),
                }
            )

    def trigger_wirehead(self, current_mv: float = 20.0):
        """Register immediate manual wireheading stimulus."""
        with self.lock:
            self.pending_wirehead_boost_mv = current_mv

    def consume_wirehead(self) -> float:
        """Read and clear pending wireheading stimulus."""
        with self.lock:
            val = self.pending_wirehead_boost_mv
            self.pending_wirehead_boost_mv = 0.0
            return val

    def get_snapshot(self) -> dict[str, Any]:
        """Fetch current telemetry and rolling chart history for UI broadcast."""
        with self.lock:
            return {
                "latest": self.latest_telemetry,
                "history": list(self.history_records),
                "paused": self.is_paused,
            }
