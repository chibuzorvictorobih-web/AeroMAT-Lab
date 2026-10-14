"""Streamlit interface regression tests.

These check app startup, navigation rendering, and recalculation after an input
change. They run without opening a browser and do not validate aircraft physics.
"""
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from aeromat.model import Inputs, MATERIALS, calculate

APP = Path(__file__).resolve().parents[1] / "app.py"


@pytest.fixture
def ui():
    app = AppTest.from_file(str(APP), default_timeout=60).run()
    assert not app.exception, [str(error) for error in app.exception]
    assert not app.error, [str(error) for error in app.error]
    return app


def test_app_starts_and_renders_all_five_sections(ui):
    assert any("AeroMAT Lab" in item.value for item in ui.title)
    assert len(ui.tabs) == 5
    labels = [tab.label for tab in ui.tabs]
    assert any("Design dashboard" in label for label in labels)
    assert any("Compare materials" in label for label in labels)
    assert any("Spar design explorer" in label for label in labels)
    assert any("Batch CSV" in label for label in labels)
    assert any("Methods & scope" in label for label in labels)
    assert any("Your aircraft design at a glance" in item.value for item in ui.subheader)


def test_airspeed_edit_recalculates_displayed_mach(ui):
    speed = next(widget for widget in ui.number_input if widget.label == "Airspeed [m/s]")
    speed.set_value(75.0)
    ui.run()
    assert not ui.exception, [str(error) for error in ui.exception]
    assert not ui.error, [str(error) for error in ui.error]
    expected = calculate(Inputs(speed_m_s=75.0), MATERIALS["Aluminium 2024-T3"])
    assert any(f"{expected.mach:.3f}" in item.value for item in ui.markdown)
    assert any("aeromat-metrics" in item.value for item in ui.markdown)


def test_material_selection_reruns_without_errors(ui):
    selector = next(widget for widget in ui.selectbox if widget.label == "Spar and modelled skin material")
    selector.set_value("Steel 4130")
    ui.run()
    assert not ui.exception, [str(error) for error in ui.exception]
    assert not ui.error, [str(error) for error in ui.error]
    expected = calculate(Inputs(), MATERIALS["Steel 4130"])
    assert any(f"{expected.spar_mass_kg:,.1f} kg" in item.value for item in ui.markdown)
