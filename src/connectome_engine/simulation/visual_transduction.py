"""Visual transduction engine: retinal projection, chromatic decomposition, and innate looming threat detection."""

from dataclasses import dataclass
from typing import Tuple
import numpy as np

from ..config import CONFIG


@dataclass
class VisualTransductionTelemetry:
    """Visual signals extracted from the incoming screen frame."""

    mean_luminance: float
    color_temperature_k: float
    looming_threat_detected: bool
    looming_expansion_rate: float
    r1_r6_currents: np.ndarray
    r8_currents: np.ndarray
    looming_currents: np.ndarray


class VisualTransductionEngine:
    """Projects screen frames to the biological fly retina and computes looming threat dynamics.

    Drosophila visual pathways:
    - R1–R6: Outer photoreceptors, high-sensitivity broadband motion & luminance (rhodopsin Rh1).
    - R8: Inner photoreceptors, chromatic & ultraviolet sensitivity (rhodopsins Rh5/Rh6).
    - LC4 & LPLC2: Lobula columnar neurons that respond specifically to dark expanding edges (looming predators).
    """

    def __init__(
        self,
        num_r1_r6: int = 3335,
        num_r8: int = 811,
        num_looming_lc4: int = 128,
        frame_width: int = CONFIG.frame_width,
        frame_height: int = CONFIG.frame_height,
    ):
        self.num_r1_r6 = num_r1_r6
        self.num_r8 = num_r8
        self.num_lc4 = num_looming_lc4
        self.width = frame_width
        self.height = frame_height

        # Previous frame luminance memory for optical expansion / looming calculation
        self.prev_luminance: Optional[np.ndarray] = None

        # Pre-assign pseudo-spatial coordinates on the 90x160 grid for each photoreceptor
        np.random.seed(42)
        self.r1_r6_y = np.random.randint(0, self.height, size=self.num_r1_r6)
        self.r1_r6_x = np.random.randint(0, self.width, size=self.num_r1_r6)

        self.r8_y = np.random.randint(0, self.height, size=self.num_r8)
        self.r8_x = np.random.randint(0, self.width, size=self.num_r8)

    def process_frame(self, frame_rgba: np.ndarray) -> VisualTransductionTelemetry:
        """Process a 90x160 RGBA video/photo frame into biophysical currents.

        Args:
            frame_rgba: np.ndarray of shape (160, 90, 4) or (160, 90, 3), dtype=uint8.
        """
        rgb = frame_rgba[:, :, :3].astype(np.float32) / 255.0

        # Standard relative luminance: Y = 0.299 R + 0.587 G + 0.114 B
        lum = 0.299 * rgb[:, :, 0] + 0.587 * rgb[:, :, 1] + 0.114 * rgb[:, :, 2]

        # 1. R1-R6 outer photoreceptor currents (proportional to luminance + contrast)
        r1_r6_vals = lum[self.r1_r6_y, self.r1_r6_x]
        # Injected current scale: 0 to 4.0 pA/mV
        r1_r6_currents = r1_r6_vals * 4.0

        # 2. R8 chromatic photoreceptor currents (spectral blue/green vs red ratio)
        # R8 inner cells are selectively sensitive to short-wavelength blue/green
        r8_blue_green = (rgb[self.r8_y, self.r8_x, 1] + rgb[self.r8_y, self.r8_x, 2]) * 0.5
        r8_currents = r8_blue_green * 3.5

        # 3. Innate Looming Threat Detection (Expanding Dark Shadows)
        threat_detected = False
        expansion_rate = 0.0
        looming_currents = np.zeros(self.num_lc4, dtype=np.float32)

        if self.prev_luminance is not None:
            # Contrast change: dark expansion corresponds to negative delta in central field
            delta = self.prev_luminance - lum
            # Focus on center 60% of field where looming predator appears
            cy_min, cy_max = int(self.height * 0.2), int(self.height * 0.8)
            cx_min, cx_max = int(self.width * 0.2), int(self.width * 0.8)
            center_delta = delta[cy_min:cy_max, cx_min:cx_max]

            # Rapid darkening in the central field
            darkening_edge_count = np.count_nonzero(center_delta > 0.15)
            total_center_pixels = (cy_max - cy_min) * (cx_max - cx_min)
            fraction_darkening = darkening_edge_count / total_center_pixels

            if fraction_darkening > 0.12:
                threat_detected = True
                expansion_rate = float(fraction_darkening * 10.0)
                # Powerful current injection directly into LC4 / Giant Fiber escape trigger
                looming_currents.fill(min(15.0, expansion_rate * 3.0))

        self.prev_luminance = lum.copy()

        # Mean visual statistics
        mean_lum = float(np.mean(lum))
        mean_r = float(np.mean(rgb[:, :, 0]))
        mean_b = float(np.mean(rgb[:, :, 2])) + 1e-5
        color_temp_k = float(3000.0 + (mean_b / (mean_r + 1e-5)) * 3500.0)

        return VisualTransductionTelemetry(
            mean_luminance=mean_lum,
            color_temperature_k=color_temp_k,
            looming_threat_detected=threat_detected,
            looming_expansion_rate=expansion_rate,
            r1_r6_currents=r1_r6_currents.astype(np.float32),
            r8_currents=r8_currents.astype(np.float32),
            looming_currents=looming_currents.astype(np.float32),
        )
