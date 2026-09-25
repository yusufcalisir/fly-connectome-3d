# Contributing to FlyConnectome 3D

Thank you for your interest in contributing to **FlyConnectome 3D**! This project models the central nervous system of *Drosophila melanogaster* using the **Janelia MaleCNS v1.0** electron-microscopy connectome (~166.7K neurons, ~25.6M synapses, 141.8K real 3D somas), driven by a vectorized Leaky Integrate-and-Fire (LIF) spiking neural network engine and an interactive Three.js 3D observation cockpit.

We welcome contributions ranging from biophysical model refinements and circuit integrations to frontend visualization improvements and performance optimizations.

---

## 📋 Table of Contents

- [Code of Conduct & Scientific Honesty Standard](#code-of-conduct--scientific-honesty-standard)
- [Reporting Issues & Suggesting Enhancements](#reporting-issues--suggesting-enhancements)
- [Development Environment Setup](#development-environment-setup)
- [Data Pipeline: Downloading & Compiling MaleCNS v1.0](#data-pipeline-downloading--compiling-malecns-v10)
- [Running the Server & Cockpit](#running-the-server--cockpit)
- [Testing & Quality Assurance](#testing--quality-assurance)
- [Continuous Integration (CI Pipeline)](#continuous-integration-ci-pipeline)
- [Empirical Validation & Benchmark Reproducibility](#empirical-validation--benchmark-reproducibility)
- [Frontend Guidelines & Bilingual (EN / TR) Contracts](#frontend-guidelines--bilingual-en--tr-contracts)
- [Code Style & Linting](#code-style--linting)
- [Submitting a Pull Request](#submitting-a-pull-request)
- [Pre-PR Checklist](#pre-pr-checklist)
- [License](#license)

---

## Code of Conduct & Scientific Honesty Standard

This project adheres to a strict standard of **empirical honesty and biological accuracy**:

1. **Zero Fabrication**: All numbers, benchmark metrics, firing rates, and spike counts must come directly from reproducible simulation runs or cited biological literature. Never invent or adjust figures to fit an expectation.
2. **Explicit Simplification Boundaries**: Our electrophysiological dynamics, photoreceptor adapters, and motor mappings are computational approximations. Any addition or alteration of biophysical mechanisms must clearly distinguish between authentic connectomic topology (MaleCNS v1.0 EM reconstruction) and simulated approximations.
3. **Mandatory Boundary Statements**: When updating biophysical behavior, you must document what the change proves and explicitly what it does **not** prove (see [docs/validation.md](docs/validation.md)).
4. **Respectful & Constructive Collaboration**: Treat all contributors and community members with respect, patience, and constructive critique.

---

## Reporting Issues & Suggesting Enhancements

### Reporting Bugs
1. Search [existing issues](https://github.com/yusufcalisir/fly-connectome-3d/issues) before opening a new one.
2. Provide a descriptive title and detailed context:
   - Operating System (Windows, Linux, macOS).
   - Python version (`python --version`, recommended 3.12).
   - Exact steps to reproduce the issue.
   - Complete stack trace or console error log.
   - Whether the issue occurs with the real connectome dataset (`data/malecns_v1/malecns_v1_graph.npz`) or synthetic fallback data.

### Suggesting Features & Circuit Integrations
Open an issue tagged `enhancement` describing:
- The biological or computational motivation and relevant neuron classes / circuits.
- Empirical source citations (e.g. Janelia FlyEM, FlyWire, NeuPrint, literature DOIs).
- Proposed computational implementation (e.g. vectorized LIF parameters, neuromodulatory kinetics, Three.js shaders).

---

## Development Environment Setup

### Prerequisites
- **Python**: `3.11` to `3.12` (Python 3.12 is recommended; see `pyproject.toml`).
- **Package Manager**: [`uv`](https://docs.astral.sh/uv/) (strongly recommended for sub-second virtualenv resolution and dependency locking).
- **Git**: For version control.

### Installation

#### 1. Clone the repository
```bash
git clone https://github.com/yusufcalisir/fly-connectome-3d.git
cd fly-connectome-3d
```

#### 2. Install `uv` (if not already installed)
- **Windows (PowerShell)**:
  ```powershell
  irm https://astral.sh/uv/install.ps1 | iex
  ```
- **macOS / Linux**:
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- Alternatively, via `pip`:
  ```bash
  pip install uv
  ```

#### 3. Sync dependencies and development tools
```bash
uv sync --dev
```
This automatically provisions a `.venv` with all runtime packages (`numpy`, `scipy`, `pyarrow`, `pandas`, `fastapi`, `uvicorn`, `websockets`, `pillow`, `pydantic`, `httpx`) and dev packages (`pytest`, `pytest-timeout`, `ruff`).

---

## Data Pipeline: Downloading & Compiling MaleCNS v1.0

The full biocomputing simulation operates on the official **Janelia MaleCNS v1.0** dataset (~166.7K neurons, ~25.6M synapses).

```bash
# 1. Download raw connectome Feather tables (~1.1 GB)
uv run python src/connectome_engine/data/downloader.py

# 2. Compile sparse CSR connectome graph and circuit manifest
uv run python src/connectome_engine/data/compile_malecns.py

# 3. Compile 141.8K 3D soma coordinates into binary buffer (2.55 MB)
uv run python src/connectome_engine/data/compile_coordinates.py
```

> **Windows Quickstart**: You can compile all data in a single command using `start.bat`:
> ```cmd
> .\start.bat compile
> ```

Compiled data files will be saved in `data/malecns_v1/`:
- `malecns_v1_graph.npz`: Sparse CSR adjacency matrix, synaptic weights, and polarity.
- `circuits_manifest.json`: Mapped neural circuit partitions (Photoreceptors, MB, CX, DNa02, VNC motor pools).
- `soma_coordinates_141k.bin`: Packed 3D point cloud array for GPU point shaders.

---

## Running the Server & Cockpit

### Option A: Windows Automated Cockpit (`start.bat`)
Run `start.bat` from CMD or PowerShell:
```cmd
.\start.bat
```
`start.bat` provides:
- Automated `uv` detection and self-installation if missing.
- Verification of compiled datasets (`.npz`, `.bin`).
- Port 8000 conflict resolution (terminates any orphaned process).
- Smart background health check that launches your default browser once the server responds HTTP 200.
- Optional `--no-browser` (or `-n`) flag to run headless.

### Option B: Cross-Platform via `uv`
```bash
# Direct module entrypoint
uv run python -m connectome_engine.server

# Or direct uvicorn launcher
uv run uvicorn connectome_engine.server.app:app --host 127.0.0.1 --port 8000 --ws-ping-interval 30 --ws-ping-timeout 60 --access-log
```

Open your browser at `http://127.0.0.1:8000/`.

---

## Testing & Quality Assurance

The test suite includes **90 automated tests across 25 test files**, verifying biophysical equations, numeric boundaries, graph topology, launcher scripts, API endpoints, and frontend contracts.

```bash
# Run the complete test suite (all 90 tests)
uv run pytest tests/ -v

# Run fast unit & integration tests (no ~1GB connectome file needed)
uv run pytest tests/ \
  --ignore=tests/test_real_connectome_full.py \
  --ignore=tests/test_server_live.py \
  -v

# Run on Windows via start.bat
.\start.bat test
```

### Targeted Test Suites

| Target Area | Test Files | Command |
| :--- | :--- | :--- |
| **Fast Unit & Biophysics** | `test_lif_ei_dynamics.py`, `test_hormones.py`, `test_plasticity_bounds.py`, `test_wave_propagation.py` | `uv run pytest tests/test_lif_ei_dynamics.py tests/test_hormones.py` |
| **LIF Performance (<500ms)** | `test_lif_vectorization.py`, `test_snn_performance_regression.py` | `uv run pytest tests/test_lif_vectorization.py -v` |
| **Real MaleCNS v1.0 Graph** | `test_real_connectome_full.py`, `test_vnc_leg_circuits.py`, `test_vnc_leg_biophysics.py` | `uv run pytest tests/test_real_connectome_full.py tests/test_vnc_leg_circuits.py` |
| **Server & WebSockets** | `test_server_live.py`, `test_soma_api.py` | `uv run pytest tests/test_server_live.py tests/test_soma_api.py -v` |
| **Frontend Contracts** | `test_vnc_kinematics_frontend.py` | `uv run pytest tests/test_vnc_kinematics_frontend.py -v` |
| **Benchmark Reproducibility**| `test_benchmarks_reproducibility.py` | `uv run pytest tests/test_benchmarks_reproducibility.py -v` |

---

## Continuous Integration (CI Pipeline)

Every pull request and push to `main` triggers a 5-job GitHub Actions workflow (`.github/workflows/ci.yml`):

1. **`unit-tests`**: Runs 81 unit & integration tests across biophysics, sensory pipelines, and contracts.
2. **`performance-regression`**: Validates that vectorized 5,000-neuron LIF chunks execute in under 500 ms.
3. **`real-connectome`**: Validates the 166.7K topology, 25.6M synapses, and 381 VNC motor neurons (runs on `main` push).
4. **`server-integration`**: Tests REST endpoints, base64 visual observation ingestion, and WebSocket telemetry broadcasts.
5. **`lint`**: Executes Ruff linting on `src/` and `tests/`, and validates `pyproject.toml` parsing integrity.

Ensure all checks pass locally before pushing your branch!

---

## Empirical Validation & Benchmark Reproducibility

### 1. Benchmark Synchronization
The project enforces strict numerical reproducibility between simulation output, `benchmarks_output.json`, and the Markdown benchmark table in `README.md`.

If you alter any neural parameters, sensory weights, or simulation stepping logic:
```bash
# Regenerate benchmarks_output.json
uv run python scripts/generate_benchmarks.py

# Verify benchmark reproducibility against README.md
uv run pytest tests/test_benchmarks_reproducibility.py -v
```
`test_benchmarks_reproducibility.py` enforces a **$\pm 5\%$ tolerance** on spike counts and firing rates against the published `README.md` table. Update `README.md` to reflect the newly measured values.

### 2. Updating `docs/validation.md`
Whenever a biophysical mechanism, circuit mapping, or numerical parameter is altered, append or update a dated section in [`docs/validation.md`](docs/validation.md) following the established protocol:
- **Title**: `## N. <Mechanism / Feature Name> — YYYY-MM-DD`
- **Context & Motivation**: Why the change was made and what bug or enhancement was addressed.
- **Empirical Measurements**: Actual measured numbers, firing rates, voltages, or timing latencies.
- **Mandatory Boundary Statement**:
  > **Boundary Statement**:
  > *This is evidence of [exact capability demonstrated]; it is **NOT** evidence of [broader biological claim].*

---

## Frontend Guidelines & Bilingual (EN / TR) Contracts

The observation cockpit located in `frontend/` is built with **plain Vanilla JavaScript, CSS3, and Three.js (r128)** — no Webpack, Vite, or npm build steps required.

### 1. Bilingual Architecture (EN / TR)
FlyConnectome 3D provides a full bilingual interface (English and Turkish). All UI text elements use `data-i18n` attributes dynamically mapped to translation dictionaries in `frontend/main.js`:
- Standard neurocomputational terms in English.
- Anatomical and biophysical Turkish terminology (e.g. `VNC Thoraks Heksapod Yürüyüşü`, `Dopamin Şoku`, `Retinal Asimetri`).
- When introducing a new UI string, add it to both `en` and `tr` dictionaries in `frontend/main.js`.

### 2. Strict Frontend Contract Tests
`tests/test_vnc_kinematics_frontend.py` enforces deterministic contracts on the frontend code:
- **HTML IDs**: Preserves HUD container IDs, all 6 leg cards (`leg-card-t1l` through `leg-card-t3r`), Hz readouts, and progress bars.
- **CSS Classes**: Enforces presence of `.vnc-hexapod-box`, `.leg-card.swing-active`, `.tripod-pill`, etc.
- **JS Tripod Coordination**: Validates canonical Tripod A (`L1, R2, L3`) vs. Tripod B (`R1, L2, R3`) phase partitioning.

Always run `uv run pytest tests/test_vnc_kinematics_frontend.py` when touching files in `frontend/`.

---

## Code Style & Linting

We use [Ruff](https://github.com/astral-sh/ruff) for fast Python linting and formatting.

### Linting Commands
```bash
# Check code style and common errors
uv run ruff check src/ tests/ --select=E,W,F,I --ignore=E501

# Automatically fix fixable issues
uv run ruff check src/ tests/ --fix --select=E,W,F,I --ignore=E501
```

### Guidelines
- **Type Annotations**: Use Python 3.12+ type hints (`list[int]`, `dict[str, Any]`, `X | None`).
- **Docstrings**: Provide clear explanations for classes and functions, explicitly noting biological context or computational simplifications.
- **No Secrets**: Never commit API keys, personal credentials, or local system paths.
- **Line Length**: While `E501` is ignored for mathematical equations and ASCII diagrams, keep lines readable and clean.

---

## Submitting a Pull Request

1. **Fork & Branch**:
   ```bash
   git checkout -b feat/your-descriptive-branch-name
   ```
2. **Implement & Test**:
   Make your changes, ensuring code is formatted and tested.
3. **Commit Messages**:
   Follow [Conventional Commits](https://www.conventionalcommits.org/):
   ```
   feat(vnc): integrate mesothoracic T2 motor pool swing elevation
   fix(lif): clamp potassium reversal potential to prevent numerical divergence
   perf(snn): optimize vectorized CSR dot product in spike accumulation
   docs(validation): add section 12 on phototaxis steering gain verification
   test(frontend): add contract test for dual-viewport canvas resizing
   ```
4. **Push & Open PR**:
   Push to your fork and submit a PR to `main`. Include a clear description of what changed, why, and which tests pass.

---

## Pre-PR Checklist

Before marking your pull request as ready for review, please verify:

- [ ] All 90 tests pass (`uv run pytest tests/ -v`).
- [ ] Ruff linting passes without warnings (`uv run ruff check src/ tests/ --select=E,W,F,I --ignore=E501`).
- [ ] `pyproject.toml` is valid (`uv run python -c "import tomllib; tomllib.loads(open('pyproject.toml').read())"`).
- [ ] If biophysical dynamics or sensory stimuli changed, benchmarks were regenerated (`uv run python scripts/generate_benchmarks.py`) and verified (`test_benchmarks_reproducibility.py`).
- [ ] If frontend files were modified, both English and Turkish dictionaries were updated and `test_vnc_kinematics_frontend.py` passed.
- [ ] If new models or biological claims were introduced, [`docs/validation.md`](docs/validation.md) was updated with an empirical log and a Boundary Statement.
- [ ] Commit history is clean and uses Conventional Commit formatting.

---

## License

By contributing to FlyConnectome 3D, you agree that your contributions will be licensed under the project's [MIT License](LICENSE).
