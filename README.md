# <div align="center">🧠 FlyConnectome 3D</div>

<div align="center">
  <h3>Interactive 3D <i>Drosophila</i> Connectome Simulation & Electrophysiology Cockpit</h3>
  <p>
    Exploring neural dynamics, visual responses, and motor behaviors using connectome wiring from the Janelia MaleCNS v1.0 dataset.
  </p>

  [![Python 3.12](https://img.shields.io/badge/Python-3.12%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
  [![Connectome](https://img.shields.io/badge/Connectome-Janelia_MaleCNS_v1.0-FF6F00?style=for-the-badge&logo=target&logoColor=white)](https://flywire.ai/)
  [![Tests](https://img.shields.io/badge/Tests-34%2F34_Passing-00C853?style=for-the-badge&logo=pytest&logoColor=white)](#-testing--development)
  [![CI](https://img.shields.io/github/actions/workflow/status/yusufcalisir/fly-connectome-3d/ci.yml?branch=main&style=for-the-badge&logo=githubactions&logoColor=white&label=CI)](https://github.com/yusufcalisir/fly-connectome-3d/actions)
  [![Three.js](https://img.shields.io/badge/Frontend-Three.js_r128-000000?style=for-the-badge&logo=three.js&logoColor=white)](https://threejs.org/)
  [![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
  [![i18n](https://img.shields.io/badge/i18n-EN_%7C_TR-7C4DFF?style=for-the-badge&logo=translate&logoColor=white)](#-bilingual-interface-en--tr)
  [![License](https://img.shields.io/badge/License-MIT-grey?style=for-the-badge)](LICENSE)

  <p align="center">
    <a href="#-quickstart">⚡ Quickstart</a> •
    <a href="#-key-features">✨ Features</a> •
    <a href="#-how-it-works">🔍 How It Works</a> •
    <a href="#-empirical-benchmarks">📊 Benchmarks</a> •
    <a href="#-circuits-modeled">🔬 Circuits</a> •
    <a href="#-web-cockpit">🎮 Cockpit</a> •
    <a href="#-api-reference">📡 API</a> •
    <a href="#-testing--development">✅ Tests</a>
  </p>
</div>

---

## 🌟 Overview

**FlyConnectome 3D** is an open-source simulation and visualization environment for exploring the connectome of the fruit fly (*Drosophila melanogaster*). The project connects the adult connectome wiring diagram (**Janelia Research Campus MaleCNS v1.0 / FlyWire**) to a Leaky Integrate-and-Fire (LIF) spiking neural network simulation, presenting real-time dynamics inside an interactive 3D web cockpit.

Users can present visual stimuli on a virtual smartphone screen facing the fly. The simulation maps these images onto modeled photoreceptors, propagates activity through connected neural circuits, estimates neuromodulator levels (dopamine, octopamine, serotonin), and decodes downstream behavioral commands (walking, steering, and escape jumps) displayed on an air-cushioned spherical treadmill.

```
                  ┌─────────────────────────────────┐
                  │ Visual Stimulus (Image / Preset) │
                  └────────────────┬────────────────┘
                                   │
                                   ▼
                  ┌─────────────────────────────────┐
                  │ Retinal Transduction (R1-R6, R8) │
                  └────────────────┬────────────────┘
                                   │
                                   ▼
                  ┌─────────────────────────────────┐
                  │    Spiking Connectome Engine    │
                  │   (Vectorized LIF Simulation)   │
                  └───────────────┬─┬───────────────┘
                                  │ │
                 ┌────────────────┘ └───────────────┐
                 ▼                                  ▼
      ┌─────────────────────┐            ┌────────────────────┐
      │   Neuromodulators   │            │   Motor Decoders   │
      │ (Dopamine, OA, 5HT) │            │ (Steering, GF Jump)│
      └──────────┬──────────┘            └──────────┬─────────┘
                 │                                  │
                 └────────────────┬─────────────────┘
                                  │ WebSocket (60 Hz)
                                  ▼
                  ┌─────────────────────────────────┐
                  │    Interactive 3D Web Cockpit   │
                  │    (Three.js + Live Telemetry)  │
                  └─────────────────────────────────┘
```

---

## ⚡ Quickstart

### Prerequisites
- **Python 3.12+**
- [`uv`](https://github.com/astral-sh/uv) (recommended package and environment manager)

### 1. Clone & Install
```bash
# Clone the repository
git clone https://github.com/yusufcalisir/fly-connectome-3d.git
cd fly-connectome-3d

# Sync virtual environment and dependencies
uv sync
```

### 2. Connectome Dataset (Optional)
The simulation includes a lightweight built-in representative circuit graph so you can test immediately without extra setup.

To use the full official **Janelia MaleCNS v1.0** dataset (~166k neurons, ~25.6M synapses):
```bash
# 1. Download official dataset tables
uv run python src/connectome_engine/data/downloader.py

# 2. Compile into a compressed sparse CSR matrix (~80 MB)
uv run python src/connectome_engine/data/compile_malecns.py
```

### 3. Launch the Application

On Windows:
```cmd
start.bat
```

Or run directly via `uv`:
```bash
uv run uvicorn connectome_engine.server.app:app --host 127.0.0.1 --port 8000
```

Open your browser and navigate to:
```
http://127.0.0.1:8000/
```

---

## ✨ Key Features

- **Biological Connectome Integration**: Compatible with the Janelia MaleCNS v1.0 dataset, compiled into memory-mapped sparse CSR matrices for efficient sparse matrix multiplications.
- **Vectorized LIF Simulation**: Simulates membrane potential updates and spike propagation across thousands of neurons using vectorized sub-step integration in NumPy.
- **Visual Mapping & Looming Detection**: Projects stimuli onto simulated outer ($R_1-R_6$) and inner ($R_8$) photoreceptors, and detects rapid optical expansion via Lobula Columnar ($LC_4$) pathways.
- **Neuromodulatory & Motor Decoding**: Simple differential equations track continuous concentrations of Dopamine, Octopamine, and Serotonin, feeding motor decoders for walking, steering ($DNa02$), and escape jumping (Giant Fiber).
- **Interactive 3D Web Environment**: Built with Three.js to provide an electrophysiology laboratory view with multiple camera perspectives, animated fly kinematics, and live cranial circuit highlights.
- **Bilingual Interface**: Seamless toggle between English and Turkish, with persistent language preference.

---

## 🔍 How It Works

### 1. Visual Input & Photoreceptor Transduction
When an image or preset is presented on the virtual screen:
- Outer photoreceptors ($R_1-R_6$) receive luminance-proportional input, modeling broad-spectrum visual drive.
- Inner photoreceptors ($R_8$) receive chromatic-weighted input, modeling short-wavelength sensitivity.
- If contrast expands rapidly across consecutive frames, an optical looming detector triggers an excitatory current into the $LC_4$ population.

### 2. Spiking Neural Network Dynamics
Neuron membrane potentials evolve according to Leaky Integrate-and-Fire (LIF) dynamics:

$$\tau_m \frac{dV_i}{dt} = -(V_i(t) - V_{\text{rest}}) + R_m \left( I_i^{\text{syn}}(t) + I_i^{\text{ext}}(t) \right)$$

When membrane potential exceeds threshold ($V_{\text{thresh}} = -50.0\text{ mV}$), the neuron spikes, resets to $V_{\text{reset}} = -70.0\text{ mV}$, and enters a brief refractory period ($\tau_{\text{ref}} = 2.0\text{ ms}$). Synaptic inputs are accumulated via sparse connectome weights.

### 3. Neuromodulators & Motor Decoding
- **Dopamine ($[\text{DA}]$)**: Driven by the $PAM11$ cluster; rises in response to appetitive cues or wirehead stimulation.
- **Octopamine ($[\text{OA}]$)**: Driven by $TDC2$ neurons; elevated during sudden changes or threat cues.
- **Serotonin ($[5\text{-HT}]$)**: Reflects calmer, baseline conditions and motor stability.
- **Motor Outputs**: Firing rates in descending neurons are mapped to walking speed, steering angle, and high-priority escape responses via the Giant Fiber ($GF$) pathway.

---

## 📊 Empirical Benchmarks

To illustrate how sensory transduction and LIF spiking dynamics behave across different visual inputs, the table below summarizes simulated network responses to calibrated reference inputs (50 ms simulation chunk, Janelia MaleCNS v1.0 connectome):

| Visual Stimulus | Luminance ($Y$) | Dominant Spectrum | Total Spikes | Mean Firing Rate | Looming Trigger | Simulated Circuit Response |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Pure White** (`#FFFFFF`) | 1.000 | Broad spectrum (6,500 K) | ~20,700 | 2.48 Hz | ❌ False | Broad-spectrum $R_1-R_6$ activation; widespread optic lobe propagation |
| **Pure Red** (`#C80000`) | 0.235 | Long wavelength (~3,000 K) | 0 | 0.00 Hz | ❌ False | Sub-threshold current injection ($V < V_{\text{thresh}}$); network remains quiescent |
| **Pure Blue** (`#0000E6`) | 0.103 | Short wavelength (UV / Blue) | ~6,680 | 0.80 Hz | ❌ False | Selective excitation of inner $R_8$ photoreceptors; chromatic contrast response |
| **Rapid Dark / Looming** (`#000000`) | 0.000 | Contrast drop | ~11,000 | 1.32 Hz | ✅ True | Optical contrast collapse ($\Delta Y > 0.15$); activates $LC_4$ and Giant Fiber escape jump |

### Key Observations
- **Spectral Selectivity**: Outer photoreceptors ($R_1-R_6$) respond broadly to overall light intensity, whereas inner $R_8$ cells are selectively tuned toward shorter wavelengths.
- **Threshold Nonlinearity**: Low-intensity or out-of-band inputs (such as pure red) distribute sub-threshold currents, keeping membrane potentials below firing threshold without generating spurious spikes.
- **Spatio-Temporal Looming**: A sharp drop in luminance across frames triggers the $LC_4$ lobula columnar pathway, simulating an incoming visual threat and driving the Giant Fiber escape reflex.
- **Statefulness**: Membrane potentials ($V_i$), refractory states ($\tau_{\text{ref}}$), and neuromodulator concentrations carry forward between frames, capturing temporal continuity rather than static stateless evaluations.

---

## 🔬 Circuits Modeled

The simulation identifies and maps key cell populations from the *Drosophila* connectome:

| Circuit / Cell Group | Connectome Identifier | Role in Model |
| :--- | :--- | :--- |
| **Photoreceptors** | $R_1 - R_6$, $R_8$ | Retinal luminance and chromatic input |
| **Looming Detectors** | $LC_4$ | Sensitive to sudden visual expansion / looming threat |
| **Dopaminergic System** | $PAM11$ | Modulates reward-related state and plasticity |
| **Octopaminergic System** | $TDC2$ | Reflects arousal and stress signals |
| **Serotonergic System** | $5\text{-HT}$ dorsal clusters | Supports steady baseline activity and patience |
| **Mushroom Body** | Kenyon Cells ($KC$), $MBON$ | Learning and associative preference modulation |
| **Central Complex** | $EPG$ compass neurons | Heading direction representation around an azimuthal ring |
| **Descending Motor Neurons**| $DNa02$, $DNp09$, $GF$ | Asymmetric steering, forward walking, and escape jump |

---

## 🎮 Web Cockpit

The web interface brings the simulation into a real-time observation deck:

- **Camera Modes**:
  - **Fly View (Default)**: General perspective focusing on the fly, treadmill, and screen.
  - **Screen View**: Look directly at the stimuli being presented to the fly.
  - **Neural View**: Translucent cranial visualization showing active brain regions (Optic Lobes, Mushroom Body, Central Complex, Descending Tracts).
- **Stimulus Arena**:
  - Presets: Sweet Watermelon, Looming Shadow, Predatory Spider, Forest Foliage.
  - **Custom Image Upload**: Upload any PNG/JPEG to test custom visual patterns.
- **Manual Actions**:
  - **Dopamine Pulse**: Stimulate the $PAM11$ dopaminergic cluster.
  - **Loom Threat**: Trigger an immediate optical threat expansion.
  - **Leg Swipe**: Trigger tactile grooming/swipe motion.

---

## 🌐 Bilingual Interface (EN / TR)

The cockpit includes a language toggle in the header:
- **English**: Standard terminology for computational neuroscience and simulation parameters.
- **Türkçe**: Translated interface labels and tooltips (`Dopamin Şoku`, `Avcı Tehdidi`, `Uyaran Arenası`, etc.).
- Preference is remembered across browser sessions via `localStorage`.

---

## 📡 API Reference

### WebSocket Telemetry Stream
- **URL**: `ws://127.0.0.1:8000/ws/telemetry`
- Stream: Delivers 60 Hz telemetry packets containing spike counts, neuromodulator levels, motor states, and compass heading.

### REST Endpoints
| Endpoint | Method | Description |
| :--- | :---: | :--- |
| `/api/telemetry` | `GET` | Returns the latest telemetry frame and rolling history buffer. |
| `/api/observe` | `POST` | Submits a visual frame (base64) to the retinal input engine. |
| `/api/wirehead` | `POST` | Injects an excitatory current into the dopaminergic $PAM11$ cluster. |

---

## ✅ Testing & Development

The test suite covers unit dynamics, vectorization performance, live server communications, and connectome integrity.

Run the test suite with `uv`:
```bash
uv run pytest tests/ -v
```

Check code formatting and imports with `ruff`:
```bash
uv run ruff check src/ tests/
```

### GitHub Actions CI
Every commit and pull request runs automated checks via GitHub Actions:
- Unit & integration tests
- Performance benchmarks for vectorized LIF kernels
- FastAPI REST and WebSocket lifecycle tests
- Ruff linting and import ordering
- Connectome topology validation

---

## 📚 References & Acknowledgments

- **Janelia Research Campus (FlyEM Project)**: *Drosophila* male central nervous system (MaleCNS v1.0) connectome dataset.
- **FlyWire & Princeton University**: Whole-brain connectome tools and community annotation resources.
- **Three.js & FastAPI**: Core open-source technologies powering the 3D rendering and backend telemetry.

---

## 📄 License

Distributed under the [MIT License](LICENSE). Open-source project for computational neuroscience exploration, education, and visualization.
