from dataclasses import replace
from math import isclose, pi, sqrt

import pytest

from aeromat.model import Inputs, MATERIALS, Material, calculate, isa_troposphere

BASE = Inputs()
AL = MATERIALS["Aluminium 2024-T3"]


def test_isa_sea_level():
    temperature, rho, viscosity = isa_troposphere(0)
    assert temperature == pytest.approx(288.15)
    assert rho == pytest.approx(1.225, rel=0.001)
    assert viscosity == pytest.approx(1.789e-5, rel=0.005)


def test_isa_density_drops_with_altitude():
    assert isa_troposphere(10000)[1] < isa_troposphere(1000)[1]


def test_default_model_is_finite_and_screening_pass():
    x = calculate(BASE, AL)
    assert x.screening_pass
    assert 0 < x.mach < 0.3
    assert x.root_moment_nm > 0
    assert x.bending_stress_mpa > 0
    assert x.mission_electricity_kwh > 0


def test_two_spar_mass_is_area_times_span_times_density():
    x = calculate(BASE, AL)
    area = BASE.spar_width_m * BASE.spar_height_m - (BASE.spar_width_m - 2*BASE.spar_wall_thickness_m) * (BASE.spar_height_m - 2*BASE.spar_wall_thickness_m)
    span = sqrt(BASE.aspect_ratio * BASE.wing_area_m2)
    assert x.spar_mass_kg == pytest.approx(area * span * AL.density_kg_m3)


def test_lift_coefficient_and_induced_drag_closed_form():
    x = calculate(BASE, AL)
    cl = x.total_mass_kg * 9.80665 / (x.dynamic_pressure_pa * BASE.wing_area_m2)
    assert x.lift_coefficient == pytest.approx(cl)
    assert x.induced_drag_n == pytest.approx(x.dynamic_pressure_pa * BASE.wing_area_m2 * cl**2 / (pi * BASE.oswald_efficiency * BASE.aspect_ratio))


def test_drag_decomposition_reconstructs_total():
    x = calculate(BASE, AL)
    assert x.total_drag_n == pytest.approx(x.skin_drag_n + x.induced_drag_n + x.other_drag_n)


def test_maneuver_load_factor_changes_stress_not_aerodynamic_drag():
    a = calculate(replace(BASE, load_factor=1), AL)
    b = calculate(replace(BASE, load_factor=2), AL)
    assert b.root_moment_nm == pytest.approx(2 * a.root_moment_nm)
    assert b.bending_stress_mpa == pytest.approx(2 * a.bending_stress_mpa)
    assert b.tip_deflection_m == pytest.approx(2 * a.tip_deflection_m)
    assert a.total_drag_n == pytest.approx(b.total_drag_n)


def test_structural_deflection_scales_with_elastic_modulus():
    low_e = replace(AL, youngs_modulus_gpa=AL.youngs_modulus_gpa / 2)
    a, b = calculate(BASE, AL), calculate(BASE, low_e)
    assert b.tip_deflection_m == pytest.approx(2 * a.tip_deflection_m)
    assert b.bending_stress_mpa == pytest.approx(a.bending_stress_mpa)


def test_reduced_height_reduces_mass_but_increases_stress():
    a, b = calculate(BASE, AL), calculate(replace(BASE, spar_height_m=0.17), AL)
    assert b.spar_mass_kg < a.spar_mass_kg
    assert b.bending_stress_mpa > a.bending_stress_mpa


def test_induced_drag_rises_with_mass():
    lighter = calculate(BASE, AL)
    heavier_material = replace(AL, density_kg_m3=8000)
    heavier = calculate(BASE, heavier_material)
    assert heavier.induced_drag_n > lighter.induced_drag_n
    assert heavier.mission_electricity_kwh > lighter.mission_electricity_kwh


def test_distance_scales_operational_energy_and_carbon():
    a = calculate(BASE, AL)
    b = calculate(replace(BASE, route_distance_km=BASE.route_distance_km * 2), AL)
    assert b.mission_electricity_kwh == pytest.approx(2 * a.mission_electricity_kwh)
    assert b.operational_kgco2e == pytest.approx(2 * a.operational_kgco2e)
    assert b.spar_embodied_kgco2e == pytest.approx(a.spar_embodied_kgco2e)


def test_embodied_factor_and_allocation():
    r = calculate(BASE, replace(AL, embodied_kgco2e_per_kg=0))
    assert r.spar_embodied_kgco2e == 0
    assert r.total_mission_kgco2e == pytest.approx(r.operational_kgco2e)
    assert calculate(replace(BASE, service_missions=5000), AL).allocated_embodied_kgco2e_per_mission == pytest.approx(2 * calculate(BASE, AL).allocated_embodied_kgco2e_per_mission)


def test_thermal_heat_flux_reverses_direction():
    cold = calculate(replace(BASE, inner_skin_temperature_c=-20), AL)
    hot = calculate(replace(BASE, inner_skin_temperature_c=50), AL)
    assert cold.thermal_flux_w_m2 > 0
    assert hot.thermal_flux_w_m2 < 0


def test_thermal_conductivity_changes_heat_flux():
    high_k = replace(AL, conductivity_w_mk=1000)
    low_k = replace(AL, conductivity_w_mk=0.1)
    p = replace(BASE, inner_skin_temperature_c=-20)
    assert calculate(p, high_k).thermal_flux_w_m2 > calculate(p, low_k).thermal_flux_w_m2


def test_over_stall_flags_failure():
    x = calculate(replace(BASE, speed_m_s=14), AL)
    assert not x.lift_feasible
    assert not x.screening_pass
    assert any("CLmax" in warning for warning in x.warnings)


def test_supersonic_inappropriate_model_warns_and_fails_screening():
    x = calculate(replace(BASE, speed_m_s=220), AL)
    assert x.mach > 0.3
    assert not x.within_low_mach_envelope
    assert not x.screening_pass


@pytest.mark.parametrize("overrides", [
    {"altitude_m": -1}, {"altitude_m": 11001}, {"speed_m_s": 0},
    {"spar_wall_thickness_m": 0.06}, {"spar_height_m": 0.001},
    {"oswald_efficiency": 1.5}, {"route_distance_km": -10},
    {"grid_kgco2e_per_kwh": -0.1}, {"wing_area_m2": float('nan')},
    {"inner_skin_temperature_c": -273.15},
])
def test_invalid_inputs_are_rejected(overrides):
    with pytest.raises(ValueError):
        calculate(replace(BASE, **overrides), AL)


def test_rejects_invalid_material():
    with pytest.raises(ValueError):
        calculate(BASE, replace(AL, density_kg_m3=-1))


def test_flat_output_is_serializable():
    import json
    x = calculate(BASE, AL)
    assert isinstance(json.dumps(x.flat()), str)
    assert isinstance(x.flat()['warnings'], str)
