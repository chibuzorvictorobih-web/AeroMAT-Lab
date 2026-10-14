"""AeroMAT Lab — interactive low-order aircraft engineering screening tool.

Run: streamlit run app.py
"""

from __future__ import annotations

import json
from dataclasses import asdict, replace
from html import escape
from pathlib import Path

import pandas as pd
import streamlit as st

from aeromat.analysis import best_feasible, compare_materials, from_record, height_sweep
from aeromat.model import Inputs, MATERIALS, Material, calculate

st.set_page_config(page_title="AeroMAT Lab | Aerospace Engineering Calculator", page_icon="✈️", layout="wide")

st.markdown("""
<style>
.block-container { padding-top: 1.2rem; max-width: 1300px; }

/* Metric cards reflow according to the CONTENT width, not the screen width.
   This also works when a phone displays the app in desktop-site mode. */
.aeromat-metrics {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(min(100%, 220px), 1fr));
    gap: 0.8rem;
    margin: 0.6rem 0 1.2rem;
}
.aeromat-metric {
    min-width: 0;
    padding: 1rem;
    border: 1px solid rgba(125, 175, 207, 0.35);
    border-radius: 12px;
    background: rgba(85, 150, 197, 0.12);
}
.aeromat-metric-label {
    font-size: 0.87rem;
    font-weight: 500;
    opacity: 0.9;
    line-height: 1.4;
    margin-bottom: 0.45rem;
}
.aeromat-metric-value {
    font-size: clamp(1.1rem, 2vw, 1.7rem);
    font-weight: 700;
    line-height: 1.25;
    font-variant-numeric: tabular-nums;
    overflow-wrap: anywhere;
}

/* Let Streamlit columns wrap inside a narrow content panel. These selectors
   are progressive enhancements; the responsive metric grid works without them. */
div[data-testid="stHorizontalBlock"] { flex-wrap: wrap !important; }
div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"],
div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
    min-width: min(100%, 290px) !important;
    flex: 1 1 290px !important;
}

div[data-testid="stMetric"] {
    background: rgba(85, 150, 197, 0.12);
    padding: 1rem;
    border: 1px solid rgba(125, 175, 207, 0.35);
    border-radius: 12px;
}
div[data-testid="stMetricValue"] { overflow-wrap: anywhere; }
div[data-testid="stTabs"] button[role="tab"] { white-space: nowrap; }
@media (max-width: 700px) {
    .block-container { padding: 0.9rem 0.85rem 2rem; }
    .aeromat-metric { padding: 0.85rem; }
    .aeromat-metric-value { font-size: 1.22rem; }
}
</style>
""", unsafe_allow_html=True)


def show_metric_cards(items: list[tuple[str, str]]) -> None:
    """Render value cards that never truncate when the main column is narrow."""
    cards = "".join(
        '<div class="aeromat-metric">'
        f'<div class="aeromat-metric-label">{escape(str(label))}</div>'
        f'<div class="aeromat-metric-value">{escape(str(value))}</div>'
        '</div>'
        for label, value in items
    )
    st.markdown(f'<div class="aeromat-metrics">{cards}</div>', unsafe_allow_html=True)


st.title("✈️ AeroMAT Lab")
st.caption("Aerospace materials × aerodynamics × heat transfer × structural mechanics × sustainability")
st.info("Educational preliminary screening, **not** a flight-safety, structural certification, CFD/FEA, or verified life-cycle assessment tool. Best suited to low-Mach illustrative aircraft scenarios.", icon="ℹ️")

