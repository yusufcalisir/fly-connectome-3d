# Local model validation

Verified on 2026-09-13 with Python 3.12.11, Windows x64, and the committed `uv.lock` dependency environment.

This document records empirical verification milestones, exact measurements, and explicit boundary statements defining what each test proves and what it does **not** prove. Future significant model changes or regressions must append a dated section to this log.

---

## 1. Initial Model & Connectome Dataset Integrity Verification — 2026-09-10

- **Dataset Provenance**: Janelia Research Campus **MaleCNS v1.0** serial-section transmission electron microscopy (ssTEM) dataset.
- **Graph Dimensions**: 166,700 reconstructed neurons and 25,582,938 directed synaptic connections.
- **Soma Morphology**: 141,781 3D $[X, Y, Z]$ soma coordinates extracted, normalized into Three.js anatomical space, and serialized into `soma_coordinates_141k.bin` (2.55 MB binary array).
- **Dale's Principle E/I Polarity**: All 166,700 cells classified by predicted neurotransmitter:
  - Acetylcholine ($ACh$): Excitatory ($w > 0$, depolarizing EPSPs).
  - GABA, Glutamate, Histamine: Inhibitory ($w < 0$, hyperpolarizing IPSPs).
- **Numerical Clamping**: Potassium reversal potential clamped at $V_{\text{clamp}} = -85.0\text{ mV}$ to prevent numerical run-away hyperpolarization under dense inhibition.
- **Automated Verification**: 87 passing automated tests across unit, biophysical integration, and full-graph connectivity suites.

> **Boundary Statement**:
> *This is evidence of structural graph integrity, 3D coordinate normalization, and numerical stability in the vectorized Leaky Integrate-and-Fire (LIF) kernel. It is **NOT** evidence of biological intracellular voltage dynamics, dendritic compartmentalization, or complete whole-organism functional fidelity.*

---

## 2. Cold-Start Empirical Benchmarks & CI Reproducibility — 2026-09-13

- **Environment**: Python 3.12.11 (`uv`), Windows 11 x64, single-socket CPU backend.
- **Protocol**: `scripts/generate_benchmarks.py` (`connectome_engine.benchmarks.run_benchmarks`) executed with a freshly instantiated `FlyConnectomeEngine` (cold-start, zero residual voltage or synaptic memory) across 4 standardized visual stimuli presented for 50 ms of simulated neural time:
  1. **Pure White** (`#FFFFFF`):
     - Luminance ($Y$): `1.000`
     - Network Spikes: `25,578`
     - Mean Firing Rate: `3.07 Hz`
     - Looming Threat: `False`
     - Correlated Color Temperature: `6,504 K` ($D_{uv} = +0.0032$, `cct_valid: True`)
  2. **Pure Red** (`#C80000`):
     - Luminance ($Y$): `0.235`
     - Network Spikes: `3,377`
     - Mean Firing Rate: `0.41 Hz`
     - Looming Threat: `False`
     - Correlated Color Temperature: Saturated color outside Planckian locus ($D_{uv} = -0.0631$, `cct_valid: False` $\rightarrow$ `N/A`)
  3. **Pure Blue** (`#0000E6`):
     - Luminance ($Y$): `0.103`
     - Network Spikes: `2,658`
     - Mean Firing Rate: `0.32 Hz`
     - Looming Threat: `False`
     - Correlated Color Temperature: Saturated color outside Planckian locus ($D_{uv} = -0.4206$, `cct_valid: False` $\rightarrow$ `N/A`)
  4. **Rapid Dark / Looming** (`#000000` following `#FFFFFF`):
     - Luminance ($Y$): `0.000` ($\Delta Y = 1.000 > 0.150$)
     - Network Spikes: `130,028`
     - Mean Firing Rate: `15.60 Hz`
     - Looming Threat: `True`
     - Correlated Color Temperature: Darkness baseline `6,500 K` (`cct_valid: False`)
- **Automated Regression**: `tests/test_benchmarks_reproducibility.py` enforces all baseline metrics within $\pm 5\%$ relative tolerance on every commit in GitHub Actions CI, and verifies that the Markdown table in `README.md` strictly reflects these exact numbers.

