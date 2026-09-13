"""Visual transduction engine: deterministic retinal projection, chromatic decomposition, and innate looming threat detection."""

from dataclasses import dataclass, field

import numpy as np

from ..config import CONFIG


def generate_deterministic_retina_coords(
    n_points: int,
    x_min: int,
    x_max: int,
    y_min: int,
    y_max: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Generate deterministic ommatidial coordinates without pseudo-random numbers.

    Distributes n_points regularly across [x_min, x_max) and [y_min, y_max)
    using a uniform 2D raster lattice with zero randomness.
    """
    if n_points <= 0:
        return np.empty(0, dtype=np.int32), np.empty(0, dtype=np.int32)

    w_h = max(1, x_max - x_min)
    h = max(1, y_max - y_min)

    cols = max(1, int(np.round(np.sqrt(n_points * (w_h / h)))))
    rows = int(np.ceil(n_points / cols))

    indices = np.arange(n_points)
    row_idx = indices % rows
    col_idx = indices // rows

    y = np.clip((row_idx + 0.5) * (h / rows), y_min, y_max - 1).astype(np.int32)
    x = np.clip(x_min + (col_idx + 0.5) * (w_h / cols), x_min, x_max - 1).astype(np.int32)
    return x, y


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

    # Hemispheric Vision Signals
    left_luminance: float = 0.0
    right_luminance: float = 0.0
    hemispheric_asymmetry: float = 0.0  # -1.0 (pure left) to +1.0 (pure right)
    r1_r6_left_currents: np.ndarray = field(default_factory=lambda: np.empty(0, dtype=np.float32))
    r1_r6_right_currents: np.ndarray = field(default_factory=lambda: np.empty(0, dtype=np.float32))
    r8_left_currents: np.ndarray = field(default_factory=lambda: np.empty(0, dtype=np.float32))
    r8_right_currents: np.ndarray = field(default_factory=lambda: np.empty(0, dtype=np.float32))

    # Chromatic Photometry & Planckian Locus Distance
    cct_duv: float = 0.0
    cct_valid: bool = True


def compute_mccamy_cct(
    r: float, g: float, b: float, return_metrics: bool = False
) -> float | tuple[float, float, bool]:
    """Calculate Correlated Color Temperature (CCT) in Kelvin via McCamy's approximation,
    along with distance to the Planckian locus (Duv in CIE 1960 UCS).

    Transforms sRGB -> linear RGB -> CIE 1931 XYZ (D65 illuminant reference) ->
    xy chromaticity coordinates -> McCamy CCT polynomial:
        CCT = 449.0 * n^3 + 3525.0 * n^2 + 6823.3 * n + 5520.33
    where n = (x - 0.3320) / (0.1858 - y).

    Also evaluates the Planckian blackbody locus (u_bb, v_bb) via Krystek's formulation
    at temperature T = CCT, and computes the signed orthogonal distance Duv:
        Duv = sign(v - v_bb) * sqrt((u - u_bb)^2 + (v - v_bb)^2)
    Per ANSI C78.377 and CIE standards, CCT is physically meaningful/correlated only when
    |Duv| <= 0.05. For highly saturated colors far from the blackbody locus (e.g. Pure Blue #0000E6,
    where |Duv| ~ 0.30), cct_valid is False.
    """
    def to_linear(c: float) -> float:
        c_clamped = max(0.0, min(1.0, float(c)))
        return c_clamped / 12.92 if c_clamped <= 0.04045 else ((c_clamped + 0.055) / 1.055) ** 2.4

    r_lin = to_linear(r)
    g_lin = to_linear(g)
    b_lin = to_linear(b)

    # IEC 61966-2-1 standard sRGB to CIE 1931 XYZ matrix (D65 reference white)
    X = 0.4124564 * r_lin + 0.3575761 * g_lin + 0.1804375 * b_lin
    Y = 0.2126729 * r_lin + 0.7151522 * g_lin + 0.0721750 * b_lin
    Z = 0.0193339 * r_lin + 0.1191920 * g_lin + 0.9503041 * b_lin

    total = X + Y + Z
    if total < 1e-7:
        if return_metrics:
            return 6500.0, 0.0, True  # Neutral D65 daylight baseline in total darkness
        return 6500.0

    x = X / total
    y = Y / total

    # CIE 1960 UCS coordinates: u = 4x / (-2x + 12y + 3), v = 6y / (-2x + 12y + 3)
    denom_uv = -2.0 * x + 12.0 * y + 3.0
    if abs(denom_uv) < 1e-7:
        denom_uv = 1e-7
    u = 4.0 * x / denom_uv
    v = 6.0 * y / denom_uv

    # McCamy's approximation formula
    # Epicenter coordinates: xe = 0.3320, ye = 0.1858
    denom = 0.1858 - y
    if abs(denom) < 1e-7:
        denom = 1e-7 if denom >= 0.0 else -1e-7

    n = (x - 0.3320) / denom
    raw_cct = 449.0 * (n ** 3) + 3525.0 * (n ** 2) + 6823.3 * n + 5520.33
    cct = float(np.clip(raw_cct, 1000.0, 40000.0))

    # Krystek's formulation for Planckian locus coordinates in CIE 1960 UCS at T = cct
    T = cct
    u_bb = (0.860117757 + 1.54118254e-4 * T + 1.28641212e-7 * T**2) / (1.0 + 8.42420235e-4 * T + 7.08145163e-7 * T**2)
    v_bb = (0.317398726 + 4.22806245e-5 * T + 4.20481691e-8 * T**2) / (1.0 - 2.89741816e-5 * T + 1.61456053e-7 * T**2)

    # Signed distance Duv (positive above Planckian locus towards green, negative below towards magenta/blue)
    dist = float(np.sqrt((u - u_bb) ** 2 + (v - v_bb) ** 2))
    duv = dist if (v >= v_bb) else -dist
    is_valid = bool(abs(duv) <= 0.05)

    if return_metrics:
        return cct, duv, is_valid
    return cct


class VisualTransductionEngine:
    """Projects screen frames to the biological fly retina and computes looming threat dynamics.

    Drosophila visual pathways:
    - R1–R6: Outer photoreceptors, high-sensitivity broadband motion & luminance (rhodopsin Rh1).
      Deterministically mapped to Left Eye [0, mid_x) and Right Eye [mid_x, width).
    - R8: Inner photoreceptors, chromatic & ultraviolet sensitivity (rhodopsins Rh5/Rh6).
    - LC4 & LPLC2: Lobula columnar neurons that respond specifically to dark expanding edges (looming predators).
    """

    def __init__(
        self,
        num_r1_r6: int | None = None,
        num_r8: int | None = None,
        num_looming_lc4: int = 128,
        num_r1_r6_left: int = 1112,
        num_r1_r6_right: int = 2265,
        num_r8_left: int = 625,
        num_r8_right: int = 704,
        frame_width: int = CONFIG.frame_width,
        frame_height: int = CONFIG.frame_height,
    ):
        self.width = frame_width
        self.height = frame_height
        self.num_lc4 = num_looming_lc4

        # If legacy flat num_r1_r6 or num_r8 are passed, partition them proportionally
        if num_r1_r6 is not None:
            self.num_r1_r6_left = round(num_r1_r6 * (1112 / 3377))
            self.num_r1_r6_right = num_r1_r6 - self.num_r1_r6_left
        else:
            self.num_r1_r6_left = num_r1_r6_left
            self.num_r1_r6_right = num_r1_r6_right

        if num_r8 is not None:
            self.num_r8_left = round(num_r8 * (625 / 1329))
            self.num_r8_right = num_r8 - self.num_r8_left
        else:
            self.num_r8_left = num_r8_left
            self.num_r8_right = num_r8_right

        self.num_r1_r6 = self.num_r1_r6_left + self.num_r1_r6_right
        self.num_r8 = self.num_r8_left + self.num_r8_right

        # Previous frame luminance memory for optical expansion / looming calculation
        self.prev_luminance: np.ndarray | None = None

        # Midline boundary separating left and right visual hemifields
        mid_x = self.width // 2

        # 1. Deterministic R1-R6 Ommatidial Mapping (Zero Random, Zero Mock)
        self.r1_r6_l_x, self.r1_r6_l_y = generate_deterministic_retina_coords(
            self.num_r1_r6_left, 0, mid_x, 0, self.height
        )
        self.r1_r6_r_x, self.r1_r6_r_y = generate_deterministic_retina_coords(
            self.num_r1_r6_right, mid_x, self.width, 0, self.height
        )
        self.r1_r6_x = np.concatenate([self.r1_r6_l_x, self.r1_r6_r_x])
        self.r1_r6_y = np.concatenate([self.r1_r6_l_y, self.r1_r6_r_y])

        # 2. Deterministic R8 Chromatic Ommatidial Mapping
        self.r8_l_x, self.r8_l_y = generate_deterministic_retina_coords(
            self.num_r8_left, 0, mid_x, 0, self.height
        )
        self.r8_r_x, self.r8_r_y = generate_deterministic_retina_coords(
            self.num_r8_right, mid_x, self.width, 0, self.height
        )
        self.r8_x = np.concatenate([self.r8_l_x, self.r8_r_x])
        self.r8_y = np.concatenate([self.r8_l_y, self.r8_r_y])

    def process_frame(self, frame_rgba: np.ndarray) -> VisualTransductionTelemetry:
        """Process a 90x160 RGBA video/photo frame into biophysical currents with deterministic hemifields.

        Args:
            frame_rgba: np.ndarray of shape (160, 90, 4) or (160, 90, 3), dtype=uint8.
        """
        rgb = frame_rgba[:, :, :3].astype(np.float32) / 255.0

        # Standard relative luminance: Y = 0.299 R + 0.587 G + 0.114 B
        lum = 0.299 * rgb[:, :, 0] + 0.587 * rgb[:, :, 1] + 0.114 * rgb[:, :, 2]

        # Hemispheric luminance partitioning
        mid_x = self.width // 2
        left_lum = float(np.mean(lum[:, :mid_x]))
        right_lum = float(np.mean(lum[:, mid_x:]))
        asym_denom = left_lum + right_lum + 1e-5
        hemispheric_asymmetry = float(np.clip((right_lum - left_lum) / asym_denom, -1.0, 1.0))

        # 1. R1-R6 outer photoreceptor currents (proportional to luminance + contrast)
        # Scale 7.0 ensures mean-luminance pixels (~0.22) exceed the LIF threshold of 1.5 pA
        # (v_thresh − v_rest) / R_membrane = (−50 − (−65)) / 10 = 1.5 pA  [LIF biophysics]
        r1_r6_l_currents = (lum[self.r1_r6_l_y, self.r1_r6_l_x] * 7.0).astype(np.float32)
        r1_r6_r_currents = (lum[self.r1_r6_r_y, self.r1_r6_r_x] * 7.0).astype(np.float32)
        r1_r6_currents = np.concatenate([r1_r6_l_currents, r1_r6_r_currents])

        # 2. R8 chromatic photoreceptor currents (Rh5 blue/UV vs Rh6 green pathway)
        # Scale 5.0 amplifies spectral differences (red vs green vs UV stimuli)
        r8_l_bg = (rgb[self.r8_l_y, self.r8_l_x, 1] + rgb[self.r8_l_y, self.r8_l_x, 2]) * 0.5
        r8_r_bg = (rgb[self.r8_r_y, self.r8_r_x, 1] + rgb[self.r8_r_y, self.r8_r_x, 2]) * 0.5
        r8_l_currents = (r8_l_bg * 5.0).astype(np.float32)
        r8_r_currents = (r8_r_bg * 5.0).astype(np.float32)
        r8_currents = np.concatenate([r8_l_currents, r8_r_currents])

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
        mean_g = float(np.mean(rgb[:, :, 1]))
        mean_b = float(np.mean(rgb[:, :, 2]))

        if mean_lum < 1e-4:
            color_temp_k = 6500.0  # Neutral daylight baseline in total darkness
            cct_duv = 0.0
            cct_valid = True
        else:
            color_temp_k, cct_duv, cct_valid = compute_mccamy_cct(
                mean_r, mean_g, mean_b, return_metrics=True
            )

        return VisualTransductionTelemetry(
            mean_luminance=mean_lum,
            color_temperature_k=color_temp_k,
            cct_duv=cct_duv,
            cct_valid=cct_valid,
            looming_threat_detected=threat_detected,
            looming_expansion_rate=expansion_rate,
            r1_r6_currents=r1_r6_currents,
            r8_currents=r8_currents,
            looming_currents=looming_currents,
            left_luminance=left_lum,
            right_luminance=right_lum,
            hemispheric_asymmetry=hemispheric_asymmetry,
            r1_r6_left_currents=r1_r6_l_currents,
            r1_r6_right_currents=r1_r6_r_currents,
            r8_left_currents=r8_l_currents,
            r8_right_currents=r8_r_currents,
        )
