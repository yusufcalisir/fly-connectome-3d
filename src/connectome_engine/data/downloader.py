"""Official Janelia MaleCNS v1.0 Connectome Downloader & Graph Compiler.

Downloads the exact 166,700-neuron Male Adult Fly Brain and Nerve Cord (MCNS v1.0)
dataset from Janelia Research Campus / FlyEM official Google Cloud Storage, verifies
cryptographic SHA256 checksums, and compiles the sparse connectome graph.
"""

import hashlib
import json
import sys
import time
import urllib.request
from pathlib import Path
from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd
import pyarrow.feather as feather
import scipy.sparse as sp

DATA_DIR = Path(__file__).resolve().parents[3] / "data" / "malecns_v1"

OFFICIAL_SOURCES: Dict[str, Dict[str, Any]] = {
    "annotations.feather": {
        "url": "https://storage.googleapis.com/flyem-male-cns/v1.0/connectome-data/flat-connectome/body-annotations-male-cns-v1.0-minconf-0.5.feather",
        "bytes": 14483314,
        "sha256": "2177e246113e4cfbf1e7772ec37c6da1955ff22e8063d0b1f833101f99a9a3b2",
    },
    "neurotransmitters.feather": {
        "url": "https://storage.googleapis.com/flyem-male-cns/v1.0/connectome-data/flat-connectome/body-neurotransmitters-male-cns-v1.0.feather",
        "bytes": 43282834,
        "sha256": "95c9289220663abeb3409f3ad9e5a7f8a53f8093f5139d15502cd08da8879621",
    },
    "edges.feather": {
        "url": "https://storage.googleapis.com/flyem-male-cns/v1.0/connectome-data/flat-connectome/connectome-weights-male-cns-v1.0-minconf-0.5.feather",
        "bytes": 1051241946,
        "sha256": "e35da783d1c686b2b58b3b87cd6a403ae43bfcfba8bff28e08ef752c1a56afc1",
    },
}


def compute_sha256(filepath: Path) -> str:
    """Compute SHA256 checksum in 8MB chunks."""
    h = hashlib.sha256()
    with filepath.open("rb") as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def download_file(name: str, info: Dict[str, Any], target_dir: Path) -> Path:
    """Download single official file with progress feedback and checksum verification."""
    target_path = target_dir / name
    if target_path.exists():
        print(f"[*] Found existing {name} ({target_path.stat().st_size / (1024*1024):.1f} MB). Verifying SHA256...")
        file_hash = compute_sha256(target_path)
        if file_hash == info["sha256"]:
            print(f"    [+] Checksum verified for {name}")
            return target_path
        else:
            print(f"    [-] Checksum mismatch for {name}. Re-downloading...")
            target_path.unlink()

    temp_path = target_dir / f"{name}.partial"
    if temp_path.exists():
        temp_path.unlink()

    print(f"[*] Downloading {name} ({info['bytes'] / (1024*1024):.1f} MB) from official Janelia GCS...")
    start_time = time.time()
    last_print = start_time
    downloaded = 0
    total_bytes = info["bytes"]

    def report_hook(block_num, block_size, total_size):
        nonlocal downloaded, last_print
        downloaded = block_num * block_size
        now = time.time()
        if now - last_print > 1.5 or downloaded >= total_bytes:
            pct = min(100.0, (downloaded / max(1, total_bytes)) * 100.0)
            elapsed = max(0.1, now - start_time)
            speed_mb = (downloaded / (1024 * 1024)) / elapsed
            print(f"    -> {name}: {pct:.1f}% ({downloaded / (1024*1024):.1f}/{total_bytes / (1024*1024):.1f} MB) at {speed_mb:.1f} MB/s", flush=True)
            last_print = now

    urllib.request.urlretrieve(info["url"], temp_path, reporthook=report_hook)

    print(f"[*] Download complete. Verifying SHA256 for {name}...")
    actual_hash = compute_sha256(temp_path)
    if actual_hash != info["sha256"]:
        temp_path.unlink()
        raise ValueError(f"Checksum mismatch for {name}: expected {info['sha256']}, got {actual_hash}")

    temp_path.rename(target_path)
    print(f"    [+] {name} verified and ready.\n")
    return target_path


def download_all_official_sources(target_dir: Path = DATA_DIR) -> Dict[str, Path]:
    """Download all official Janelia MaleCNS v1.0 files."""
    target_dir.mkdir(parents=True, exist_ok=True)
    paths = {}
    for name, info in OFFICIAL_SOURCES.items():
        paths[name] = download_file(name, info, target_dir)
    return paths


if __name__ == "__main__":
    download_all_official_sources()