with st.sidebar:
    st.header("Set your design")
    st.caption("All entries are editable. Every change recalculates the physics models. On phones, collapse this panel after editing to give the results more room.")
    selected_material = st.selectbox("Spar and modelled skin material", list(MATERIALS) + ["Custom material"])

    if selected_material == "Custom material":
        with st.expander("Custom material properties", expanded=True):
            custom_name = st.text_input("Material name", value="User-defined alloy")
            custom_density = st.number_input("Density [kg/m³]", min_value=1.0, value=2800.0, step=50.0)
            custom_e = st.number_input("Young's modulus [GPa]", min_value=0.01, value=73.0, step=1.0)
            custom_y = st.number_input("Yield strength [MPa]", min_value=0.1, value=350.0, step=10.0)
            custom_k = st.number_input("Thermal conductivity [W/m·K]", min_value=0.001, value=120.0, step=5.0)
            custom_carbon = st.number_input("Illustrative embodied factor [kgCO₂e/kg]", min_value=0.0, value=8.0, step=0.5)
        material = Material(custom_name, custom_density, custom_e, custom_y, custom_k, custom_carbon)
    else:
        reference = MATERIALS[selected_material]
        with st.expander("Selected material values / carbon assumptions"):
            st.caption("Properties are representative, not certified design allowables. Carbon factor is an illustrative placeholder.")
            density = st.number_input("Density [kg/m³]", min_value=1.0, value=float(reference.density_kg_m3), key=f"rho_{selected_material}")
            youngs = st.number_input("Young's modulus [GPa]", min_value=0.01, value=float(reference.youngs_modulus_gpa), key=f"E_{selected_material}")
            yield_strength = st.number_input("Yield strength [MPa]", min_value=0.1, value=float(reference.yield_strength_mpa), key=f"yield_{selected_material}")
            k = st.number_input("Thermal conductivity [W/m·K]", min_value=0.001, value=float(reference.conductivity_w_mk), key=f"k_{selected_material}")
            carbon = st.number_input("Illustrative embodied factor [kgCO₂e/kg]", min_value=0.0, value=float(reference.embodied_kgco2e_per_kg), key=f"co2_{selected_material}")
        material = Material(reference.name, density, youngs, yield_strength, k, carbon)

    with st.expander("1 · Flight & wing geometry", expanded=True):
        altitude = st.number_input("Altitude [m] (ISA, 0–11,000)", min_value=0.0, max_value=11000.0, value=1500.0, step=100.0)
        speed = st.number_input("Airspeed [m/s]", min_value=1.0, max_value=350.0, value=65.0, step=5.0)
        wing_area = st.number_input("Wing planform area [m²]", min_value=0.01, value=16.0, step=1.0)
        aspect = st.number_input("Wing aspect ratio", min_value=0.1, value=8.0, step=0.5)
        body_mass = st.number_input("Aircraft mass EXCLUDING two modelled spars [kg]", min_value=0.1, value=900.0, step=50.0)
        other_cd = st.number_input("Other parasite CD₀ (excludes modelled wing skin friction)", min_value=0.0, value=0.018, step=0.002, format="%.3f")
        oswald = st.number_input("Oswald efficiency", min_value=0.01, max_value=1.0, value=0.80, step=0.05)
        clmax = st.number_input("Assumed maximum lift coefficient CLmax", min_value=0.01, value=1.50, step=0.1)

    with st.expander("2 · Structural beam", expanded=True):
        width = st.number_input("Spar box width [m]", min_value=0.001, value=0.12, step=0.01)
        height = st.number_input("Spar box height [m]", min_value=0.001, value=0.24, step=0.01)
        wall = st.number_input("Uniform box wall thickness [m]", min_value=0.0001, value=0.006, step=0.001, format="%.4f")
        load_factor = st.number_input("Structural maneuver load factor [g]", min_value=0.1, value=2.5, step=0.5)
        min_sf = st.number_input("Required yield safety factor", min_value=0.1, value=1.5, step=0.1)
        max_deflection = st.number_input("Maximum semi-span tip deflection [%]", min_value=0.1, max_value=100.0, value=8.0, step=1.0)

    with st.expander("3 · Thermal boundary conditions"):
        skin_thickness = st.number_input("Modelled wing skin thickness [m]", min_value=0.0001, value=0.002, step=0.0005, format="%.4f")
        inside_t = st.number_input("Internal skin-side temperature [°C]", value=20.0, step=5.0)

    with st.expander("4 · Electric propulsion & carbon"):
        prop_eff = st.number_input("Propeller efficiency", min_value=0.01, max_value=1.0, value=0.82, step=0.02)
        motor_eff = st.number_input("Motor / drivetrain efficiency", min_value=0.01, max_value=1.0, value=0.93, step=0.02)
        route = st.number_input("Cruise distance [km]", min_value=0.1, value=100.0, step=20.0)
        grid = st.number_input("Electricity carbon factor [kgCO₂e/kWh]", min_value=0.0, value=0.35, step=0.05)
        service = st.number_input("Assumed lifetime cruise missions", min_value=1.0, value=10000.0, step=1000.0)

