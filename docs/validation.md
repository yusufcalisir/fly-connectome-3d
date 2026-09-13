# Local model validation

Verified on 2026-09-13 with Python 3.12.11, Windows x64, and the committed `uv.lock` dependency environment.

This document records empirical verification milestones, exact measurements, and explicit boundary statements defining what each test proves and what it does **not** prove. Future significant model changes or regressions must append a dated section to this log.

---

## 1. Initial Model & Connectome Dataset Integrity Verification — 2026-09-10

- **Dataset Provenance**: Janelia Research Campus **MaleCNS v1.0** serial-section transmission electron microscopy (ssTEM) dataset.
- **Graph Dimensions**: 166,700 reconstructed neurons and 25,582,938 directed synaptic connections.
- **Soma Morphology**: 141,781 3D $[X, Y, Z]$ soma coordinates extracted, normalized into Three.js anatomical space, and serialized into `soma_coordinates_141k.bin` (2.55 MB binary array).
- **Photoreceptor Display Adapter**: 3,335 mapped $R_1-R_6$ outer and 811 mapped $R_8$ inner inputs are modeled as spiking LIF units with depolarizing current injection to interface with the spiking graph engine. In biological *Drosophila*, photoreceptors and laminar monopolar cells are graded-potential systems that do not fire action potentials; this is an explicit display adapter, not validated retinal electrophysiology.
- **Dale's Principle E/I Polarity**: All 166,700 cells classified by predicted neurotransmitter:
  - Acetylcholine ($ACh$): Excitatory ($w > 0$, depolarizing EPSPs).
  - GABA, Glutamate, Histamine: Inhibitory ($w < 0$, hyperpolarizing IPSPs).
- **Numerical Clamping**: Potassium reversal potential clamped at $V_{\text{clamp}} = -85.0\text{ mV}$ to prevent numerical run-away hyperpolarization under dense inhibition.
- **Automated Verification**: 87 passing automated tests across unit, biophysical integration, and full-graph connectivity suites.

> **Boundary Statement**:
> *This is evidence of structural graph integrity, 3D coordinate normalization, and numerical stability in the vectorized Leaky Integrate-and-Fire (LIF) kernel. It is **NOT** evidence of biological intracellular voltage dynamics, dendritic compartmentalization, true graded retinal/laminar physiology, or complete whole-organism functional fidelity.*

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
  1. `dopamine_hz`: Action potential firing rate of the 15 $PAM11$ dopaminergic neurons (in $\text{Hz}$, spikes per second per neuron).
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

## 6. Neurotransmitter Polarity Assignment & E/I Balance Verification — 2026-09-13

- **Dataset Provenance**: Janelia Research Campus MaleCNS v1.0 (`neurotransmitters.feather`, `annotations.feather`, `synapses.feather`).
- **Population Scope**: All 166,700 retained neurons and 25,582,938 directed synaptic connections in the compiled connectome graph (`malecns_v1_graph.npz`).
- **Identified Questions**:
  1. How much of the whole-brain neurotransmitter polarity assignment relies on an unlabeled fallback default (`else: +1.0`) versus empirical predictions?
  2. What is the true out-of-sample machine learning accuracy versus ground truth?
  3. Does the observed 100% agreement of `consensus_nt` with `ground_truth` represent independent cross-validation or a construction formula?

### Empirical Distribution by Neurotransmitter Category

| Neurotransmitter Category | Assigned Sign | Neuron Count | % Neurons | Synaptic Edges | % Edges | Synaptic Weight | % Weight |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Acetylcholine** ($ACh$) | $+1.0$ (Excitatory) | 103,720 | 62.22% | 14,745,137 | 57.64% | 71,847,949 | 57.86% |
| **Glutamate** ($Glu$) | $-1.0$ (Inhibitory) | 29,302 | 17.58% | 4,798,718 | 18.76% | 23,266,488 | 18.74% |
| **GABA** | $-1.0$ (Inhibitory) | 22,069 | 13.24% | 4,925,557 | 19.25% | 23,732,965 | 19.11% |
| **Histamine** | $-1.0$ (Inhibitory) | 7,891 | 4.73% | 89,723 | 0.35% | 454,767 | 0.37% |
| **Unclear / Ambiguous** | $+1.0$ (Default) | 2,999 | 1.80% | 588,262 | 2.30% | 2,829,380 | 2.28% |
| **Missing in NT Table** | $+1.0$ (Default) | 178 | 0.11% | 0 | 0.00% | 0 | 0.00% |
| **Dopamine** | $+1.0$ (Modulatory) | 392 | 0.24% | 241,694 | 0.94% | 1,180,684 | 0.95% |
| **Octopamine** | $+1.0$ (Modulatory) | 101 | 0.06% | 148,519 | 0.58% | 639,521 | 0.51% |
| **Serotonin** | $+1.0$ (Modulatory) | 48 | 0.03% | 45,328 | 0.18% | 225,858 | 0.18% |
| **Total Retained Network** | — | **166,700** | **100.00%** | **25,582,938** | **100.00%** | **124,177,612** | **100.00%** |

