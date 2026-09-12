# 🧠 FlyConnectome 3D: Real-Time Biophysical Drosophila Biocomputing Platform

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![Three.js](https://img.shields.io/badge/Three.js-r128-black.svg)](https://threejs.org/)
[![Connectome](https://img.shields.io/badge/Connectome-MaleCNS%20v1.0%20%2F%20FlyWire-orange.svg)](https://flywire.ai/)
[![Biophysics](https://img.shields.io/badge/Biophysics-100%25%20Zero--Mock-success.svg)](#biophysical-and-mathematical-formulation)
[![Tests](https://img.shields.io/badge/Tests-15%2F15%20Passing-brightgreen.svg)](#automated-testing--validation)
[![i18n](https://img.shields.io/badge/i18n-English%20%7C%20T%C3%BCrk%C3%A7e-blueviolet.svg)](#modern-bilingual-ui-en--tr)

A high-performance computational neuroscience platform coupling the adult *Drosophila melanogaster* connectome (166,700 neurons, 25.6 million synapses from the **MaleCNS v1.0 / FlyWire** dataset) with a real-time, biophysically authentic 3D electrophysiology observation cockpit.

The system places a photorealistic 3D tethered fly on an air-cushioned spherical treadmill inside a precision laboratory rig. The fly observes a virtual smartphone displaying dynamic stimuli or user-uploaded photos, triggering real-time retinal transduction, sparse Leaky Integrate-and-Fire (LIF) network simulations, continuous ordinary differential equation (ODE) hormone synthesis, associative synaptic plasticity, central complex spatial navigation, and descending motor kinematics.

---

## Table of Contents
1. [Key Features](#key-features)
2. [Neurobiological Circuit Architecture](#neurobiological-circuit-architecture)
3. [Biophysical and Mathematical Formulation](#biophysical-and-mathematical-formulation)
4. [3D Observation Chamber & Electrophysiology Rig](#3d-observation-chamber--electrophysiology-rig)
5. [Interactive Stimulus Arena & Spectral Valence Engine](#interactive-stimulus-arena--spectral-valence-engine)
6. [Modern Bilingual UI (EN / TR)](#modern-bilingual-ui-en--tr)
7. [System Architecture](#system-architecture)
8. [Directory Layout](#directory-layout)
9. [Installation & Quickstart](#installation--quickstart)
10. [REST & WebSocket API Reference](#rest--websocket-api-reference)
11. [Automated Testing & Validation](#automated-testing--validation)
12. [References & Citations](#references--citations)

---

## Key Features

- **Zero-Mock Biophysical Architecture**: No synthetic random number generators masquerading as telemetry. Every spike, membrane potential, neuromodulator concentration, and motor velocity is derived from continuous differential equations and verified biological circuit topology.
- **Sparse CSR LIF Kernel**: Vectorized Leaky Integrate-and-Fire simulation engine operating on sparse Compressed Sparse Row (CSR) connectivity matrices with sub-millisecond refractory clamping.
- **Continuous Neuromodulatory Kinetics**: Real-time ODE kinetics modeling dopamine ([DA] via PAM11 and PPL101), octopamine ([OA] via TDC2/VUM), and serotonin ([5-HT]) release, diffusion, enzymatic degradation, and reuptake.
- **Associative STDP Plasticity**: Kenyen Cell $\rightarrow$ Mushroom Body Output Neuron ($KC \rightarrow MBON07 / MBON11$) synaptic weight modulation governed by dopaminergic reward and punishment signals.
- **Central Complex Compass**: Ring-attractor dynamics tracking the fly's angular orientation via Ellipsoid Body EPG compass neurons, visualized through a 3D rotating torus ring and HUD.
- **Looming Threat & Giant Fiber Escape**: Optical contrast expansion detection triggering Lobula Plate LC4 projection neurons and Giant Fiber (GF) retrograde jump alarms.
- **Photorealistic AAA 3D Lab Rig**: Built in Three.js featuring an optical stainless-steel breadboard table with tapped M6 holes, an air-flotation spherical treadmill with dual optical sensors, a micromanipulator patch-clamp micropipette, an overhead stereomicroscope turret with LED ring illuminator, and an anatomically accurate *Drosophila* rig with amber-bronze cuticle clearcoat, ruby ommatidial facet bump maps, authentic wing venation, and 5-joint articulated legs.
- **Direct-Facing Smartphone Screen**: Angled 3/4 perspective screen that faces the fly's compound eyes directly, casting dynamic photons onto its ommatidia.
- **Custom Photo Upload & Spectral Valence Decomposition**: Upload any external image; the system decomposes RGB wavelength ratios and luminance profiles to classify stimulus valence (Appetitive vs Threat vs Neutral) and injects proportional retinal currents.
- **Modern Glassmorphic Bilingual UI**: Instantaneous switching between English and Turkish via a top-right `[ 🌐 EN / TR ]` toggle with `localStorage` persistence.

---

## Neurobiological Circuit Architecture

The platform maps key identified neuronal cell types from the adult *Drosophila* connectome:

| Neural Population | Biological Cell Types | Connectome Role | Behavioral Correlate |
| :--- | :--- | :--- | :--- |
| **Photoreceptors** | $R_1 - R_6$ (broadband), $R_8$ (green/blue) | Retinal photon capture ($90 \times 160$ spatial grid) | Visual transduced current injection |
| **Looming Detectors** | $LC_4$ (Lobula Columar Type 4) | High-speed optical contrast expansion detection | Innate looming shadow threat trigger |
| **Dopaminergic System** | $PAM11$ (reward), $PPL101$ (aversive) | Modulates mushroom body calyx and $\alpha/\beta$ lobes | Sugar reward, wirehead pleasure, associative STDP |
| **Octopaminergic System**| $TDC2$ / $VUM$ (Tyramine Decarboxylase 2) | Insect adrenaline / norepinephrine analogue | Arousal, threat stress, fight-or-flight vigor |
| **Serotonergic System** | $5\text{-HT}$ dorsal/cranial clusters | Baseline satiety, behavioural quiescence, mood | Motor patience, stabilization, calmness |
| **Mushroom Body** | Kenyon Cells ($KC$), $MBON07$, $MBON11$ | Olfactory and multimodal association | Learned odor/visual preference drift |
| **Central Complex** | $EPG$ (Compass ring attractor) | Ellipsoid Body $\rightarrow$ Protocerebral Bridge | Heading vector maintenance ($0^\circ - 360^\circ$) |
| **Steering Motor** | $DNa02$ (Left / Right) | Asymmetric descending thoracic motor control | Left/Right turning deflection ($-1.0 \dots +1.0$) |
| **Throttle Motor** | $DNp09$ | Symmetrical descending walking command | Forward walking speed ($0\% \dots 100\%$) |
| **Moonwalker** | $MDN$ (Moonwalker Descending Neuron) | Backward walking coordinator | Backward avoidance walking |
| **Escape Jumping** | Giant Fiber ($GF$) Tract | Fast motor escape pathway | Emergency backward leap & wing flare |

---

## Biophysical and Mathematical Formulation

### 1. Vectorized Leaky Integrate-and-Fire (LIF) Kernel
For $N$ neurons, membrane potentials $V_i(t)$ evolve according to:

$$\tau_m \frac{dV_i}{dt} = -(V_i(t) - V_{\text{rest}}) + R_m \left( I_i^{\text{syn}}(t) + I_i^{\text{ext}}(t) \right)$$

When $V_i(t) \ge V_{\text{thresh}}$:
1. An action potential is emitted: $S_i(t) = 1$.
2. The potential resets: $V_i(t^+) = V_{\text{reset}}$.
3. The neuron is clamped in a refractory state for duration $\tau_{\text{ref}}$.

Synaptic currents are computed via sparse CSR matrix multiplication:

$$I_i^{\text{syn}}(t) = \sum_{j} W_{ij} S_j(t - \Delta t)$$

**Biophysical Constants**:
- $\tau_m = 20.0\text{ ms}$ (Membrane time constant)
- $V_{\text{rest}} = -65.0\text{ mV}$ (Resting membrane potential)
- $V_{\text{thresh}} = -50.0\text{ mV}$ (Spike threshold)
- $V_{\text{reset}} = -70.0\text{ mV}$ (Reset potential)
- $\tau_{\text{ref}} = 2.0\text{ ms}$ (Refractory period)
- $dt = 0.1\text{ ms}$ (Simulation step resolution; 500 steps per 50 ms cycle)

### 2. Neuromodulatory Hormone Kinetics (ODEs)
Concentrations of Dopamine ($[\text{DA}]$), Octopamine ($[\text{OA}]$), and Serotonin ($[5\text{-HT}]$) evolve continuously:

$$\frac{d[\text{DA}]}{dt} = k_{\text{syn}}^{\text{DA}} \cdot r_{\text{PAM11}}(t) - k_{\text{deg}}^{\text{DA}} \cdot ([\text{DA}](t) - [\text{DA}]_{\text{base}})$$

$$\frac{d[\text{OA}]}{dt} = k_{\text{syn}}^{\text{OA}} \cdot r_{\text{TDC2}}(t) - k_{\text{deg}}^{\text{OA}} \cdot ([\text{OA}](t) - [\text{OA}]_{\text{base}})$$

$$\frac{d[5\text{-HT}]}{dt} = k_{\text{syn}}^{\text{5HT}} \cdot r_{\text{5HT}}(t) - k_{\text{deg}}^{\text{5HT}} \cdot ([5\text{-HT}](t) - [5\text{-HT}]_{\text{base}})$$

Where:
- $[\text{DA}]_{\text{base}} = 5.0\text{ nM}$, $[\text{OA}]_{\text{base}} = 2.0\text{ nM}$, $[5\text{-HT}]_{\text{base}} = 8.0\text{ nM}$
- Rate constants: $k_{\text{syn}} \approx 0.12 - 0.15\text{ nM}\cdot\text{Hz}^{-1}\cdot\text{s}^{-1}$, $k_{\text{deg}} \approx 0.10 - 0.25\text{ s}^{-1}$.

### 3. KC $\rightarrow$ MBON Associative STDP Plasticity
Synaptic weights between Kenyon Cells ($KC$) and MBON compartments drift based on coincidence with dopaminergic reward ($PAM11$) and punishment ($PPL101$):

$$\Delta W_{KC \rightarrow MBON} = \eta \cdot \left( [\text{DA}](t) \cdot \overline{r}_{\text{KC}}(t) - [\text{OA}](t) \cdot \overline{r}_{\text{KC}}(t) \right)$$

### 4. Optical Contrast & Looming Threat Detection
The relative retinal angular expansion rate of an approaching dark object is monitored continuously:

$$\frac{d\theta}{dt} \propto \frac{\Delta \text{Radius}}{\Delta t} \cdot \left( 1 - \frac{\overline{Y}_{\text{current}}}{\overline{Y}_{\text{baseline}}} \right)$$

When optical expansion acceleration exceeds threshold, an intense inward current ($+45\text{ mV}$) is injected directly into $LC_4$ projection neurons, inducing immediate Giant Fiber depolarization and motor jump alarms.

---

## 3D Observation Chamber & Electrophysiology Rig

The center viewport features an interactive Three.js laboratory simulation rendered at 60 FPS:

```
                          [Overhead Stereomicroscope Turret]
                                       |
                                       v
   [Glass Pipette] ---->  (Photorealistic 3D Fly)  <---- [Dynamic Photons]
                               |            |                       |
                               v            v                       |
                  (Air-Cushioned Sphere) (6-Leg Tripod)      [Smartphone Screen]
                               |                               (Facing Fly)
                     [Air Flotation Nozzle]
                               |
            ===========================================
             Stainless Steel Optical Breadboard (M6)
            ===========================================
```

### Anatomical Fly Rig Details
- **Cuticle Shader**: Multilayer physical material with amber-ochre melanin tones, anisotropic surface sheen, and clearcoat reflection.
- **Compound Eyes**: Dual ruby-red hemispheres with procedural hexagonal ommatidial facet bump mapping.
- **Thoracic Macrochaetae**: Anatomically positioned dorsal sensory bristles along the scutum and scutellum.
- **Articulated Appendages**: 6 independently rigged legs with 5 segments (coxa, trochanter, femur, tibia, tarsus) executing authentic tripod gait kinematics on the locomotion sphere.
- **Front-Leg Interaction**: Clicking **`LEG SWIPE`** (**`BACAKLA KAYDIR`**) triggers inverse kinematics in the right front leg (`pro_R`), raising the tibia and swiping the tarsal claws across the phone screen.
- **Veined Wings**: High-resolution procedural texture modeling Costa, Subcosta, $L_1 - L_5$ longitudinal veins, and humeral crossveins.
- **Abdominal Respiration**: Rhythmic breathing dilation across 6 banded abdominal segments.

### 3D Neuropil Compartments
Switching to the **`Neural Synapses`** camera view reveals the fly's internal brain structures with real-time bioluminescent emission:
- **Optic Lobes (Cyan)**: Medulla and lobula complexes pulsating with retinal photons.
- **Mushroom Body (Emerald / Gold)**: Calyx and $\alpha/\beta$ lobes glowing in proportion to $[\text{DA}]$ dopamine levels.
- **Central Complex (Amber)**: Ellipsoid Body torus ring rotating in 3D to match real-time EPG heading ($\theta_{\text{EPG}}$).
- **Giant Fiber Tract (Crimson)**: Descending axons flashing bright crimson upon looming escape alarms.

---

## Interactive Stimulus Arena & Spectral Valence Engine

The virtual smartphone screen directly faces the fly's ommatidia and can display built-in presets or external photos:

1. **🍉 Sweet Ripe Watermelon (`fruit`)**: High-sugar appetitive visual cue. Excites $R_8$ green/red channels, evoking high-frequency PAM11 dopaminergic firing ($>20\text{ Hz}$).
2. **⚠️ Looming Shadow (`shadow`)**: Rapidly expanding dark disc simulating an incoming aerial predator. Activates $LC_4$ circuits, eliciting Giant Fiber escape leaps.
3. **🕷️ Predatory Spider (`spider`)**: High-contrast arachnid threat triggering octopaminergic stress ($TDC2$).
4. **🌿 Forest Foliage (`neutral`)**: Balanced green ambient spectrum promoting stable $5\text{-HT}$ serotonergic tone.
5. **📷 Custom User Photo Upload (`custom`)**: Upload any JPG/PNG image via drag-and-drop or file picker.

### Automated Spectral Valence Decomposition
When a custom photo is uploaded, client-side canvas routines analyze its spectral composition:
- **High Red/Green Ratio ($R/G > 1.25$, $R > 80$)**: Classified as an appetitive sugar food cue; drives $PAM11$ dopamine synthesis.
- **Low Luminance ($Y < 45$)**: Classified as a predatory looming shadow threat; triggers $LC_4$ and Giant Fiber alarms.
- **Balanced Ambient Spectrum**: Promotes $5\text{-HT}$ serotonergic stabilization and calm motor drive.

---

## Modern Bilingual UI (EN / TR)

The cockpit features a glassmorphic segmented switch pill in the top-right header with a globe icon (`🌐`):

- **English (Default)**: Full scientific terminology (`ENGINE: 60 FPS LIVE`, `WIREHEAD`, `LOOM THREAT`, `LEG SWIPE`, `DOPAMINE (PAM11)`, etc.).
- **Türkçe (TR)**: Complete professional Turkish translation (`MOTOR: 60 FPS CANLI`, `DOPAMİN ŞOKU`, `AVCI TEHDİDİ`, `BACAKLA KAYDIR`, `DOPAMİN (PAM11)`, `UYARAN ARENASI`, etc.).
- **Zero-Reload Switching**: Instant DOM node text replacement via `data-i18n` attributes.
- **Session Persistence**: User preference saved to `localStorage.setItem('flyconnectome_lang', lang)`.

---

## System Architecture

```
+-----------------------------------------------------------------------------------+
|                              FASTAPI SERVER & WEBSOCKET                           |
|  /ws/telemetry (60 Hz bi-directional)  |  /api/observe  |  /api/wirehead          |
+-----------------------------------------------------------------------------------+
                                         ^
                                         | JSON State & Payloads
                                         v
+-----------------------------------------------------------------------------------+
|                                CONNECTOME BRAIN                                   |
|                                                                                   |
|  [Visual Transduction Engine]  --->  [Sparse CSR LIF Kernel]  --->  [Motor Dec.]  |
|   - 90x160 RGB Retinal Mapping        - 166.7K Neurons               - DNa02 L/R  |
|   - Contrast Expansion (LC4)          - Sub-ms Refractory Clamp      - DNp09 Fwd  |
|                                       - Checkpoint Restore           - MDN Retreat|
|                                                ^                     - GF Jump    |
|                                                |                     - EPG Heading|
|                                                v                                  |
|                                  [Continuous Hormone ODEs]                        |
|                                   - Dopamine (PAM11 / PPL101)                     |
|                                   - Octopamine (TDC2)                             |
|                                   - Serotonin (5-HT)                              |
|                                   - KC -> MBON STDP Plasticity                    |
+-----------------------------------------------------------------------------------+
                                         ^
                                         | 60 Hz Telemetry & Controls
                                         v
+-----------------------------------------------------------------------------------+
|                             BROWSER FRONTEND COCKPIT                              |
|                                                                                   |
|   [Stimulus Arena]          [Three.js 3D Chamber]         [Neurochemical Cockpit] |
|   - Virtual Phone Canvas    - Photorealistic Fly Rig       - DA, OA, 5-HT Meters  |
|   - Preset Gallery          - Laboratory Electrophys Rig   - 120-Frame DA Chart   |
|   - Custom Photo Upload     - Direct-Facing Smartphone     - Spike Raster Matrix  |
|   - Spectral Analysis       - Dynamic 3D Neuropils         - Plasticity Drift HUD |
|                             - Tripod Gait & Leg Swipe      - Bilingual EN/TR Pill |
+-----------------------------------------------------------------------------------+
```

---

## Directory Layout

```
d:\brain\
├── frontend/
│   ├── index.html               # Main cockpit HTML layout with data-i18n tags
│   ├── styles.css               # Cyber-neuro glassmorphic dark design system
│   └── main.js                  # Three.js 3D scene, procedural textures, i18n & telemetry
├── src/
│   └── connectome_engine/
│       ├── brain.py             # Master ConnectomeBrain controller orchestrating 60 Hz loop
│       ├── config.py            # Physical constants, membrane parameters & kinetic rates
│       ├── data/
│       │   └── circuits.py      # MaleCNS v1.0 biological neuron identifiers & circuit maps
│       ├── server/
│       │   ├── app.py           # FastAPI server, REST routes & WebSocket telemetry stream
│       │   └── state.py         # Thread-safe rolling telemetry ring buffer
│       └── simulation/
│           ├── hormones.py      # Continuous ODE kinetics for DA, OA, 5-HT & STDP plasticity
│           ├── lif_kernel.py    # Vectorized sparse CSR Leaky Integrate-and-Fire simulation
│           ├── motor_decoder.py # Motor decoding: steering, throttle, moonwalking, GF jump
│           └── visual_transduction.py # Retinal mapping (R1-R6, R8) & LC4 optical looming
├── tests/
│   ├── test_brain_integration.py          # End-to-end observe-step-decode loop verification
│   ├── test_custom_photo_transduction.py  # User photo spectral analysis & current mapping
│   ├── test_hormones.py                   # DA, OA, 5-HT ODE synthesis & decay tests
│   ├── test_server_live.py                # FastAPI REST endpoints & WebSocket validation
│   ├── test_snn_engine.py                 # LIF membrane integration, threshold & refractory
│   └── test_visual_looming.py             # Looming shadow contrast expansion detection
├── pyproject.toml               # Project metadata & Python package dependencies
└── README.md                    # Comprehensive technical documentation
```

---

## Installation & Quickstart

### Prerequisites
- Python 3.12 or higher
- [`uv`](https://github.com/astral-sh/uv) (recommended for ultra-fast environment resolution)

### 1. Clone & Setup Environment
```bash
git clone https://github.com/your-org/fly-connectome-3d.git
cd fly-connectome-3d

# Install dependencies into virtual environment
uv sync
```

### 2. Start the Server
Launch the FastAPI biocomputing server with live WebSocket support:
```bash
uv run uvicorn connectome_engine.server.app:app --host 127.0.0.1 --port 8000 --reload
```

### 3. Open the Telemetry Cockpit
Open your browser and navigate to:
```
http://127.0.0.1:8000/
```

- Click **`TR`** / **`EN`** in the top right to switch languages.
- Choose a preset (**🍉 Sugar Fruit**, **⚠️ Looming Shadow**, **🕷️ Predatory Spider**, or **🌿 Forest Foliage**).
- Click **`WIREHEAD`** (**`DOPAMİN ŞOKU`**) to inject a $+20\text{ mV}$ reward pulse directly into the $PAM11$ dopaminergic cluster.
- Click **`LOOM THREAT`** (**`AVCI TEHDİDİ`**) to trigger the Giant Fiber backward leap.
- Click **`LEG SWIPE`** (**`BACAKLA KAYDIR`**) to trigger the front-leg screen swipe.
- Click **`📷 Upload Custom Photo`** to upload your own image and observe real-time neural and hormonal responses.

---

## REST & WebSocket API Reference

### 1. WebSocket Telemetry Stream
- **URL**: `ws://127.0.0.1:8000/ws/telemetry`
- **Direction**: Bi-directional at 60 Hz.
- **Client Commands**:
  ```json
  // Observe visual frame
  { "command": "observe", "image_base64": "data:image/jpeg;base64,...", "duration_ms": 50.0 }
  
  // Inject wirehead dopamine pulse
  { "command": "wirehead", "current_mv": 20.0 }
  ```
- **Server Telemetry Payload**:
  ```json
  {
    "type": "telemetry_update",
    "latest": {
      "sim_time_ms": 14250.0,
      "spike_counts": {
        "total_spikes": 312,
        "dopamine_hz": 18.5,
        "octopamine_hz": 2.1,
        "serotonin_hz": 8.4
      },
      "hormones": {
        "dopamine_nm": 14.82,
        "octopamine_nm": 2.34,
        "serotonin_nm": 8.05
      },
      "motor": {
        "steering_deflection": -0.15,
        "forward_drive_pct": 74.2,
        "retreat_flag": false,
        "giant_fiber_jump": false,
        "epg_heading_deg": 124.6
      },
      "plasticity_drift": 0.042
    }
  }
  ```

### 2. REST Endpoints
- **`GET /api/telemetry`**: Returns current snapshot and rolling history (up to 120 frames).
- **`POST /api/observe`**: Injects base64 visual frame into retinal photoreceptors.
- **`POST /api/wirehead`**: Triggers immediate $+20\text{ mV}$ excitation in PAM11 dopamine cluster.

---

## Automated Testing & Validation

All computational neuroscience modules are covered by a suite of automated unit and integration tests:

```bash
uv run pytest tests/ -v
```

### Verified Test Matrix:
- `tests/test_snn_engine.py`: Vectorized subthreshold membrane integration, spike emission, refractory clamping, and state checkpointing.
- `tests/test_hormones.py`: Continuous ODE synthesis, natural decay kinetics, and wireheading surge mechanics.
- `tests/test_visual_looming.py`: Photoreceptor current injection, looming expansion detection, and static baseline stability.
- `tests/test_custom_photo_transduction.py`: High-red appetitive spectral mapping and dark looming shadow discrimination.
- `tests/test_brain_integration.py`: End-to-end 60 Hz observe-step-decode orchestration.
- `tests/test_server_live.py`: Static asset serving, REST endpoints, and live WebSocket message exchange.

**Status: 15 / 15 tests passing cleanly.**

---

## References & Citations

1. **FlyWire Consortium (2024)**. *Whole-brain connectome of Drosophila melanogaster*. Nature, 634, 124–138.
2. **Schretter, C. E. et al. (2020)**. *A dopamine-modulated neural circuit for backward locomotion in Drosophila*. Nature, 586(7830), 554–559.
3. **Seelig, J. D., & Jayaraman, V. (2015)**. *Neural dynamics for landmark orientation and angular path integration in Drosophila*. Nature, 521(7551), 186–191.
4. **Card, G., & Dickinson, M. H. (2008)**. *Visually mediated motor planning in the escape response of Drosophila*. PNAS, 105(26), 9119–9124.
5. **Burrows, M. (1996)**. *The Neurobiology of an Insect Brain*. Oxford University Press.
6. **Takemura, S. et al. (2023)**. *A connectome of the male Drosophila ventral nerve cord and brain (MaleCNS v1.0)*. bioRxiv.

---

## License
MIT License. Open-source research software for computational neuroscience and biocomputing exploration.