params = Inputs(
    altitude_m=altitude, speed_m_s=speed, wing_area_m2=wing_area,
    aspect_ratio=aspect, aircraft_mass_excl_spars_kg=body_mass,
    load_factor=load_factor, spar_width_m=width, spar_height_m=height,
    spar_wall_thickness_m=wall, skin_thickness_m=skin_thickness,
    inner_skin_temperature_c=inside_t, other_parasite_cd0=other_cd,
    oswald_efficiency=oswald, propeller_efficiency=prop_eff,
    motor_efficiency=motor_eff, route_distance_km=route,
    grid_kgco2e_per_kwh=grid, service_missions=service,
    cl_max=clmax, required_yield_safety_factor=min_sf,
    max_tip_deflection_ratio=max_deflection / 100,
)

try:
    result = calculate(params, material)
except ValueError as exc:
    st.error(f"Invalid inputs: {exc}")
    st.stop()

tabs = st.tabs(["📊 Design dashboard", "🧱 Compare materials", "🔎 Spar design explorer", "📥 Batch CSV", "📚 Methods & scope"])

with tabs[0]:
    st.subheader("Your aircraft design at a glance")
    if result.screening_pass:
        st.success("**Screening status: PASS.** The selected preliminary checks pass. This is not an airworthiness or safety approval.")
    else:
        st.warning("**Screening status: REVIEW REQUIRED.** At least one preliminary check did not pass.")

    show_metric_cards([
        ("Cruise drag", f"{result.total_drag_n:,.1f} N"),
        ("Two-spar mass", f"{result.spar_mass_kg:,.1f} kg"),
        ("Mission electricity", f"{result.mission_electricity_kwh:,.1f} kWh"),
        ("Yield safety factor", f"{result.yield_safety_factor:.2f}"),
        ("Wing tip deflection", f"{result.tip_deflection_m:.3f} m"),
        ("Mach", f"{result.mach:.3f}"),
        ("Mission CO₂e (proxy)", f"{result.total_mission_kgco2e:.2f} kg"),
    ])

    for warning in result.warnings:
        if warning.startswith("Educational"):
            continue
        st.warning(warning)

    col_left, col_right = st.columns(2)
    with col_left:
        st.markdown("#### Aerodynamics and fluid mechanics")
        aero = {
            "Wing skin friction": result.skin_drag_n,
            "Finite-wing induced drag": result.induced_drag_n,
            "Other parasite drag": result.other_drag_n,
        }
        st.bar_chart(pd.DataFrame({"Drag [N]": aero}), horizontal=True)
        st.write(f"**Density:** {result.air_density_kg_m3:.3f} kg/m³ · **Reynolds (chord):** {result.reynolds_chord:,.0f} · **CL:** {result.lift_coefficient:.3f} · **L/D:** {result.lift_to_drag:.1f}")
        st.caption(f"Flow model: {result.flow_regime}. Approximate stall speed: {result.stall_speed_m_s:.1f} m/s (CLmax supplied by user).")
    with col_right:
        st.markdown("#### Thermal & materials")
        show_metric_cards([
            ("Convection coefficient", f"{result.convection_coefficient_w_m2k:.1f} W/m²K"),
            ("Heat transferred, signed", f"{result.thermal_power_w:,.1f} W"),
        ])
        st.write(f"**Outer skin:** {result.outer_skin_temperature_c:.2f} °C · **Heat flux:** {result.thermal_flux_w_m2:.1f} W/m² · **Root bending stress:** {result.bending_stress_mpa:.1f} MPa")
        st.caption("Positive heat flow = from surrounding air into the prescribed interior temperature boundary; negative = outward.")

    st.markdown("#### Mission sustainability proxy")
    carbon = pd.DataFrame({"kg CO₂e per mission": {
        "Electricity operations": result.operational_kgco2e,
        "Amortized spar production": result.allocated_embodied_kgco2e_per_mission,
    }})
    st.bar_chart(carbon, horizontal=True)
    st.caption("Electric aircraft cruise only. No battery sizing, takeoff, climb, infrastructure, end-of-life, non-CO₂ aviation effects, or certified life-cycle factors are included.")

    col1, col2 = st.columns(2)
    with col1:
        st.download_button("⬇️ Download current result (JSON)", data=json.dumps({"model_inputs": asdict(params), "material": asdict(material), "results": result.flat()}, indent=2), file_name="aeromat_design_report.json", mime="application/json", use_container_width=True)
    with col2:
        st.download_button("⬇️ Download current result (CSV)", data=pd.DataFrame([result.flat()]).to_csv(index=False), file_name="aeromat_design_report.csv", mime="text/csv", use_container_width=True)