### Polarity Aggregation & E/I Balance

- **Excitatory (+1.0)**: **107,438 neurons (64.45%)** | **15,768,940 edges (61.64%)** | **76,723,392 weight (61.78%)**
- **Inhibitory (-1.0)**: **59,262 neurons (35.55%)** | **9,813,998 edges (38.36%)** | **47,454,220 weight (38.22%)**
- **Broad Consistency**: This distribution is broadly consistent with typical insect CNS excitatory-dominant proportions without fabricating unverified external literature percentage ranges.

### ML Accuracy vs. Ground Truth & Pipeline Construction

- **Ground Truth Coverage**: 85,484 of the 166,700 neurons (51.28%) have verified biological ground truth annotations in MaleCNS v1.0.
- **Tautology / Formula by Construction**: In Janelia's pipeline, `consensus_nt` is computed as `ground_truth if not null else predicted_nt`. As a result, `consensus_nt == ground_truth` is 85,484 / 85,484 (100.00%) **by definition / override**, not an independent cross-validation.
- **True Independent ML Accuracy**: Directly comparing Janelia's machine-learning classifier (`predicted_nt`) against verified biological annotations (`ground_truth`) across all 85,484 ground truth neurons:
  - **Matches (`predicted_nt == ground_truth`)**: **75,747 / 85,484 = 88.61% accuracy**
  - **Mismatches (`predicted_nt != ground_truth`)**: 9,737 / 85,484 = 11.39% mismatch
- **Default Fallback Impact & Sensitivity Analysis**:
  - Exactly **3,177 neurons (1.91%)** hit the default-excitatory branch (2,999 with ambiguous calls like `acetylcholine / glutamate` or `unclear`, plus 178 unannotated neurons with 0 synaptic connections).
  - These default neurons represent only **2.30% of synaptic connections** (588,262 / 25,582,938) and **2.28% of synaptic weight** (2,829,380 / 124,177,612).
  - Under a worst-case counterfactual bound where 100% of these 3,177 ambiguous neurons are treated as inhibitory instead of excitatory:
    - Excitatory neurons: 104,261 (62.54%)
    - Inhibitory neurons: 62,439 (37.46%)
    - Maximum E/I shift: $\pm 1.91\%$ at the neuron level, $\pm 2.30\%$ at the edge level.
  - The fallback default has a negligible influence on whole-brain excitation/inhibition balance.

> **Boundary Statement**:
> *This is evidence of the quantitative breakdown, ML prediction accuracy (88.61%), and minimal sensitivity ($\le 1.91\%$) of the default fallback in the MaleCNS v1.0 neurotransmitter polarity assignment. It is **NOT** evidence of dynamic multi-transmitter co-transmission, postsynaptic receptor subtype variation (e.g. excitatory vs. inhibitory glutamate receptor distributions at individual synapses), or metabolic neurotransmitter turnover in living tissue.*

---

## 7. Synaptic Plasticity Saturation & Exponential Decay Verification — 2026-09-13

- **Identified Issue**: Under repeated stimulus presentations with active dopamine drive, `plasticity_index` (`HormoneDynamicsEngine.learned_weight_drift`) exhibited unbounded linear growth without saturation or decay (+0.345 per 50 ms step, reaching 7.0930 at step 20). When stimulation ceased, the index froze permanently without active forgetting or relaxation toward baseline.
- **Underlying Weight Array Integrity Check**: The 25,582,938-edge sparse CSR synaptic weight matrix in `LIFKernel` is static and was never mutated by `plasticity_index` ($\sum w = 29,269,178.0$, 0 NaNs, 0 Infs). The scalar is a macroscopic phenomenological telemetry index of associative potentiation between Kenyon Cells ($KC$) and Mushroom Body Output Neurons ($MBON$).
- **Mechanism Implementation**:
  1. **Homeostatic Saturation Ceiling** ($P_{\text{max}} = 2.00$): Implemented soft-headroom gain scaling $(1 - P_t / P_{\text{max}})$. Under sustained pairing, marginal potentiation diminishes smoothly as the index approaches the biological doubling ceiling of $2.00$, preventing unbounded divergence.
  2. **Passive Exponential Decay (Active Forgetting)** ($\tau_{\text{plasticity\_decay}} = 10,000\text{ ms}$): In the absence of continued stimulation, the index decays exponentially toward zero via $e^{-\Delta t / \tau_{\text{decay}}}$, relaxing back to baseline ($P \rightarrow 0.0$).
