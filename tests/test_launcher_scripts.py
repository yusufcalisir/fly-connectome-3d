"""Deterministic Unit Tests for Windows Launcher Scripts (start.bat and run.bat).

Verifies script existence, argument forwarding, subcommands, dataset checks,
and smart healthcheck polling mechanisms.
ZERO MOCK, ZERO RANDOM NUMBERS.
"""

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_launcher_scripts_exist():
    """Verify that start.bat and run.bat exist at repository root."""
    start_bat = REPO_ROOT / "start.bat"
    run_bat = REPO_ROOT / "run.bat"

    assert start_bat.exists(), "start.bat is missing from repository root."
    assert run_bat.exists(), "run.bat is missing from repository root."


def test_run_bat_forwards_arguments():
    """Verify that run.bat forwards all CLI arguments to start.bat."""
    run_bat = REPO_ROOT / "run.bat"
    content = run_bat.read_text(encoding="utf-8")

    assert "start.bat" in content
    assert "%*" in content, "run.bat must forward %* arguments to start.bat"


def test_start_bat_capabilities_contract():
    """Verify start.bat has dataset verification, soma checking, subcommands, and healthcheck."""
    start_bat = REPO_ROOT / "start.bat"
    content = start_bat.read_text(encoding="utf-8")

    # 1. Dataset checks
    assert "malecns_v1_graph.npz" in content, "start.bat must check for malecns_v1_graph.npz"
    assert "soma_coordinates_141k.bin" in content, "start.bat must check for soma_coordinates_141k.bin"
    assert "compile_coordinates.py" in content, "start.bat must compile coordinates if missing"

    # 2. Subcommands
    assert 'if /i "%~1"=="test"' in content, "start.bat must support 'test' subcommand"
    assert 'if /i "%~1"=="compile"' in content, "start.bat must support 'compile' subcommand"

    # 3. Smart browser healthcheck
    assert "Invoke-WebRequest" in content, "start.bat must poll HTTP healthcheck"
    assert "--no-browser" in content, "start.bat must support --no-browser flag"

    # 4. Clean window title without ugly quotes
    assert "title FlyConnectome 3D" in content
    assert 'title "' not in content, "start.bat window title should not have literal quotes"


@pytest.mark.skipif(sys.platform != "win32", reason="cmd.exe batch execution requires Windows")
def test_start_bat_test_subcommand_execution():
    """Verify that 'start.bat test' executes pytest cleanly through Windows cmd."""
    cmd = ["cmd.exe", "/c", "start.bat", "test", "tests/test_vnc_kinematics_frontend.py"]
    res = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=30)

    assert res.returncode == 0, f"start.bat test failed with code {res.returncode}:\n{res.stdout}\n{res.stderr}"
    assert "passed in" in res.stdout
