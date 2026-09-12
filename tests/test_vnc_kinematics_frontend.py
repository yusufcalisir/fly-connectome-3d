"""Deterministic Unit Tests for Frontend VNC Hexapod HUD and Kinematic Contracts.

Verifies that HTML layout, CSS classes, and JavaScript translation dictionaries
and tripod groupings conform strictly to the biological VNC hexapod specification.
ZERO MOCK, ZERO RANDOM NUMBERS.
"""

from pathlib import Path
import re
import pytest

FRONTEND_DIR = Path(__file__).resolve().parents[1] / "frontend"


def test_vnc_hexapod_html_contract():
    """Verify that index.html defines all required VNC Hexapod HUD elements and leg IDs."""
    html_file = FRONTEND_DIR / "index.html"
    assert html_file.exists(), "frontend/index.html does not exist."

    content = html_file.read_text(encoding="utf-8")

    # 1. Container and Header
    assert "vnc-hexapod-box" in content, "Missing .vnc-hexapod-box in index.html"
    assert 'data-i18n="title_vnc_hexapod"' in content, "Missing title_vnc_hexapod translation tag"
    assert 'data-i18n="tag_vnc_cpg"' in content, "Missing tag_vnc_cpg translation tag"

    # 2. Tripod Alternation Badges
    assert 'id="tripod-a-badge"' in content, "Missing #tripod-a-badge in index.html"
    assert 'id="tripod-b-badge"' in content, "Missing #tripod-b-badge in index.html"

    # 3. All 6 Leg Cards
    expected_cards = [
        "leg-card-t1l",
        "leg-card-t1r",
        "leg-card-t2l",
        "leg-card-t2r",
        "leg-card-t3l",
        "leg-card-t3r",
    ]
    for card_id in expected_cards:
        assert f'id="{card_id}"' in content, f"Missing #{card_id} in index.html"

    # 4. All 6 Leg Hz Readout Spans
    expected_hz_ids = [
        "vnc-t1l-hz",
        "vnc-t1r-hz",
        "vnc-t2l-hz",
        "vnc-t2r-hz",
        "vnc-t3l-hz",
        "vnc-t3r-hz",
    ]
    for hz_id in expected_hz_ids:
        assert f'id="{hz_id}"' in content, f"Missing #{hz_id} in index.html"

    # 5. All 6 Leg Progress Bar Fill Elements
    expected_fill_ids = [
        "vnc-t1l-fill",
        "vnc-t1r-fill",
        "vnc-t2l-fill",
        "vnc-t2r-fill",
        "vnc-t3l-fill",
        "vnc-t3r-fill",
    ]
    for fill_id in expected_fill_ids:
        assert f'id="{fill_id}"' in content, f"Missing #{fill_id} in index.html"


def test_vnc_hexapod_css_styles_contract():
    """Verify that styles.css defines all styling and animation classes for VNC Hexapod HUD."""
    css_file = FRONTEND_DIR / "styles.css"
    assert css_file.exists(), "frontend/styles.css does not exist."

    content = css_file.read_text(encoding="utf-8")

    required_classes = [
        ".vnc-hexapod-box",
        ".vnc-header",
        ".vnc-tag",
        ".tripod-status-row",
        ".tripod-pill",
        ".tripod-pill.active-stance",
        ".tripod-pill.active-swing",
        ".hexapod-leg-grid",
        ".leg-card",
        ".leg-card.swing-active",
        ".leg-card.stance-active",
        ".progress-bar.leg-bar",
    ]

    for cls in required_classes:
        assert cls in content, f"Missing CSS class '{cls}' in styles.css"


def test_vnc_main_js_translations_contract():
    """Verify that main.js provides complete EN and TR translations for VNC Hexapod elements."""
    js_file = FRONTEND_DIR / "main.js"
    assert js_file.exists(), "frontend/main.js does not exist."

    content = js_file.read_text(encoding="utf-8")

    # Check EN translations
    assert "title_vnc_hexapod: 'VNC THORACIC HEXAPOD GAIT'" in content
    assert "tag_vnc_cpg: 'CPG Alternating Tripod'" in content

    # Check TR translations
    assert "title_vnc_hexapod: 'VNC THORAKS HEKSAPOD YÜRÜYÜŞÜ'" in content
    assert "tag_vnc_cpg: 'CPG Alternatif Tripod'" in content


def test_vnc_main_js_tripod_coordination_contract():
    """Verify that main.js implements canonical Tripod A vs Tripod B partitioning."""
    js_file = FRONTEND_DIR / "main.js"
    content = js_file.read_text(encoding="utf-8")

    # Tripod A: pro_L (L1), meso_R (R2), meta_L (L3)
    # Tripod B: pro_R (R1), meso_L (L2), meta_R (R3)
    assert "tripodGroup: (cfg.name === 'pro_L' || cfg.name === 'meso_R' || cfg.name === 'meta_L') ? 'A' : 'B'" in content

    # Check default angles stored for swing elevation
    assert "defaultFemurRotX: femur.rotation.x" in content
    assert "defaultTibiaRotZ: tibia.rotation.z" in content

    # Check phase synchronization
    assert "this.cpgTripodPhase" in content
    assert "telemetry.vnc_legs" in content