with tabs[1]:
    st.subheader("Compare aerospace engineering alloys")
    st.caption("Same prescribed geometry and flight conditions. Spar mass changes aircraft mass and required lift, which changes induced drag and mission energy. The selected material's edits apply to its row.")
    all_materials = {**MATERIALS, material.name: material}
    options = st.multiselect("Materials to compare", list(all_materials), default=list(all_materials))
    if not options:
        st.info("Select at least one alloy to see a comparison.")
    else:
        comparisons = compare_materials(params, [all_materials[x] for x in options])
        frame = pd.DataFrame([{
            "Material": r.material,
            "Spar mass (kg)": round(r.spar_mass_kg, 2),
            "Yield SF": round(r.yield_safety_factor, 2),
            "Tip deflection (m)": round(r.tip_deflection_m, 3),
            "Drag (N)": round(r.total_drag_n, 1),
            "Electricity (kWh)": round(r.mission_electricity_kwh, 2),
            "Mission CO₂e (kg)": round(r.total_mission_kgco2e, 2),
            "Screening pass": r.screening_pass,
        } for r in comparisons]).set_index("Material")
        st.caption("On smaller screens, swipe horizontally within the table to see the remaining columns.")
        st.dataframe(frame, use_container_width=True)
        chart_frame = frame.rename(index={
            "Aluminium 2024-T3": "Al 2024-T3",
            "Aluminium 7075-T6": "Al 7075-T6",
            "Titanium Ti-6Al-4V": "Ti-6Al-4V",
            "Steel 4130": "Steel 4130",
        })
        st.markdown("#### Spar mass by material")
        st.bar_chart(chart_frame[["Spar mass (kg)"]], horizontal=True, height=285)
        st.markdown("#### Mission carbon proxy by material")
        st.bar_chart(chart_frame[["Mission CO₂e (kg)"]], horizontal=True, height=285)
        st.download_button("⬇️ Export material comparison CSV", data=frame.to_csv(), file_name="aeromat_material_comparison.csv", mime="text/csv")
        st.caption("The nominal mechanical properties and carbon factors are illustrative. For research, replace them with sourced alloy temper, product-form allowables and region-specific lifecycle data.")