- **Engineering Choice & Parameter Calibration Note**: $\tau_{\text{ms}} = 10,000$ and $P_{\text{max}} = 2.0$ are engineering choices to keep the metric bounded and observable within a single session; they are not derived from a specific measured biological time constant. Real biological memory forgetting curves in *Drosophila* behavioral experiments operate across minutes to hours (e.g., 5 min to 24 hr in active forgetting protocols), not interactive 50 ms simulation chunks.
- **20-Stimulus Stress Test (MaleCNS v1.0 Connectome)**:
  Measured across 20 consecutive 50 ms visual presentations with active dopamine drive, followed by 10 quiescent relaxation steps:

| Step | Unbounded Baseline (Before) | Homeostatic Saturation (After) | Status | Firing Rate ($Hz$) |
| :---: | :---: | :---: | :---: | :---: |
| **1** | 0.4122 | **0.4122** | Initial potentiation | 14.83 |
| **2** | 0.8014 | **0.7195** | Diminishing gain | 21.07 |
| **3** | 1.1755 | **0.9561** | Diminishing gain | 21.57 |
| **4** | 1.5395 | **1.1422** | Diminishing gain | 21.78 |
| **5** | 1.8970 | **1.2909** | Diminishing gain | 21.47 |
| **6** | 2.2502 | **1.4108** | Diminishing gain | 21.43 |
| **7** | 2.6005 | **1.5082** | Diminishing gain | 21.70 |
| **8** | 2.9489 | **1.5877** | Diminishing gain | 21.27 |
| **9** | 3.2961 | **1.6527** | Diminishing gain | 21.40 |
| **10** | 3.6424 | **1.7060** | Diminishing gain | 21.26 |
| **11** | 3.9882 | **1.7498** | Asymptotic approach | 21.32 |
| **12** | 4.3337 | **1.7858** | Asymptotic approach | 20.77 |
| **13** | 4.6789 | **1.8154** | Asymptotic approach | 21.49 |
| **14** | 5.0239 | **1.8398** | Asymptotic approach | 21.63 |
| **15** | 5.3689 | **1.8598** | Asymptotic approach | 21.70 |
| **16** | 5.7138 | **1.8763** | Asymptotic approach | 21.48 |
| **17** | 6.0586 | **1.8899** | Asymptotic approach | 21.57 |
| **18** | 6.4035 | **1.9011** | Asymptotic approach | 21.47 |
| **19** | 6.7483 | **1.9103** | Asymptotic approach | 21.02 |
| **20** | 7.0930 | **1.9179** | Bounded ($\le 2.00$) | 21.30 |

- **Quiescent Decay Phase (Post-Stimulation Relaxation)**:
  - $t = 500\text{ ms}$: `1.8243`
  - $t = 1,500\text{ ms}$: `1.6507`
  - $t = 3,000\text{ ms}$: `1.4208`
  - $t = 5,000\text{ ms}$ ($0.5\tau$): `1.1632` ($1.9179 \times e^{-0.5} = 1.1632$)
  - Verified by unit test suite `tests/test_plasticity_bounds.py` (3 passing tests).

> **Boundary Statement**:
> *This is evidence of a mathematically bounded, homeostatically saturated, and exponentially decaying macroscopic associative plasticity index in the neuromodulatory engine. It is **NOT** evidence of synapse-specific spike-timing-dependent plasticity (STDP), biophysically resolved dendritic compartmentalization, or individual synaptic conductance rewiring across the 25.6M connectome edges.*

---

## 8. Dopaminergic Modulation & Wirehead Boundary Clarification — 2026-09-13

