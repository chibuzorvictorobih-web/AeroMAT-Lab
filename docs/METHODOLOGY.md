# Technical Methodology and Model Scope

**Status:** Transparent low-order educational parametric model; no calibration to aircraft wind-tunnel, FE, CFD or flight-test data. Do not use its outputs to certify or manufacture flight hardware.

## 1 · Model schematic and dimensional consistency

A rectangular, untwisted wing has planform area `S [m²]` and aspect ratio `AR [-]`. Total wingspan `b = sqrt(AR × S) [m]`; corresponding mean chord `c = S/b [m]`. Two equal-length hollow rectangular wing spars are idealised as cantilever beams spanning the two half-wings (`b/2` each). Their combined mass is part of modelled aircraft weight.

The user supplies the mass of **everything except the two spars**. Mass due to batteries, propulsion, wing skins, other structure, controls, occupants and payload is implicitly included in this user-provided baseline mass. The separate thermal wing skin is *not* structurally modelled or weighed.

### Atmosphere

At geometric altitude `z` from 0 to 11,000 m, the tropospheric International Standard Atmosphere approximation is:

- `T = 288.15 − 0.0065 z` in K.
- `p = 101325 (T/288.15)^(g/(R × 0.0065))` in Pa.
- `rho = p/(RT)` in kg/m³, with `R = 287.05287 J/(kg K)` and `g = 9.80665 m/s²`.
- Dynamic viscosity `mu` uses Sutherland's formula referenced to 273.15 K.

This simplification neglects humidity, wind, actual weather, and geopotential/geometric-altitude subtleties.

### Flow and drag

`q = 0.5 rho V²` is dynamic pressure (Pa); `Re = rho V c / mu` uses the single equivalent chord; `M = V/sqrt(gamma R T)` with `gamma = 1.4`.

`W = (m_base + 2-spar_mass) g` is weight in newtons. For 1-g level flight, `L = W`, `CL_required = W/(qS)`.

For a finite-wing approximation, `C_Di = CL_required²/(pi AR e)`, `D_induced = q S C_Di`. The user enters `e` (Oswald efficiency). The implied wing loading and polar are **not** calculated from a chosen airfoil or aerofoil polar.

The model approximates both wing surfaces as flat plates with wetted area `2S`. For `Re <= 5e5`:

- Average laminar friction coefficient `Cf = 1.328/sqrt(Re)`.
- Average plate Nusselt number `Nu = 0.664 sqrt(Re) Pr^(1/3)`.

For `Re > 5e5`, the transition-corrected empirical averages are:

- `Cf = 0.074/Re^0.2 − 1742/Re`.
- `Nu = (0.037 Re^0.8 − 871) Pr^(1/3)`.

These idealized correlations assume a nominal transition region and constant property estimates. They do not account for roughness, pressure gradients, separated flow, laminar-flow-control wings, swept wings, curved wing surfaces or changes of local chord. The atmosphere model takes `Pr = 0.71`, `cp = 1005 J/(kg K)`.

`D_skin = q × 2S × Cf`. `D_other = qS CD0_other`; this last **must exclude the modelled wing skin friction**. `D_total = D_skin + D_induced + D_other`. The lift-to-drag ratio in the app is `W / D_total`. Airplane drag components beyond the user-entered `CD0_other` are not inferred.

`V_stall_approx = sqrt(2W/(rho S CLmax))` is a coarse value based solely on user-supplied `CLmax`, not a certified stall speed. Whenever `CL_required > CLmax`, the calculation is flagged.

**Envelope:** Since the equations do not capture wing compressibility, Mach above 0.3 is explicitly marked outside the screening envelope (the results still display as approximate diagnostics but the "pass" flag is false). At `Re < 10,000`, an additional caution is raised.

### Two hollow rectangular spars and loads

Let the spar outside width be `w`, outside height `h`, uniform wall thickness `t < min(w,h)/2`.

Cross-sectional area:

`A = w h − (w − 2t)(h − 2t)` in m².

Second moment of area about the horizontal centroidal bending axis:

`I = [w h³ − (w − 2t)(h − 2t)³]/12` in m⁴.

Combined two-spar mass is `m_spars = A × b × rho_material` in kg.

For a hypothetical aircraft structural maneuver load factor `n`, the *uniform* distributed lift load along **each** half-wing is `w_load = nW / b` in N/m. Root moment for each independent cantilever is `M_root = w_load × (b/2)² / 2` in N·m.

Extreme fiber stress `sigma = M_root × (h/2) / I` in Pa, and elastic tip deflection `delta = w_load × (b/2)^4 / (8 E I)` in m. Yield safety factor `SF = sigma_yield / sigma`. The screen passes the structural part if `SF >= minimum_user_SF` and `delta / (b/2) <= maximum_user_ratio`.

**Structural idealisations that matter:** A single uniform equivalent lift distribution is applied along each semi-span. Distributed self-weight/load inertial relief, aeroelastic load redistribution, connections, fuel load, bending about other axes, torsion, shear, wingbox skins, local/global buckling, fatigue, fracture, damage tolerance, plasticity, yield anisotropy, temperature-dependent properties and ultimate/load regulations are excluded. For a real aircraft, these may dominate the design. The selected `n` affects structure only; cruise aerodynamic `CL` remains 1-g.