with tabs[2]:
    st.subheader("Automated spar-height design explorer")
    st.write("Sweep rectangular hollow-spar heights across multiple materials; find the lightest feasible candidate under the chosen strength, deflection, CLmax and low-Mach conditions.")
    candidate_materials = {**MATERIALS, material.name: material}
    explore_materials = st.multiselect("Candidate materials", list(candidate_materials), default=list(candidate_materials), key="explore_materials")
    c1, c2 = st.columns(2)
    min_height = c1.number_input("Minimum spar height [m]", min_value=0.015, value=0.15, step=0.01)
    max_height = c2.number_input("Maximum spar height [m]", min_value=0.020, value=0.40, step=0.01)
    nsteps = st.slider("Resolution per material", min_value=5, max_value=101, value=41, step=4)
    objective_label = st.selectbox("Optimization objective", ["Minimum spar mass", "Minimum cruise electricity", "Minimum mission CO₂e proxy"])
    objective = {"Minimum spar mass": "spar_mass_kg", "Minimum cruise electricity": "mission_electricity_kwh", "Minimum mission CO₂e proxy": "total_mission_kgco2e"}[objective_label]
    if explore_materials:
        try:
            candidates = height_sweep(params, [candidate_materials[x] for x in explore_materials], min_height, max_height, nsteps)
            best = best_feasible(candidates, objective)
            if best is None:
                st.warning("No candidate passes every selected screening constraint. Try a larger height range, different load factor, or flight conditions; do not treat failure as a certified assessment.")
            else:
                st.success(f"Best feasible candidate for **{objective_label.lower()}**: **{best.material}** · spar height **{best.spar_height_m:.3f} m** · two-spar mass **{best.spar_mass_kg:.1f} kg** · yield safety factor **{best.yield_safety_factor:.2f}**.")
            table = pd.DataFrame([{
                "Material": x.material, "Height [m]": min_height + (max_height - min_height) * (i % nsteps) / (nsteps - 1),
                "Mass [kg]": x.spar_mass_kg, "Mission CO₂e [kg]": x.total_mission_kgco2e,
                "Energy [kWh]": x.mission_electricity_kwh, "Yield SF": x.yield_safety_factor,
                "Tip deflection [%]": 100 * x.tip_deflection_ratio, "Screening pass": x.screening_pass,
            } for i, x in enumerate(candidates)])
            st.scatter_chart(table, x="Mass [kg]", y="Mission CO₂e [kg]", color="Material", size=None)
            st.write(f"**Feasible candidates:** {int(table['Screening pass'].sum())} / {len(table)}")
            st.caption("On phones, swipe horizontally within the results table for additional columns.")
            st.dataframe(table.round(3), use_container_width=True, height=280)
            st.download_button("⬇️ Download parameter sweep", data=table.to_csv(index=False), file_name="aeromat_spar_height_sweep.csv", mime="text/csv")
        except ValueError as exc:
            st.error(f"Sweep inputs need adjustment: {exc}")
    else:
        st.info("Select at least one material to run the sweep.")