- **Context & Motivation**: In *Drosophila* neurobiology, PAM-cluster dopaminergic neurons project to specific compartments of the mushroom body to modulate synaptic plasticity during associative olfactory and visual conditioning. In computational models and the `/api/wirehead` interactive endpoint, depolarizing current ($+20\text{ mV}$) is injected into the 15 identified $PAM11$ neurons, increasing simulated dopamine firing rate (`dopamine_hz`), extracellular concentration (`dopamine_conc_nm`), and Kenyon Cell $\to$ MBON associative drift (`learned_knowledge_index`).
- **Clarification & Scoping Audit**:
  - Language implying subjective states ("pleasure", "appetitive enjoyment", "addiction") was audited across documentation, REST API docstrings, telemetry descriptions, and frontend tooltips.
  - All readouts are explicitly scoped to the physiological quantities modeled:
    1. `dopamine_hz`: Electrophysiological action potential firing rate of the 15 $PAM11$ neurons (Hz).
    2. `dopamine_conc_nm`: Synthesized volume-averaged extracellular dopamine concentration under 1st-order DAT clearance ODE kinetics (nM).
    3. `learned_knowledge_index`: Cumulative dopamine-gated weight drift between Kenyon Cells and mushroom body output neurons.
  - The `/api/wirehead` endpoint is documented as a numerical current-injection stimulation check. No living organism is involved, and behavioral preference, subjective valence, or addiction have not been established.

> **Boundary Statement**:
> *These are numerical stimulation checks, ODE concentration models, and dopamine-gated weight modulations. They are **NOT** evidence of pleasure, subjective reward, hedonic valence, or learned preference.*

---

## 9. MaleCNS v1.0 Data Provenance & Cryptographic Integrity Verification — 2026-09-13

- **Distribution Source**: Howard Hughes Medical Institute / Janelia Research Campus (FlyEM Team) public Google Cloud Storage bucket (`storage.googleapis.com/flyem-male-cns/v1.0/connectome-data/flat-connectome/`), documented on the canonical dataset page `male-cns.janelia.org/download`.
- **GCS Bucket XML Listing & Verbatim ETags**:
  - `body-annotations-male-cns-v1.0-minconf-0.5.feather`:
    - Size: `14483314` bytes
    - Verbatim XML `<ETag>`: `"50a7718770c57220f160ba4f431ab89e"`
    - GCS Header: `x-goog-hash: md5=UKdxh3DFciDxYLpPQxq4ng==`
  - `body-neurotransmitters-male-cns-v1.0.feather`:
    - Size: `43282834` bytes
    - Verbatim XML `<ETag>`: `"3d842b12fe5c49eefade528d7dd24a1f"`
    - GCS Header: `x-goog-hash: md5=PYQrEv5cSe763lKNfdJKHw==`
  - `connectome-weights-male-cns-v1.0-minconf-0.5.feather`:
    - Size: `1051241946` bytes
    - Verbatim XML `<ETag>`: `"f30e9dcca25cfd021bf1e7b3d975599e"`
    - GCS Header: `x-goog-hash: md5=8w6dzKJc/QIb8eez2XVZng==`
- **Hash Algorithm Reconciliation & Verification**:
  - **ETag Structure**: The ETags returned by GCS are standard 32-character hexadecimal strings representing the 128-bit **MD5** digest of the object (single-part non-composite upload). They are not composite `hash-N` multipart digests. Base64 decoding of `x-goog-hash: md5` confirms exact hex equivalence with the XML `<ETag>`.
  - **Algorithm Distinction**: Directly comparing a local SHA-256 hash to a GCS MD5 ETag is mathematically invalid.
  - **Local vs. Remote Hash Match**: Computing the exact MD5 hash of the downloaded local files confirms an identical match to Janelia's GCS ETags:
    - `annotations.feather`: Local MD5 `50a7718770c57220f160ba4f431ab89e` $\equiv$ Remote ETag `"50a7718770c57220f160ba4f431ab89e"`.
    - `neurotransmitters.feather`: Local MD5 `3d842b12fe5c49eefade528d7dd24a1f` $\equiv$ Remote ETag `"3d842b12fe5c49eefade528d7dd24a1f"`.
    - `edges.feather`: Local MD5 `f30e9dcca25cfd021bf1e7b3d975599e` $\equiv$ Remote ETag `"f30e9dcca25cfd021bf1e7b3d975599e"`.
  - **Byte Sizes**: Exact 1-to-1 byte match across all three tables (14,483,314; 43,282,834; 1,051,241,946 bytes).

> **Boundary Statement**:
> *This is evidence of exact byte-level file provenance and cryptographic MD5 integrity against Janelia's official MaleCNS v1.0 Google Cloud Storage distribution bucket. It is **NOT** evidence of automated runtime checksum validation in `downloader.py` (which currently trusts downloaded file streams upon fetch) or EM segmentation perfection.*

---

