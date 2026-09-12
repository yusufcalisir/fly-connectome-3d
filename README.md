# <div align="center">🧠 FlyConnectome 3D</div>

<div align="center">
  <h3>Interactive 3D <i>Drosophila</i> Connectome Simulation & Electrophysiology Cockpit</h3>
  <p>
    Biophysically grounded spiking neural network simulation, 141K real 3D EM soma coordinates,
    and thoracic motor kinematics driven by the adult <b>Janelia MaleCNS v1.0</b> connectome.
  </p>

  [![Python 3.12](https://img.shields.io/badge/Python-3.12%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
  [![Connectome](https://img.shields.io/badge/Connectome-Janelia_MaleCNS_v1.0-FF6F00?style=for-the-badge&logo=target&logoColor=white)](https://flywire.ai/)
  [![Tests](https://img.shields.io/badge/Tests-80%2F80_Passing-00C853?style=for-the-badge&logo=pytest&logoColor=white)](#-testing--development)
  [![CI](https://img.shields.io/github/actions/workflow/status/yusufcalisir/fly-connectome-3d/ci.yml?branch=main&style=for-the-badge&logo=githubactions&logoColor=white&label=CI)](https://github.com/yusufcalisir/fly-connectome-3d/actions)
  [![Three.js](https://img.shields.io/badge/Frontend-Three.js_r128-000000?style=for-the-badge&logo=three.js&logoColor=white)](https://threejs.org/)
  [![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
  [![i18n](https://img.shields.io/badge/i18n-EN_%7C_TR-7C4DFF?style=for-the-badge&logo=translate&logoColor=white)](#-bilingual-interface-en--tr)
  [![License](https://img.shields.io/badge/License-MIT-grey?style=for-the-badge)](LICENSE)

  <p align="center">
    <a href="#-quickstart">⚡ Quickstart</a> •
    <a href="#-core-biophysical-integrations">🔬 Integrations</a> •
    <a href="#-system-architecture">📐 Architecture</a> •
    <a href="#-3d-neural-visualization--dual-viewport-architecture">🌌 3D Architecture</a> •
    <a href="#-empirical-benchmarks">📊 Benchmarks</a> •
    <a href="#-neural-circuits-modeled">🧬 Circuits</a> •
    <a href="#-web-cockpit--telemetry">🎮 Cockpit</a> •
    <a href="#-api-reference">📡 API</a> •
    <a href="#-testing--development">✅ Tests</a>
  </p>
</div>

---

## 🌟 Overview

**FlyConnectome 3D** is an open computational biology and neurokinematics platform modeling the central nervous system of the fruit fly (*Drosophila melanogaster*). The simulation bridges electron-microscopy synaptic wiring diagrams from the **Janelia Research Campus MaleCNS v1.0** dataset (~166.7K neurons, ~25.6M synapses) with a vectorized Leaky Integrate-and-Fire (LIF) biophysical engine and a high-performance 3D observation cockpit.

Instead of artificial representations or heuristic movement cycles, sensory inputs on a virtual smartphone display stimulate bilateral photoreceptor arrays, propagate through excitatory and inhibitory neurotransmitter pathways (Dale's principle), engage descending motor tracts ($DNa02, DNp09, MDN, GF$), and directly drive **381 ventral nerve cord (VNC) leg motor neurons** to generate canonical alternating tripod locomotion on a spherical treadmill.

---

## 🔬 Core Biophysical Integrations

### 1. 🧪 Neurotransmitter Polarity & Dale's Principle (E/I Balance)
- **Dale's Principle**: Biological classification of 166.7K neurons by primary neurotransmitter predictions.
  - **Acetylcholine (ACh)**: Excitatory current injection ($w > 0$, depolarizing EPSPs).
  - **GABA, Glutamate, Histamine**: Inhibitory current injection ($w < 0$, hyperpolarizing IPSPs).
- **Physiological Clamping**: Realistic potassium reversal potential clamp ($V_{\text{clamp}} = -85.0\text{ mV}$) prevents runaway hyper-excitation and unphysiological hyperpolarization, fostering natural rhythmic balance and sparse network firing.

### 2. 🌌 141.8K Real 3D Soma Coordinates & Synaptic Wave Propagation
- **EM Morphology Mapping**: Exact $[X, Y, Z]$ soma coordinates for **141,781 real neurons** extracted from MaleCNS v1.0 serial-section electron microscopy, isotropically normalized into Three.js anatomical space.
- **High-Performance Binary Point Cloud**: Packed into a 2.55 MB binary buffer (`soma_coordinates_141k.bin`) with custom GPU point shaders.
- **Synaptic Latency Waves**: Activity cascades through anatomical compartments with realistic synaptic conduction delays:
  - $\Delta t = 0\text{ ms}$: Retinotopic input cartridges (Optic Lobe)
  - $\Delta t = 18\text{ ms}$: Associative neuropils (Mushroom Body & Central Brain)
  - $\Delta t = 36\text{ ms}$: Descending motor command pathways ($DNa02$, Giant Fiber)
  - $\Delta t = 54\text{ ms}$: Ventral nerve cord thoracic motor pools ($T_1 - T_3$)

### 3. 🧭 Bilateral Hemispheric Asymmetry & Closed-Loop Phototaxis
- **Bilateral Retinotopy**: Strict separation of left (`somaSide == 'L'`) and right (`somaSide == 'R'`) visual hemifields.
- **Optomotor Steering**: Calculates instantaneous retinal asymmetry:

$$
\text{Asymmetry} = \frac{\bar{I}_{\text{Right}} - \bar{I}_{\text{Left}}}{\bar{I}_{\text{Right}} + \bar{I}_{\text{Left}}}
$$

- **Descending Tract Modulation**: Illuminating the left visual field excites left-dominant optical pathways and triggers asymmetric firing in bilateral descending steering neurons ($DNa02$), causing the outer right legs to step faster and wider to orient the fly toward the light source.

### 4. 🦿 VNC Thoracic Leg Motor Pools & Alternating Tripod Kinematics
- **381 Biological Leg Motor Neurons**: Extracted from MaleCNS v1.0 neuromeres ($T_1$ prothoracic, $T_2$ mesothoracic, $T_3$ metathoracic):
  - **$T1_L$ / $T1_R$ (Front Legs $L_1 / R_1$)**: 68 / 67 motor neurons
  - **$T2_L$ / $T2_R$ (Middle Legs $L_2 / R_2$)**: 58 / 58 motor neurons
  - **$T3_L$ / $T3_R$ (Hind Legs $L_3 / R_3$)**: 66 / 64 motor neurons
- **Central Pattern Generator (CPG)**: Generates canonical insect alternating tripod coordination:
  - **Tripod A** ($L_1, R_2, L_3$): Phase $\Phi_{\text{cpg}}$
  - **Tripod B** ($R_1, L_2, R_3$): Phase $\Phi_{\text{cpg}} + \pi$ ($180^\circ$ antiphase)
- **Direct Neural Joint Driving**: Femur protraction/retraction (`rotation.x`) and swing-phase tibia elevation (`rotation.z`) scale dynamically with each leg motor pool's firing rate ($Hz$). Reverse locomotion ($MDN$ moonwalker) reverses CPG phase progression.

---

## 📐 System Architecture

```
                  ┌─────────────────────────────────────────┐
                  │   Visual Stimulus (Phone Screen / File) │
                  └────────────────────┬────────────────────┘
                                       │
                    ┌──────────────────┴──────────────────┐
                    ▼                                     ▼
         ┌─────────────────────┐               ┌─────────────────────┐
         │ Left Retinotopy (L) │               │ Right Retinotopy (R)│
         └──────────┬──────────┘               └──────────┬──────────┘
                    │                                     │
                    └──────────────────┬──────────────────┘
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │ 166.7K Biological Connectome Graph      │
                  │ Dale's Principle: ACh (+) vs GABA/Glu(-)│
                  │ 141.8K 3D Soma Point Cloud (GPU Wave)   │
                  └────────────────────┬────────────────────┘
                                       │
                    ┌──────────────────┴──────────────────┐
                    ▼                                     ▼
         ┌─────────────────────┐               ┌─────────────────────┐
         │ Neuromodulators     │               │ Descending Commands │
         │ (DA, OA, 5-HT, E/I) │               │ (DNa02, DNp09, MDN) │
         └──────────┬──────────┘               └──────────┬──────────┘
                    │                                     │
                    └──────────────────┬──────────────────┘
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │ VNC Thoracic Central Pattern Generator  │
                  │ 381 Motor Neurons across T1, T2, T3     │
                  └────────────────────┬────────────────────┘
                                       │ WebSocket (60 Hz Telemetry)
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │ Three.js Cockpit & Hexapod Kinematics   │
                  │ Alternating Tripod Gait on Treadmill    │
                  └─────────────────────────────────────────┘
```

---

## ⚡ Quickstart

### Prerequisites
- **Python 3.12+**
- [`uv`](https://github.com/astral-sh/uv) (fast Python package and project manager)

### 1. Installation
```bash
git clone https://github.com/yusufcalisir/fly-connectome-3d.git
cd fly-connectome-3d

# Sync virtual environment and dependencies
uv sync
```

### 2. Connectome Dataset & 3D Soma Coordinates
The repository includes automated download and compilation scripts for the official **Janelia MaleCNS v1.0** dataset:
```bash
# 1. Download raw connectome Feather tables
uv run python src/connectome_engine/data/downloader.py

# 2. Compile sparse CSR connectome graph and circuit manifest
uv run python src/connectome_engine/data/compile_malecns.py

# 3. Compile 141K 3D soma coordinates binary buffer
uv run python src/connectome_engine/data/compile_coordinates.py
```

### 3. Launching the Engine

Start the biocomputing server and telemetry engine using `uv`:
```bash
uv run uvicorn connectome_engine.server.app:app --host 127.0.0.1 --port 8000 --ws-ping-interval 30 --ws-ping-timeout 60
```

Open your browser and navigate to:
```
http://127.0.0.1:8000/
```

---

## 📊 Empirical Benchmarks

The table below summarizes simulated network responses across calibrated sensory inputs (50 ms simulation chunk, Janelia MaleCNS v1.0 connectome):

| Visual Stimulus | Luminance ($Y$) | Dominant Spectrum | Network Spikes | Firing Rate | Looming Trigger | Circuit Dynamics & Kinematic Outcome |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Pure White** (`#FFFFFF`) | 1.000 | Broad spectrum (6,500 K) | ~20,700 | 2.48 Hz | ❌ Inactive | Broad-spectrum $R_1-R_6$ excitation; optic lobe wave propagation; steady tripod walking. |
| **Pure Red** (`#C80000`) | 0.235 | Long wavelength (~3,000 K) | 0 | 0.00 Hz | ❌ Inactive | Sub-threshold current injection ($V < V_{\text{thresh}}$); network remains quiescent with potassium reversal clamping. |
| **Pure Blue** (`#0000E6`) | 0.103 | Short wavelength (UV / Blue) | ~6,680 | 0.80 Hz | ❌ Inactive | Selective excitation of inner $R_8$ photoreceptors; moderate forward drive. |
| **Rapid Dark / Looming** (`#000000`) | 0.000 | Contrast drop | ~11,000 | 1.32 Hz | ✅ Active | Contrast collapse ($\Delta Y > 0.15$); $LC_4$ activation; Giant Fiber ($GF$) jump escape triggered. |

---

## 🧬 Neural Circuits Modeled

The simulation maps specific, identifiable functional circuits from the Janelia MaleCNS v1.0 connectome:

| Circuit Population | Anatomic / Genetic ID | Neuromere / Brain Area | Functional Role in Simulation |
| :--- | :--- | :--- | :--- |
| **Photoreceptors** | $R_1 - R_6$, $R_8$ | Retina / Optic Cartridge | Bilateral luminance and chromatic inputs |
| **Looming Detectors** | $LC_4$ | Lobula Complex | Visual threat detection & rapid expansion |
| **Dopaminergic System** | $PAM11$ | Mushroom Body / SMP | Appetitive reward, pleasure, and plastic association |
| **Octopaminergic System** | $TDC2$ | Central Neuropil | Acute arousal, flight response, and motor vigor |
| **Serotonergic System** | $5\text{-HT}$ clusters | Dorsal Central Brain | Baseline calm, motor persistence, and satiety |
| **Compass Neurons** | $EPG$ ring | Central Complex ($EB/PB$) | Azimuthal head direction compass heading |
| **Steering Descending** | $DNa02_L / DNa02_R$ | Brain $\rightarrow$ Thoracic VNC | Asymmetric outer leg step amplitude modulation |
| **Forward Descending** | $DNp09$ | Brain $\rightarrow$ Thoracic VNC | Forward locomotion rate & CPG frequency drive |
| **Reverse Descending** | $MDN$ | Brain $\rightarrow$ Thoracic VNC | Moonwalker reverse stepping & CPG phase inversion |
| **Escape Descending** | $GF$ (Giant Fiber) | Brain $\rightarrow$ Thoracic VNC | Escape jump reflex & rapid wing elevation |
| **Front Leg Motor Pools** | $T1_L / T1_R$ (`fl`) | Prothoracic Neuromere $T_1$ | 135 motor neurons driving $L_1 / R_1$ leg kinematics |
| **Middle Leg Motor Pools**| $T2_L / T2_R$ (`ml`) | Mesothoracic Neuromere $T_2$ | 116 motor neurons driving $L_2 / R_2$ leg kinematics |
| **Hind Leg Motor Pools**  | $T3_L / T3_R$ (`hl`) | Metathoracic Neuromere $T_3$ | 130 motor neurons driving $L_3 / R_3$ leg kinematics |

---

## 🎮 Web Cockpit & Telemetry

The observation cockpit presents real-time electrophysiology and behavioral readouts:

1. **Stimulus Arena**:
   - **Preset Patterns**: Sugar Watermelon (Appetitive), Looming Shadow (Escape), Predatory Spider (Threat), Forest Foliage (Calm).
   - **Custom Photo Upload**: Submits custom imagery for real-time photo-transduction.
   - **Spatial Target Positions**: Left, Center, Right phototaxis orientation buttons.
2. **Descending Motor & VNC Hexapod Telemetry**:
   - **Bilateral Steering Meter**: $DNa02$ deflection with retinal hemisphere luminance bars.
   - **Tripod Alternation Indicator**: Live status indicators for **Tripod A** ($L_1, R_2, L_3$) and **Tripod B** ($R_1, L_2, R_3$) in stance/swing.
   - **6-Leg Firing Gauges**: Live $Hz$ meters for $L_1, R_1, L_2, R_2, L_3, R_3$.
3. **Neurochemical Gauges & Oscilloscopes**:
   - Continuous Dopamine ($PAM11$), Octopamine ($TDC2$), and Serotonin ($5\text{-HT}$) molar concentrations.
   - Dale's Law E/I balance ratio and associative plasticity index.
   - Real-time dopamine waveform and spike raster waterfall plots.
4. **Interactive Camera Perspectives**:
   - **Fly View**: Macro perspective on fly joints and spherical treadmill.
   - **Phone Angle**: Displays visual stimuli as presented to the compound eyes.
   - **Neural Synapses**: Visualizes the 141K 3D soma point cloud and real-time synaptic waves.
5. **Dedicated CNS 3D Neural Activity Viewport (Bottom-Right Panel)**:
   - Real-time rotating 3D fruit fly central nervous system point cloud (141.8K real somas).
   - Live synaptic flares lighting up active circuits, complete with interactive 3D touch/mouse drag manipulation.

---

## 🌌 3D Neural Visualization & Dual-Viewport Architecture

FlyConnectome 3D implements a synchronized **dual Three.js WebGL viewport architecture** that bridges whole-body kinematic behavior with an isolated, live anatomical central nervous system inspection view:

```
                                  ┌────────────────────────────────────────────────────────┐
                                  │      60 Hz Bidirectional Telemetry (WebSocket)        │
                                  └───────────┬────────────────────────────────┬───────────┘
                                              │                                │
                       ┌──────────────────────▼───────┐        ┌───────────────▼──────────────────────┐
                       │   Viewport 1: Rig & Treadmill │        │   Viewport 2: Cockpit CNS 3D View    │
                       │   (#three-container)         │        │   (#cns-brain-canvas)                │
                       ├──────────────────────────────┤        ├──────────────────────────────────────┤
                       │ • Anatomical Fly Rig         │        │ • Isolated MaleCNS v1.0 Point Cloud  │
                       │ • Hexapod 6-Leg Kinematics   │        │ • 141,781 Real EM Soma Coordinates   │
                       │ • Spherical Air Treadmill    │        │ • 360° Turntable Auto-Rotation       │
                       │ • OLED Stimulus Display      │        │ • Circuit Bioluminescent Palettes    │
                       │ • Cranial Wave Propagation   │        │ • Spiking Blooming & Synaptic Flares │
                       │ • Orbit Camera Director      │        │ • Interactive Mouse / Touch Drag     │
                       └──────────────────────────────┘        └──────────────────────────────────────┘
```

### 1. Primary Electrophysiology & Kinematic Chamber (`#three-container`)
- **Biomechanical Insect Morphology**:
  - **Head & Sensory Lattice**: Bilateral compound eye meshes with hexagonal ommatidia normal maps, articulated olfactory antennae, and feeding proboscis.
  - **Chitinous Thorax & Abdomen**: Realistic chitin standard PBR materials with subtle respiratory ventilation oscillations.
  - **Six Articulated Thoracic Legs**: Prothoracic ($T_1$), mesothoracic ($T_2$), and metathoracic ($T_3$) leg assemblies, each modeled with anatomical coxa, femur, tibia, and tarsus joint segments.
  - **Treadmill Ball Rig**: Air-supported floating sphere dynamically rotating under the fly's tarsi in direct kinematic closed-loop coupling with the VNC alternating tripod gait.
- **Virtual Stimulus Arena**:
  - A 720×1280 virtual smartphone display mounted on an articulating ball-mount stand in front of the fly.
  - Live canvas rendering of chromatic targets (appetitive sugar fruits, looming predatory shadows, spider threats, forest foliage, and user-uploaded custom images).
  - Dynamic retinal casting: The display casts physical light onto the compound eyes, driving the bilateral retinotopic arrays.
- **Cranial Synaptic Latency Wave Propagation**:
  - The 141.8K EM somas embedded inside the cranial capsule are rendered via GPU point shaders (`THREE.Points`).
  - Active action potentials propagate in 4 distinct biological latency waves ($0\text{ ms}$ retina $\rightarrow$ $18\text{ ms}$ mushroom body $\rightarrow$ $36\text{ ms}$ central complex/descending $\rightarrow$ $54\text{ ms}$ thoracic VNC), creating visual rippling wavefronts through the head.
- **Multi-Camera Director**:
  - **Fly View**: Macro perspective on the spherical treadmill and hexapod leg articulation.
  - **Phone Angle**: First-person retinal perspective from the stimulus screen toward the fly.
  - **Neural Synapses**: Close-up inspection of the cranial point cloud and synaptic firing waves.

### 2. Dedicated Cockpit CNS 3D Neural Activity Viewport (`#cns-brain-canvas`)
Located in the bottom-right panel of the cockpit, this dedicated viewport provides a standalone, high-resolution 3D inspection of the fruit fly central nervous system in continuous operation:
- **Full Connectome Soma Architecture**:
  - Directly ingests the **141,781 real EM soma coordinates** from `soma_coordinates_141k.bin` (MaleCNS v1.0).
  - Normalizes and centers the somas around origin (`[0.0, -0.0368, -0.2180]`), fitting the natural bounding sphere perfectly inside the viewport.
- **Elevated 3/4 Dorsal Perspective & Turntable Auto-Rotation**:
  - Positioned at an elevated dorsal angle ($\theta_{\text{pitch}} = -0.45\text{ rad}$, $\theta_{\text{roll}} = -0.10\text{ rad}$) matching standard neuroanatomical orientation (revealing bilateral optic lobes, central brain dome, and ventral nerve cord).
  - Continuously auto-rotates around the vertical axis (`rotation.y += 0.0048`), providing a complete 360-degree holographic inspection.
- **Bioluminescent Circuit Color Coding**:
  Somas are color-coded by verified biological neuropil circuits:
  - **Optic Lobes ($R_1-R_8$, Lamina/Medulla)**: Electric Cyan (`#00f0ff`, `rgb(0, 224, 255)`)
  - **Central Brain Neuropil**: Deep Electric Blue (`#38bdf8`, `rgb(38, 166, 242)`)
  - **Mushroom Body (Kenyon Cells)**: Honey Amber (`#f59e0b`, `rgb(255, 166, 38)`)
  - **Central Complex ($EPG$ Compass)**: Mint Emerald (`#10b981`, `rgb(26, 242, 140)`)
  - **Descending Motor Pathways ($DNa02, DNp09, GF$)**: Fiery Coral (`#ef4444`, `rgb(255, 89, 64)`)
  - **Ventral Nerve Cord (Thoracic Motor Cord)**: Radiant Violet (`#a855f7`, `rgb(166, 89, 255)`)
- **GPU Additive Blending & Dynamic Action Potential Flares**:
  - Built with custom GLSL vertex and fragment shaders using `THREE.AdditiveBlending`.
  - **Resting state**: Ethereal, semi-transparent points ($\alpha = 0.35$ with soft radial gaussian falloff).
  - **Spiking state**: When the biophysical engine fires action potentials, active somas expand up to **4.5× in point size**, ignite in pure **radiant white-cyan bloom** ($\alpha = 1.0$), and smoothly decay over $\approx 150\text{ ms}$ with realistic biological latency. Dense firing clusters fuse into glowing energy hubs.
- **Interactive 3D Touch & Mouse Drag**:
  - Users can click and drag (or touch-drag on mobile/tablets) to freely pitch, yaw, and inspect the connectome from any angle in 3D space.
  - Releasing the pointer smoothly restores the graceful auto-rotation.
- **Real-Time Telemetry HUD**:
  - Live active soma counter (e.g., `35,321 active`) dynamically updated every frame.
  - Bottom telemetry badge displaying dataset provenance (`MaleCNS v1.0 · 141.8K Somas`) and interaction hints.

---

## 🌐 Bilingual Interface (EN / TR)

The cockpit features a one-click language toggle (English $\leftrightarrow$ Türkçe) with persistent user preference storage:
- **English**: Standard computational neuroscience terminology and units.
- **Türkçe**: Anatomical and biophysical Turkish terminology (`VNC Thoraks Heksapod Yürüyüşü`, `Dopamin Şoku`, `Retinal Asimetri`, `Avcı Tehdidi`, etc.).

---

## 📡 API Reference

### WebSocket Telemetry Stream
- **Endpoint**: `ws://127.0.0.1:8000/ws/telemetry`
- **Rate**: 60 Hz bidirectional JSON stream.
- **Payload Structure**:
  ```json
  {
    "sim_time_ms": 150.0,
    "spike_counts": { "total_spikes": 342, "excitatory_spikes": 280, "inhibitory_spikes": 62 },
    "hormones": { "dopamine_nm": 18.5, "octopamine_nm": 3.2, "serotonin_nm": 8.0, "ei_balance": 1.45 },
    "motor": { "forward_drive_pct": 65.0, "steering_deflection": -0.35, "compass_heading_deg": 142.5 },
    "vnc_legs": {
      "t1_left_hz": 12.4, "t1_right_hz": 24.8,
      "t2_left_hz": 11.2, "t2_right_hz": 22.4,
      "t3_left_hz": 14.1, "t3_right_hz": 28.2,
      "tripod_phase": 1.84
    },
    "active_neurons": [12, 145, 890, 14022]
  }
  ```

### REST Endpoints
| Route | Method | Description |
| :--- | :---: | :--- |
| `/api/telemetry` | `GET` | Fetches latest telemetry state and rolling historical buffer. |
| `/api/observe` | `POST` | Ingests base64-encoded image frame for biological transduction. |
| `/api/wirehead` | `POST` | Injects depolarizing current (+20 mV) into dopaminergic $PAM11$ cluster. |
| `/api/connectome/soma-coordinates` | `GET` | Streams binary buffer of 141.8K real soma coordinates (`.bin`). |
| `/api/connectome/soma-metadata` | `GET` | Returns anatomical bounding boxes, scaling factors, and circuit partitions. |

---

## ✅ Testing & Development

The test suite includes **80 automated tests across 22 test files**, covering biological circuits, biophysical equations, launcher scripts, and frontend contracts:

```bash
# Run complete test suite
uv run pytest tests/ -v

# Run static analysis and style checks
uv run ruff check src/ tests/
```

### GitHub Actions CI Workflow
Every push to `main` and pull request is verified across 5 parallel CI jobs:
1. **`unit-tests`**: 75 tests covering biophysics, phototaxis, frontend contracts, and launcher scripts.
2. **`performance-regression`**: Benchmarks the vectorized LIF kernel sub-500ms execution.
3. **`real-connectome`**: Validates the 166.7K topology, 25.6M synapses, and 381 VNC motor neurons.
4. **`server-integration`**: Validates FastAPI REST endpoints and WebSocket telemetry transmission.
5. **`lint`**: Ruff static code analysis and `pyproject.toml` specification integrity.

---

## 📚 References & Data Sources

- **Janelia Research Campus (FlyEM Team)**: *Drosophila* male central nervous system connectome (MaleCNS v1.0).
- **FlyWire & Princeton University**: Community whole-brain connectomic proofreading and annotation tools.
- **Three.js**: WebGL 3D rendering library.
- **FastAPI & Uvicorn**: Asynchronous backend and real-time telemetry streaming framework.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