with tabs[3]:
    st.subheader("Batch engineering calculator")
    st.write("Upload up to **500 scenario rows** in CSV format. Any numeric input names from the template can be supplied; omitted/blank inputs inherit the current sidebar settings. Each row may include a `material` name from the preset alloys.")
    sample_path = Path(__file__).resolve().parent / "data" / "example_scenarios.csv"
    st.download_button("⬇️ Download example input CSV", data=sample_path.read_bytes(), file_name="aeromat_example_scenarios.csv", mime="text/csv")
    uploaded = st.file_uploader("Select a CSV scenario file", type=["csv"])
    if uploaded is not None:
        try:
            scenarios = pd.read_csv(uploaded)
        except Exception as exc:
            st.error(f"Could not parse CSV: {exc}")
        else:
            if len(scenarios) == 0 or len(scenarios) > 500:
                st.error("CSV must contain between 1 and 500 data rows.")
            else:
                outcomes = []
                for i, record in scenarios.iterrows():
                    try:
                        row = record.to_dict()
                        design = from_record(row, params)
                        chosen = row.get("material", selected_material)
                        if pd.isna(chosen) or str(chosen).strip() == "":
                            chosen = selected_material
                        if chosen == selected_material:
                            mat = material
                        elif chosen in MATERIALS:
                            mat = MATERIALS[chosen]
                        else:
                            raise ValueError(f"Unknown material {chosen!r}; use a preset name or current selected material")
                        r = calculate(design, mat)
                        outcomes.append({"scenario_row": i + 2, "error": "", **r.flat()})
                    except (ValueError, TypeError, OverflowError) as exc:
                        outcomes.append({"scenario_row": i + 2, "error": str(exc)})
                output = pd.DataFrame(outcomes)
                good = int((output["error"] == "").sum())
                st.write(f"**Processed:** {len(output)} scenarios · **Successful:** {good} · **Errors:** {len(output)-good}")
                st.caption("Swipe horizontally within the results table to read additional columns.")
                st.dataframe(output, use_container_width=True)
                st.download_button("⬇️ Download batch results CSV", data=output.to_csv(index=False), file_name="aeromat_batch_results.csv", mime="text/csv")

with tabs[4]:
    st.subheader("Model boundaries, equations and reproducibility")
    st.markdown("""
**Engineering approach:** AeroMAT Lab brings together simplified structural mechanics, materials selection, external aerodynamics, heat transfer and energy estimates in one reproducible parametric calculator. It does not claim to be a CFD solver, FEA package, or certified aircraft design authority.

**Aerodynamics:** ISA troposphere (0–11 km). `q = ½ρV²`, `CL = W/(qS)`, `Di = qS·CL²/(πeAR)`, `Dfriction = q·(2S)·Cf`, `Dother = qS·CD0_other`. Re uses an equivalent constant mean chord. Skin friction uses standard laminar and transition-corrected turbulent flat-plate correlations.

**Structures:** Two identical hollow rectangular cantilever spars along a rectangular planform's span. `b = √(AR·S)`. For a uniform half-wing idealized lift load `w = nW/b`, `Mroot = w(b/2)²/2`, `σ = M(h/2)/I`, `δtip = w(b/2)⁴/(8EI)`. Section area and moment of inertia account for internal cavity. Cruise drag assumes 1-g level flight, while structural load applies the selected maneuver factor.

**Heat transfer:** Flat-plate average Nusselt correlations with air `Pr=0.71`. Estimated adiabatic wall temperature includes a recovery-factor approximation. One-dimensional series resistance between outside convection and prescribed internal skin temperature gives heat flux. This module uses the selected material's conductivity, but does **not** add a separate skin mass to aircraft mass.

**Sustainability:** Steady, level electric-cruise electricity = `D·distance / (3.6e6·ηprop·ηmotor)` kWh. Electric operating carbon = grid factor × electricity. Embodied-carbon proxy = two-spar mass × editable factor, apportioned by the assumed number of lifetime missions. The other aircraft structure, production, maintenance and battery emissions are excluded.

**Important gaps:** Lift distributions and spar loading are idealised, beam analysis omits torsion, local buckling, joins, dynamic fatigue, fracture, aeroelasticity and material anisotropy. No empirical wing airfoil polars, climb/descent, stall margin beyond a user-provided CLmax, battery mass feedback, propeller maps or full LCA. Mach > 0.3 produces a reliability warning and fails the screening-pass indicator.

See `docs/METHODOLOGY.md` for assumptions, limitations, model transparency, and test references. Use the exported CSV/JSON to reproduce your run. No inputs are transmitted to a custom external service by this repository's Python code; Streamlit hosting has its own service/data policies.
""")
    st.markdown("**Aerodynamics references:** [NASA: Drag Equation](https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/drag-equation/) · [NASA: Induced Drag](https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/induced-drag-coefficient/) · [NASA: Lift-to-Drag Ratio](https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/lift-to-drag-ratio/)")