### Heat transfer and energy exchange

The equivalent chord acts as plate length `c`. Thermal conductivity of ambient air is approximated by `k_air = mu cp/Pr`; `h_conv = Nu × k_air/c` in W/(m² K).

The freestream stagnation heating approximation uses `T_aw = T_air + r V²/(2cp)`, with recovery factor `r = sqrt(Pr)` for laminar and `r = Pr^(1/3)` for the turbulent correlation.

For a prescribed inside surface temperature `T_inside`, skin thickness `t_skin` and material conductivity `k_skin`, a 1-D convection + conduction network gives:

`heat_flux = (T_aw − T_inside) / (1/h_conv + t_skin/k_skin)` in W/m².

An equivalent one-sided surface of planform area `S` gives total `Q = heat_flux × S` in W. Estimated outer surface temperature is `T_outside = T_inside + heat_flux × t_skin/k_skin`. **Positive** Q is air-to-interior heat; negative is interior-to-air heat.

This is steady-state, uniform property, prescribed interior boundary condition. It omits transient heating, radiation, solar insolation, wing fuel, actual three-dimensional flow, internal convective resistances, substrate layers and any skin structural mass contribution. Do **not** confuse total signed heat transfer power with the electric-cruise propulsion energy model; no thermal-management electricity penalty is estimated.

### Cruise electricity & environmental proxy

Steady level force balance assumes thrust required is `D_total`. Mechanical thrust work over cruise distance `d` metres is `D d` Joules. Idealised electric-drive energy:

`E_kWh = D_total × (d_km × 1000) / (3.6e6 × eta_prop × eta_motor)`.

It is a **cruise-only electric-aircraft scenario**; it assumes constant velocity, density and drag during the flight, and omits taxi, takeoff, climb/descent, reserves, charging losses, battery weight/aging and changing operating points.

Electric operations proxy: `C_electric = E_kWh × grid_kgco2e_per_kwh`.

Two-spar manufacture proxy: `C_spar = m_spars × material_kgco2e_per_kg`.

Amortized spar contribution per mission: `C_spar / number_of_lifetime_missions`.

Reported `mission_kgco2e = C_electric + (C_spar / missions)`.

**WARNING**: Carbon factors provided in material presets (Al 8, Ti 20, steel 2.4 kg CO2e per kg) are fictional/illustrative comparison settings, **not verified regional material LCA data or EPDs**. Users must replace them with sourced cradle-to-gate embodied figures before research-grade statements. Applying the same nominal value to both aluminium tempers is a simplification. Grid intensity is also user-defined. This metric is neither a full greenhouse-gas inventory nor an actual aircraft life-cycle footprint.

## 2 · Coupling and optimization

Changing material density changes the mass of the two spars. As `W` changes, `CL`, induced drag, electricity, operations carbon, and allocated manufacturing emissions change. Material modulus also affects beam deflection, yield strength affects yield safety, and material conductivity affects thermal heat flux.

The **design explorer** runs a deterministic, bounded grid over outer spar height at fixed outside width and wall thickness. Each candidate is re-evaluated from first principles; infeasible candidates are removed using the constraints. The top feasible candidate minimizes the selected computed objective: spar mass, mission electricity or the limited carbon proxy. A height-only grid search is **not** global aerodynamic/structural optimization, and other design variables and nonlinear constraints are fixed.

The model does not consider the existence of real commercially available spar profiles of the supplied geometry. It is a conceptual sensitivity study only.

## 3 · Verification and reproducibility

The `tests/` suite checks independent closed-form mass and induced-drag formulas, 1-g lift, atmospheric reference values, scale laws (load factor doubles stress/deflection; Young's modulus inversely scales deflection; doubling distance doubles cruise energy), thermal flux sign, feasibility warnings, constrained sweep outcomes and invalid-input handling.

The sample CSV and input defaults are included in the repo. Results can be exported as JSON or CSV. No randomness is used. `docs/TEST_REPORT.md` records which tests were actually run in the preparation environment.

**Tests do not equal validation.** Before an engineering research paper or real design exercise, benchmark aerodynamic predictions against suitable measured polars, structural outcomes against FEA/beam reference problems, thermal estimates against validated convection data, and environment factors against verified EPD/LCA datasets.

## 4 · Sources and follow-on ideas

- [NASA Glenn: Drag Equation](https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/drag-equation/)
- [NASA Glenn: Induced Drag Coefficient](https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/induced-drag-coefficient/)
- [NASA Glenn: Lift to Drag](https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/lift-to-drag-ratio/)

Reasonable next research iterations: measured polar interpolation, speed–range optimizations, fuselage drag buildup, temperature-dependent materials, a 2-D Euler–Bernoulli beam FEA benchmark, composite laminate theory with anisotropy, verified aircraft component production inventory, full mission phases and a documented experimental validation plan.
