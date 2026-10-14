from dataclasses import replace
import pytest

from aeromat.analysis import best_feasible, compare_materials, from_record, height_sweep
from aeromat.model import Inputs, MATERIALS, calculate


def test_compare_materials_returns_each_selected():
    materials = list(MATERIALS.values())
    results = compare_materials(Inputs(), materials)
    assert len(results) == len(materials)
    assert {x.material for x in results} == set(MATERIALS)


def test_height_sweep_respects_bounds_and_steps():
    rows = height_sweep(Inputs(), [MATERIALS['Aluminium 2024-T3']], 0.2, 0.3, 11)
    assert len(rows) == 11
    assert rows[0].spar_height_m == pytest.approx(0.2)
    assert rows[-1].spar_height_m == pytest.approx(0.3)


def test_best_feasible_is_minimum_of_feasible_only():
    rows = height_sweep(Inputs(), MATERIALS.values(), 0.12, 0.40, 20)
    winner = best_feasible(rows)
    assert winner.screening_pass
    assert winner.spar_mass_kg == pytest.approx(min(x.spar_mass_kg for x in rows if x.screening_pass))


def test_no_feasible_design_returns_none():
    rows = compare_materials(replace(Inputs(), speed_m_s=220), MATERIALS.values())
    assert best_feasible(rows) is None


def test_sweep_rejects_broken_bounds_or_too_few_steps():
    with pytest.raises(ValueError):
        height_sweep(Inputs(), MATERIALS.values(), 0.4, 0.1)
    with pytest.raises(ValueError):
        height_sweep(Inputs(), MATERIALS.values(), 0.1, 0.4, 1)


def test_batch_numeric_parsing_and_default_inheritance():
    p = Inputs()
    parsed = from_record({'speed_m_s': '78', 'altitude_m': '', 'misc': 25}, p)
    assert parsed.speed_m_s == 78.0
    assert parsed.altitude_m == p.altitude_m


def test_bad_batch_input_gives_explanatory_error():
    with pytest.raises(ValueError, match='speed_m_s'):
        from_record({'speed_m_s': 'very fast'}, Inputs())


def test_material_names_and_baseline_are_stable():
    assert 'Aluminium 7075-T6' in MATERIALS
    assert calculate(Inputs(), MATERIALS['Aluminium 7075-T6']).screening_pass