## 10. Leg Motor Neuron Reconciliation: Connectome Reconstruction vs. Classical Electrophysiology — 2026-09-13

- **Context & Investigated Question**: The project claims 381 leg motor neurons across the three thoracic neuromeres ($T_1$: 135, $T_2$: 116, $T_3$: 130). Classical literature on *Drosophila* leg motor control (e.g. Azevedo & Tuthill et al., 2020 *eLife*, DOI: [10.7554/eLife.56754](https://doi.org/10.7554/eLife.56754)) cited ~53 motor neurons per leg. How do these numbers reconcile with Janelia's MaleCNS v1.0 and whole-VNC EM connectome publications?
- **Anatomical Scope Discrepancy Resolved**:
  - The ~53 motor neurons per leg figure from Azevedo & Tuthill (2020) (citing Baek & Mann 2009; Brierley et al. 2012; Maniates-Selvin et al. 2020; Soler et al. 2004) counted **only the motor neurons innervating the 14 intrinsic muscles** confined within leg segments (coxa, trochanter, femur, tibia, tarsus).
  - In modern whole-VNC electron microscopy reconstruction, Cheong et al. 2024 (*eLife*, DOI: [10.7554/eLife.96084](https://doi.org/10.7554/eLife.96084)) analyzed the complete motor output system and demonstrated that each limb is additionally controlled by **5 extrinsic thoracic muscles that insert into the leg** (tergotrochanteral jump muscle, sternal rotators, pleural promotors/remotors):
    > *"Each leg contains 14 muscles confined within the proximal leg segments, and another five in the thorax that insert in the leg (Azevedo et al., 2024; Brierley et al., 2012). These leg muscles are estimated to be innervated by around 70 MNs in each leg, that originate from ~15 hemilineages... Overall, in the MANC dataset, we find 392 leg MNs (142 in T1, 119 in T2, 131 in T3)."*
- **Reconciliation Table**:

| Neuromere Segment | Cheong et al. 2024 (MANC) | MaleCNS v1.0 (`fl`/`ml`/`hl`) | Left Side ($L$) | Right Side ($R$) | Per-Leg Average | Delta vs MANC |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **$T_1$ (Front Legs)** | 142 | **135** | 68 | 67 | 67.5 | -7 |
| **$T_2$ (Middle Legs)** | 119 | **116** | 58 | 58 | 58.0 | -3 |
| **$T_3$ (Hind Legs)** | 131 | **130** | 66 | 64 | 65.0 | -1 |
| **Total** | **392** | **381** | **192** | **189** | **63.5** | **-11 (-2.8%)** |

- **Origin of the 2.8% Delta (-11 neurons)**:
  - In [compile_malecns.py](file:///d:/brain/src/connectome_engine/data/compile_malecns.py), filtering relies strictly on Janelia's official annotation hierarchy: `superclass == 'vnc_motor'` and `subclass in ['fl', 'ml', 'hl']`.
  - All 381 neurons exit via canonical peripheral leg nerves (`ProLN`, `ProAN`, `VProN`, `DProN`, `MesoLN`, `MetaLN`, and `AbN1`).
  - The 11-neuron difference reflects borderline extra motor neurons (`xm`, 6 neurons across T1/T2: `MNxm01`, `MNxm02`, `MNxm03`) and 5 unclassified thoracic efferents in Janelia's v1.0 release table that lack explicit `fl`/`ml`/`hl` subclass tags.

> **Boundary Statement**:
> *This is evidence that the 381 leg motor neurons modeled in this project represent verified anatomical reconstructions from Janelia MaleCNS v1.0, and that the count aligns with full EM connectomic reconstructions (~70 MNs/leg including thoracic extrinsic leg muscles) rather than older intrinsic-only (53 MNs/leg) estimates. It is **NOT** evidence that all muscle insertions or neuromuscular junction biomechanics are modeled with individual muscle-fiber resolution.*

---

## 11. Validation Maintenance Protocol

All contributors and agent sessions must adhere to the following protocol when introducing significant biophysical, algorithmic, or architectural modifications:

1. **Do not fabricate or hand-tune benchmarks**: Run the automated generation scripts (`scripts/generate_benchmarks.py`) and report raw figures as measured.
2. **Document Environment & Exact Numbers**: State the date, Python version, platform, stimulus parameters, and exact numerical outputs.
3. **Mandatory Boundary Statement**: Conclude every new validation section with the explicit template:
   > *This is evidence of [exact technical capability demonstrated]; it is **NOT** evidence of [broader biological claim or unmodeled phenomenon].*
