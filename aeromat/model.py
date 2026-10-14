"""Transparent, low-order integrated aerospace screening models.

Educational engineering estimation only. Not an aircraft design or flight-safety tool.
No CFD/FEA, certification analysis, fatigue or aeroelasticity is claimed.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from math import isfinite, pi, sqrt

GRAVITY = 9.80665
GAS_CONSTANT = 287.05287
GAMMA = 1.4
CP_AIR = 1005.0
PRANDTL = 0.71


@dataclass(frozen=True)
class Material:
    name: str
    density_kg_m3: float
    youngs_modulus_gpa: float
    yield_strength_mpa: float
    conductivity_w_mk: float
    embodied_kgco2e_per_kg: float


# Representative, rounded classroom values, NOT guaranteed design allowables.
# Embodied-carbon values are explicit ILLUSTRATIVE placeholders, not verified LCA data.
MATERIALS = {
    "Aluminium 2024-T3": Material("Aluminium 2024-T3", 2780, 73.1, 345, 121, 8.0),
    "Aluminium 7075-T6": Material("Aluminium 7075-T6", 2810, 71.7, 503, 130, 8.0),
    "Titanium Ti-6Al-4V": Material("Titanium Ti-6Al-4V", 4430, 113.8, 880, 6.7, 20.0),
    "Steel 4130": Material("Steel 4130", 7850, 205, 435, 42.7, 2.4),
}


@dataclass(frozen=True)
class Inputs:
    altitude_m: float = 1500.0
    speed_m_s: float = 65.0
    wing_area_m2: float = 16.0
    aspect_ratio: float = 8.0
    aircraft_mass_excl_spars_kg: float = 900.0
    load_factor: float = 2.5
    spar_width_m: float = 0.12
    spar_height_m: float = 0.24
    spar_wall_thickness_m: float = 0.006
    skin_thickness_m: float = 0.002
    inner_skin_temperature_c: float = 20.0
    other_parasite_cd0: float = 0.018
    oswald_efficiency: float = 0.80
    propeller_efficiency: float = 0.82
    motor_efficiency: float = 0.93
    route_distance_km: float = 100.0
    grid_kgco2e_per_kwh: float = 0.35
    service_missions: float = 10000.0
    cl_max: float = 1.50
    required_yield_safety_factor: float = 1.50
    max_tip_deflection_ratio: float = 0.08


@dataclass(frozen=True)
class Result:
    material: str
    spar_height_m: float
    altitude_m: float
    speed_m_s: float
    air_temperature_c: float
    air_density_kg_m3: float
    dynamic_pressure_pa: float
    mach: float
    reynolds_chord: float
    flow_regime: str
    wingspan_m: float
    mean_chord_m: float
    spar_mass_kg: float
    total_mass_kg: float
    lift_coefficient: float
    stall_speed_m_s: float
    skin_drag_n: float
    induced_drag_n: float
    other_drag_n: float
    total_drag_n: float
    lift_to_drag: float
    root_moment_nm: float
    bending_stress_mpa: float
    yield_safety_factor: float
    tip_deflection_m: float
    tip_deflection_ratio: float
    convection_coefficient_w_m2k: float
    thermal_flux_w_m2: float
    thermal_power_w: float
    outer_skin_temperature_c: float
    mission_electricity_kwh: float
    operational_kgco2e: float
    spar_embodied_kgco2e: float
    allocated_embodied_kgco2e_per_mission: float
    total_mission_kgco2e: float
    structurally_feasible: bool
    lift_feasible: bool
    within_low_mach_envelope: bool
    screening_pass: bool
    warnings: tuple[str, ...]

    def flat(self) -> dict:
        record = asdict(self)
        record["warnings"] = "; ".join(self.warnings)
        return record


def _check_finite(label: str, value: float, low: float | None = None,
                  high: float | None = None, strict_low: bool = False) -> None:
    if not isfinite(value):
        raise ValueError(f"{label}: must be finite")
    if low is not None and (value <= low if strict_low else value < low):
        qualifier = ">" if strict_low else ">="
        raise ValueError(f"{label}: must be {qualifier} {low}")
    if high is not None and value > high:
        raise ValueError(f"{label}: must be <= {high}")


def validate(inputs: Inputs, material: Material) -> None:
    checks = {
        "Altitude (m)": (inputs.altitude_m, 0, 11000, False),
        "Speed (m/s)": (inputs.speed_m_s, 0, 350, True),
        "Wing area (m²)": (inputs.wing_area_m2, 0, 10000, True),
        "Aspect ratio": (inputs.aspect_ratio, 0, 200, True),
        "Mass excluding spars (kg)": (inputs.aircraft_mass_excl_spars_kg, 0, 1e7, True),
        "Maneuver load factor": (inputs.load_factor, 0, 100, True),
        "Spar width (m)": (inputs.spar_width_m, 0, 100, True),
        "Spar height (m)": (inputs.spar_height_m, 0, 100, True),
        "Spar wall thickness (m)": (inputs.spar_wall_thickness_m, 0, 10, True),
        "Wing skin thickness (m)": (inputs.skin_thickness_m, 0, 10, True),
        "Inside skin temperature (°C)": (inputs.inner_skin_temperature_c, -273.15, 1000, True),
        "Other parasite CD0": (inputs.other_parasite_cd0, 0, 10, False),
        "Oswald efficiency": (inputs.oswald_efficiency, 0, 1, True),
        "Propeller efficiency": (inputs.propeller_efficiency, 0, 1, True),
        "Motor efficiency": (inputs.motor_efficiency, 0, 1, True),
        "Trip distance (km)": (inputs.route_distance_km, 0, 1e7, True),
        "Grid factor (kgCO2e/kWh)": (inputs.grid_kgco2e_per_kwh, 0, 1e4, False),
        "Number of lifetime missions": (inputs.service_missions, 0, 1e12, True),
        "Maximum lift coefficient": (inputs.cl_max, 0, 20, True),
        "Minimum safety factor": (inputs.required_yield_safety_factor, 0, None, True),
        "Maximum tip deflection ratio": (inputs.max_tip_deflection_ratio, 0, 1, True),
        "Material density": (material.density_kg_m3, 0, 1e6, True),
        "Material Young's modulus": (material.youngs_modulus_gpa, 0, 1e5, True),
        "Material yield strength": (material.yield_strength_mpa, 0, 1e6, True),
        "Material thermal conductivity": (material.conductivity_w_mk, 0, 1e6, True),
        "Material embodied factor": (material.embodied_kgco2e_per_kg, 0, 1e6, False),
    }
    for label, (value, low, high, strict_low) in checks.items():
        _check_finite(label, float(value), low, high, strict_low)
    if inputs.spar_wall_thickness_m * 2 >= min(inputs.spar_width_m, inputs.spar_height_m):
        raise ValueError("Spar wall thickness must be less than half of both width and height")


def isa_troposphere(altitude_m: float) -> tuple[float, float, float]:
    """Standard atmosphere (0–11 km): temperature K, density kg/m³, mu Pa·s."""
    _check_finite("Altitude (m)", altitude_m, 0, 11000)
    temperature = 288.15 - 0.0065 * altitude_m
    pressure = 101325.0 * (temperature / 288.15) ** (GRAVITY / (GAS_CONSTANT * 0.0065))
    density = pressure / (GAS_CONSTANT * temperature)
    viscosity = 1.716e-5 * (temperature / 273.15) ** 1.5 * (273.15 + 110.4) / (temperature + 110.4)
    return temperature, density, viscosity


def calculate(inputs: Inputs, material: Material) -> Result:
    validate(inputs, material)
    temp_k, rho, mu = isa_troposphere(inputs.altitude_m)
    span = sqrt(inputs.aspect_ratio * inputs.wing_area_m2)
    chord = inputs.wing_area_m2 / span
    half_span = span / 2.0
    width, height, wall = (inputs.spar_width_m, inputs.spar_height_m,
                           inputs.spar_wall_thickness_m)
    area_section = width * height - (width - 2 * wall) * (height - 2 * wall)
    inertia = (width * height ** 3 - (width - 2 * wall) * (height - 2 * wall) ** 3) / 12
    spar_mass = area_section * span * material.density_kg_m3  # both half-wing spars
    total_mass = inputs.aircraft_mass_excl_spars_kg + spar_mass
    weight = total_mass * GRAVITY

    q = 0.5 * rho * inputs.speed_m_s ** 2
    reynolds = rho * inputs.speed_m_s * chord / mu
    mach = inputs.speed_m_s / sqrt(GAMMA * GAS_CONSTANT * temp_k)
    cl = weight / (q * inputs.wing_area_m2)  # 1-g level flight
    stall_speed = sqrt(2 * weight / (rho * inputs.wing_area_m2 * inputs.cl_max))

    if reynolds <= 5e5:
        regime = "laminar correlation"
        cf = 1.328 / sqrt(reynolds)
        nusselt = 0.664 * sqrt(reynolds) * PRANDTL ** (1 / 3)
    else:
        regime = "transition-corrected turbulent correlation"
        cf = 0.074 / (reynolds ** 0.2) - 1742 / reynolds
        nusselt = (0.037 * reynolds ** 0.8 - 871) * PRANDTL ** (1 / 3)
    # Fallback to positive laminar estimates only outside ordinary correlation range.
    if cf <= 0 or nusselt <= 0:
        raise ValueError("Reynolds number outside supported positive correlation region")

    skin_drag = q * (2 * inputs.wing_area_m2) * cf  # two flat-plate wing surfaces
    induced_drag = q * inputs.wing_area_m2 * cl ** 2 / (pi * inputs.oswald_efficiency * inputs.aspect_ratio)
    other_drag = q * inputs.wing_area_m2 * inputs.other_parasite_cd0
    drag = skin_drag + induced_drag + other_drag

    # Uniform distributed semi-span *lift*, ignoring spanwise inertial-relief effects.
    # Structural maneuver load factor is intentionally separate from 1-g aerodynamic cruise.
    distributed_load = inputs.load_factor * weight / span  # N/m on each half-wing
    root_moment = distributed_load * half_span ** 2 / 2
    stress = root_moment * (height / 2) / inertia
    deflection = distributed_load * half_span ** 4 / (8 * material.youngs_modulus_gpa * 1e9 * inertia)
    sf = material.yield_strength_mpa * 1e6 / stress
    deflection_ratio = deflection / half_span

    conductivity_air = mu * CP_AIR / PRANDTL
    h = nusselt * conductivity_air / chord
    recovery_factor = sqrt(PRANDTL) if reynolds <= 5e5 else PRANDTL ** (1 / 3)
    adiabatic_wall_k = temp_k + recovery_factor * inputs.speed_m_s ** 2 / (2 * CP_AIR)
    interior_k = inputs.inner_skin_temperature_c + 273.15
    heat_flux = (adiabatic_wall_k - interior_k) / (1 / h + inputs.skin_thickness_m / material.conductivity_w_mk)
    outer_skin_k = interior_k + heat_flux * inputs.skin_thickness_m / material.conductivity_w_mk
    heat_rate = heat_flux * inputs.wing_area_m2  # one exposed equivalent skin area

    battery_kwh = drag * inputs.route_distance_km * 1000 / 3.6e6 / (inputs.propeller_efficiency * inputs.motor_efficiency)
    op_co2 = battery_kwh * inputs.grid_kgco2e_per_kwh
    embodied = spar_mass * material.embodied_kgco2e_per_kg
    allocated = embodied / inputs.service_missions
    mission_co2 = op_co2 + allocated

    struct_ok = sf >= inputs.required_yield_safety_factor and deflection_ratio <= inputs.max_tip_deflection_ratio
    lift_ok = cl <= inputs.cl_max
    low_mach = mach <= 0.3
    warnings: list[str] = []
    if not low_mach:
        warnings.append("Mach > 0.3: incompressible flat-plate/induced-drag screening assumptions become unreliable")
    if not lift_ok:
        warnings.append("Required CL exceeds the user-provided CLmax: 1-g level flight may be infeasible")
    if sf < inputs.required_yield_safety_factor:
        warnings.append("Beam yield safety factor is below the selected minimum")
    if deflection_ratio > inputs.max_tip_deflection_ratio:
        warnings.append("Estimated beam tip deflection exceeds the selected limit")
    if reynolds < 1e4:
        warnings.append("Very low chord Reynolds number: standard plate correlations may be inaccurate")
    if abs(heat_flux) > 20000:
        warnings.append("High estimated skin heat flux: validate the 1-D thermal approximation")
    warnings.append("Educational screening only; not CFD, FEA, fatigue, flutter, certification, or life-cycle assessment")

    return Result(
        material=material.name, spar_height_m=inputs.spar_height_m, altitude_m=inputs.altitude_m, speed_m_s=inputs.speed_m_s,
        air_temperature_c=temp_k - 273.15, air_density_kg_m3=rho,
        dynamic_pressure_pa=q, mach=mach, reynolds_chord=reynolds, flow_regime=regime,
        wingspan_m=span, mean_chord_m=chord, spar_mass_kg=spar_mass,
        total_mass_kg=total_mass, lift_coefficient=cl, stall_speed_m_s=stall_speed,
        skin_drag_n=skin_drag, induced_drag_n=induced_drag, other_drag_n=other_drag,
        total_drag_n=drag, lift_to_drag=weight / drag, root_moment_nm=root_moment,
        bending_stress_mpa=stress / 1e6, yield_safety_factor=sf,
        tip_deflection_m=deflection, tip_deflection_ratio=deflection_ratio,
        convection_coefficient_w_m2k=h, thermal_flux_w_m2=heat_flux,
        thermal_power_w=heat_rate, outer_skin_temperature_c=outer_skin_k - 273.15,
        mission_electricity_kwh=battery_kwh, operational_kgco2e=op_co2,
        spar_embodied_kgco2e=embodied, allocated_embodied_kgco2e_per_mission=allocated,
        total_mission_kgco2e=mission_co2, structurally_feasible=struct_ok,
        lift_feasible=lift_ok, within_low_mach_envelope=low_mach,
        screening_pass=struct_ok and lift_ok and low_mach, warnings=tuple(warnings)
    )