> **Boundary Statement**:
> *This is evidence of deterministic, reproducible network-wide spike propagation and consistent quantitative behavior across fresh cold-start engine runs. It is **NOT** evidence that the fly's full natural visual experience, perceptual consciousness, or behavioral repertoire is captured by these four artificial stimuli.*

---

## 3. Physical Correlated Color Temperature (CCT) & Planckian Locus Deviation ($D_{uv}$) — 2026-09-13

- **Identified Issue**: The previous implementation estimated color temperature using a naive heuristic `(mean_b / mean_r) * 6500`, clamped between 1,000 K and 40,000 K. This produced arbitrary temperature figures for saturated chromatic inputs without physical meaning.
- **Physical Colorimetry Implementation**:
  - Linearization of non-linear sRGB values via the standard IEC 61966-2-1 inverse companding function.
  - Projection into CIE 1931 $[X, Y, Z]$ color space using the standard sRGB transformation matrix.
  - Calculation of 2D chromaticity coordinates: $x = \frac{X}{X + Y + Z}, \quad y = \frac{Y}{X + Y + Z}$.
  - Estimation of Correlated Color Temperature via McCamy's polynomial approximation:
    $$n = \frac{x - 0.3320}{0.1858 - y}, \quad \text{CCT} = 449 n^3 + 3525 n^2 + 6823.3 n + 5520.33$$
  - Projection into CIE 1960 UCS space: $u = \frac{4x}{-2x + 12y + 3}, \quad v = \frac{6y}{-2x + 12y + 3}$.
  - Calculation of signed Euclidean distance ($D_{uv}$) from the Planckian blackbody locus using Krystek (1985) polynomial coordinates $(u_0, v_0)$:
    $$D_{uv} = \text{sgn}(v - v_0) \cdot \sqrt{(u - u_0)^2 + (v - v_0)^2}$$
  - **Blackbody Validity Gating**: If $|D_{uv}| > 0.05$, the chromaticity deviates excessively from the blackbody curve; `cct_valid` is set to `False`, and downstream consumers display `N/A — saturated color` rather than an unphysical Kelvin value.
- **Measured Verification Values**:
  - Pure White (`#FFFFFF`, sRGB D65): $x \approx 0.3127, y \approx 0.3290 \implies \text{CCT} \approx 6,504\text{ K}, D_{uv} = +0.0032$ (`cct_valid: True`).
  - Pure Red (`#C80000`): $x \approx 0.6484, y \approx 0.3309 \implies D_{uv} = -0.0631$ (`cct_valid: False`).
  - Pure Blue (`#0000E6`): $x \approx 0.1500, y \approx 0.0600 \implies D_{uv} = -0.4206$ (`cct_valid: False`).
  - Dark Frame Guard ($Y < 10^{-4}$): Returns baseline `6,500 K`, $D_{uv} = 0.0$, `cct_valid: False`.
- **Automated Regression**: 4 test cases in `tests/test_color_temperature_regression.py` verify D65 accuracy, non-blackbody rejection for saturated primaries, and zero-luminance safety guards.

> **Boundary Statement**:
> *This is evidence of physically sound radiometric-to-photometric color space transformation and blackbody Planckian locus validity gating. It is **NOT** evidence of biological fly color vision, which relies on compound eye ommatidia with five distinct rhodopsin photopigments ($Rh_1-Rh_6$) extending into the near-ultraviolet spectrum ($300-360\text{ nm}$).*

---

## 4. Giant Fiber Escape Gating & Mechanosensory Distinction — 2026-09-13

- **Identified Issue**: In biological *Drosophila*, the Giant Fiber ($GF$) escape reflex circuit integrates multimodal inputs—both lobula visual projection neurons ($LC_4, LPLC_2$) and mechanosensory sound/wind displacement signals from the Johnston's organ (antennal nerve) and halteres. The simulation previously presented the visual looming trigger without distinguishing it from biological multisensory escape gating.
- **Simulation Scope Clarification**:
  - The motor decoder (`motor_decoder.py`) implements a functional threshold on visual looming contrast collapse: $\Delta Y = Y_{\text{prev}} - Y_{\text{curr}} > 0.15$.
  - When active, an excitatory current burst is injected into $LC_4$ looming detector nodes, activating descending motor pathways and asserting the `giant_fiber_jump` flag.
  - Code comments and documentation were updated to explicitly classify this as an intentional simulation scope simplification (visual-only looming trigger) rather than full multisensory escape integration.
