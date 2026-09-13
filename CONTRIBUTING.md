# Contributing to FlyConnectome 3D

Thank you for your interest in contributing! This document outlines how to work with the codebase, report issues, and submit improvements.

---

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Report a Bug](#how-to-report-a-bug)
- [How to Suggest a Feature](#how-to-suggest-a-feature)
- [Development Setup](#development-setup)
- [Running Tests](#running-tests)
- [Submitting a Pull Request](#submitting-a-pull-request)
- [Validation & Honesty Standard](#validation--honesty-standard)
- [Coding Style](#coding-style)

---

## Code of Conduct

Be respectful, constructive, and honest. Scientific accuracy matters — do not fabricate or overstate biological claims. See [docs/validation.md](docs/validation.md) for the project's empirical honesty standard.

---

## How to Report a Bug

1. Search [existing issues](https://github.com/yusufcalisir/fly-connectome-3d/issues) first.
2. If not found, open a new issue with:
   - A clear title and description.
   - Steps to reproduce the problem.
   - The exact error message or unexpected output.
   - Your Python version and OS.

---

## How to Suggest a Feature

Open an issue tagged `enhancement`. Describe:
- The motivation and use case.
- Whether it requires new biophysical claims (if so, cite a source or mark it as a simplification).

---

## Development Setup

This project uses [`uv`](https://github.com/astral-sh/uv) for fast, reproducible dependency management.

```bash
# 1. Clone the repository
git clone https://github.com/yusufcalisir/fly-connectome-3d.git
cd fly-connectome-3d

# 2. Install uv (if not already installed)
pip install uv

# 3. Create virtualenv and install all dependencies (including dev tools)
uv sync --dev

# 4. Download the Janelia MaleCNS v1.0 connectome data (~1.1 GB)
uv run python src/connectome_engine/data/downloader.py

# 5. Compile the connectome graph
uv run python src/connectome_engine/data/compile_malecns.py

# 6. Run the server
uv run python -m connectome_engine.server
```

The web interface will be available at `http://localhost:8000`.

---

## Running Tests

```bash
# Run the full test suite (90 tests)
uv run pytest tests/ -v

# Run only unit tests (no large connectome file needed)
uv run pytest tests/ \
  --ignore=tests/test_real_connectome_full.py \
  --ignore=tests/test_server_live.py \
  -v

# Run linting
uv run ruff check src/ tests/ --select=E,W,F,I --ignore=E501
```

All 90 tests must pass before submitting a pull request.

---

## Submitting a Pull Request

1. Fork the repository and create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Make your changes and ensure all tests pass.
3. If you are adding or changing biophysical behaviour, **add or update a section in [`docs/validation.md`](docs/validation.md)** using the established format:
   - Describe exactly what was changed and why.
   - Include empirical verification (measured values, test output).
   - End with the mandatory **Boundary Statement** template:
     > *This is evidence of [exact capability demonstrated]; it is **NOT** evidence of [broader biological claim].*
4. Commit with a clear message following [Conventional Commits](https://www.conventionalcommits.org/):
   ```
   feat(hormones): add serotonin release kinetics model
   fix(lif): clamp potassium reversal to prevent numerical runaway
   docs(validation): add section 12 – serotonin ODE verification
   ```
5. Open a pull request against `main` with a description of what you changed and why.

---

## Validation & Honesty Standard

This project follows a strict empirical honesty standard:

- **Do not fabricate numbers.** All benchmarks must be produced by running the actual code.
- **Do not overstate biological accuracy.** Every model simplification must be documented explicitly.
- **Cite sources correctly.** If a parameter value is derived from literature, verify the exact figure in the original paper. If it is an engineering choice, say so plainly.

See [docs/validation.md](docs/validation.md) for the full record of verified claims and their boundary statements.

---

## Coding Style

- **Python**: Formatted and linted with [Ruff](https://github.com/astral-sh/ruff). Maximum line length is not enforced (E501 ignored), but keep lines readable.
- **Docstrings**: Use plain English. Describe what a function does, its parameters, and any biological interpretation caveats.
- **Frontend (JS/CSS)**: Plain Vanilla JS and CSS — no build step, no framework dependency.
- **No secrets in code**: API keys, credentials, or private data must never be committed.

---

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