- **Automated Verification**: `tests/test_giant_fiber_dynamics.py` (2 passing tests):
  - Confirms `giant_fiber_jump == True` upon abrupt contrast drops ($\Delta Y = 1.0 > 0.15$).
  - Confirms `giant_fiber_jump == False` during steady-state or gradual illumination changes ($\Delta Y \le 0.15$).

> **Boundary Statement**:
> *This is evidence of a functional thresholded coupling between visual looming contrast collapse and the simulated Giant Fiber descending motor flag. It is **NOT** evidence of the full biological escape reflex, which requires mechanosensory Johnston's organ and haltere interneuron convergence absent from this visual-only sensory loop.*

---

## 5. Neuromodulator Telemetry: Firing Rate (`dopamine_hz`) vs. Chemical Concentration (`dopamine_conc_nm`) — 2026-09-13

- **Identified Issue**: The telemetry packet and dashboard contain two related dopamine metrics that could be easily conflated without explicit dimensional documentation:
  1. `dopamine_hz`: Action potential firing rate of the 15 $PAM11$ dopaminergic reward neurons (in $\text{Hz}$, spikes per second per neuron).
  2. `dopamine_conc_nm` (telemetry `dopamine_nm`): Simulated continuous extracellular dopamine concentration (in $\text{nM}$, nanomoles per liter).
- **Kinetic Model Verification**:
  - `dopamine_hz` reflects instantaneous and smoothed spiking frequency:
    $$\text{inst\_da\_hz} = \frac{\text{pam11\_spikes}}{15 \times \Delta t_{\text{sec}}}, \quad \text{smoothed\_da\_hz} = 0.7 \cdot \text{prev} + 0.3 \cdot \text{inst\_da\_hz}$$
  - `dopamine_conc_nm` is modeled via a continuous differential release and reuptake equation:
    $$[\text{DA}]_{t+\Delta t} = [\text{DA}]_{\text{baseline}} + ([\text{DA}]_t - [\text{DA}]_{\text{baseline}}) \cdot e^{-\Delta t / \tau_{\text{decay}}} + (\text{pam11\_spikes} \times k_{\text{synth}})$$
    with baseline $[\text{DA}]_{\text{baseline}} = 5.0\text{ nM}$, decay time constant $\tau_{\text{decay}} = 2000\text{ ms}$, and synthesis constant $k_{\text{synth}} = 0.05\text{ nM/spike}$.
- **Empirical Validation**:
  - Quiescent resting baseline: `dopamine_hz = 0.0 Hz`, `dopamine_conc_nm = 5.0 nM`.
  - Stimulated condition (PAM11 current injection): `dopamine_hz` spikes dynamically; `dopamine_conc_nm` rises above $5.0\text{ nM}$.
  - Recovery assay: Following cessation of stimulation, `dopamine_hz` drops immediately to $0.0\text{ Hz}$, while `dopamine_conc_nm` exhibits characteristic exponential clearance toward $5.0\text{ nM}$ ($\Delta < 0.5\text{ nM}$ within 10 seconds of simulated time).
  - Verified by `tests/test_hormones.py`.

> **Boundary Statement**:
> *This is evidence of a mathematical separation between electrophysiological spike rate and ODE-governed volume neurotransmitter release/reuptake kinetics. It is **NOT** evidence of in vivo microdialysis precision, 3D synaptic cleft diffusion dynamics, or whole-brain pharmacological receptor saturation.*

---

## 6. Validation Maintenance Protocol

All contributors and agent sessions must adhere to the following protocol when introducing significant biophysical, algorithmic, or architectural modifications:

1. **Do not fabricate or hand-tune benchmarks**: Run the automated generation scripts (`scripts/generate_benchmarks.py`) and report raw figures as measured.
2. **Document Environment & Exact Numbers**: State the date, Python version, platform, stimulus parameters, and exact numerical outputs.
3. **Mandatory Boundary Statement**: Conclude every new validation section with the explicit template:
   > *This is evidence of [exact technical capability demonstrated]; it is **NOT** evidence of [broader biological claim or unmodeled phenomenon].*
