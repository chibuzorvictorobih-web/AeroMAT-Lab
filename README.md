# AeroMAT Lab ✈️
### Open-source, interactive aerospace wing design and sustainability calculator

**Creator:** Chibuzor Victor Obih  
**Scope:** Independent preliminary aerospace engineering calculator  
**Stack:** Python · Streamlit · pandas · pytest · GitHub Actions

**Try the online calculator:** [Launch AeroMAT Lab](https://aeromat-lab.streamlit.app/)

> **Educational preliminary tool only.** AeroMAT Lab is a transparent, low-order engineering *screening* calculator. It is not CAD, CFD, FEA, validated aircraft design software, a flight-safety system, or a certified life-cycle assessment. Results must not be used to construct or approve aircraft parts.

## What it does

Users enter their own flight conditions, geometric properties, assumed material properties, thermal boundary conditions, propulsion efficiencies, and emissions factors. The web interface instantly recomputes **six coupled results**:

1. **Atmosphere and aerodynamics:** ISA troposphere, density, Reynolds number, Mach number, required lift coefficient, skin-friction drag, induced drag, other parasite drag, L/D and approximate stall speed.
2. **Wing spar structural response:** mass of two idealized hollow rectangular cantilever spars, root moment, bending stress, yield safety factor, tip deflection, and screening constraints under a maneuver load factor.
3. **Heat transfer:** flat-plate convection coefficient, signed thermal flux, one-dimensional skin conduction, and estimated outside skin temperature.
4. **Electric-cruise energy:** powertrain-efficiency-adjusted electricity for a user-specified cruise distance.
5. **Sustainability trade-offs:** configurable operational electricity emissions plus illustrative, lifetime-apportioned two-spar embodied carbon.
6. **Multi-scenario decisions:** side-by-side alloy comparisons, parameter-sweep spar height search and up to 500 rows of batch CSV scenarios.

A key feature is **cross-domain coupling**: selecting a denser material increases two-spar mass, raising total modelled aircraft mass, required cruise lift, induced drag, electric-cruise energy, and the carbon proxy. Larger spar sections generally reduce stress and deflection but increase mass. The tool makes such trade-offs visible rather than independently reporting unrelated calculator outputs.

## Interface

| Tab | Use |
|---|---|
| Design dashboard | Edit engineering inputs and see results, drag decomposition, warnings and exportable outputs |
| Compare materials | Compare four representative metal alloy presets (or a custom selected material) |
| Spar design explorer | Scan an adjustable range of hollow spar heights and filter by user-selected screening limits |
| Batch CSV | Analyse up to 500 cases at once; download result and error reports |
| Methods & scope | Read equations, assumptions, and model boundaries |

All editable design inputs appear in the Streamlit sidebar. The material properties and embodied factor are editable. CSV input permits different values for all numeric fields declared in `aeromat/model.py` and an optional `material` preset name.

### Five project-development tasks — completed

| Task | Deliverable | Status |
|---|---|---|
| 1. Define the engineering problem | Coupled system boundaries, modelling assumptions and input/output definitions | Complete |
| 2. Build the physics engine | Atmosphere, drag, beam, thermal, energy and carbon modules | Complete |
| 3. Create the interactive app | Responsive Streamlit dashboard, custom material, comparison and CSV exports | Complete in code; hosting remains user-controlled |
| 4. Add design exploration and verification | Parametric sweep, feasibility filtering, automated regression tests, CI workflow | Complete |
| 5. Package and prepare public deployment | README, example CSV, methodology, deployment instructions, repository archive | Complete; GitHub upload and Streamlit deployment require your account |

## Install and run on Windows

1. Download/unzip the project archive and open the resulting `aeromat-lab` folder in VS Code.
2. Open **Terminal → New Terminal** in VS Code.
3. If Python 3.11 (or 3.10+) is installed, run:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m pytest -q
.venv\Scripts\python.exe -m streamlit run app.py
```

4. Your default browser should open a Streamlit URL, typically `http://localhost:8501`.
5. Change values in the left sidebar; open the **Compare materials**, **Spar design explorer**, and **Batch CSV** tabs. Test the bundled `data/example_scenarios.csv` in the batch tab.

An optional no-Streamlit check is `python scripts/generate_demo.py`, which regenerates `data/example_results.csv`.

Run these commands individually. On Windows, use the `python` command if `py` is unavailable. Installation requires internet access for the Python packages. No paid API, external account, or API key is required to use the calculator locally.

## Publish it

Follow **[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)** for GitHub and Streamlit Community Cloud. In brief, create an empty GitHub repository, commit the extracted project folder contents, push to `main`, then configure a Streamlit Cloud app with entrypoint `app.py`.

## Numerical credibility and limits

The aim is to **demonstrate physical reasoning**, not to claim that simplified equations are verified engineering design. Most importantly:

- The aircraft has an assumed rectangular wing; two identical hollow rectangular spars span the wings. No skin/fuel/battery/fastener mass feedback is modelled except the two spars.
- Cruise is steady and level at 1-g. Structural loads use a separate user-supplied maneuver factor, idealized as uniform vertical distributed half-wing lift.
- The drag estimate combines flat-plate wing skin friction, a finite-wing induced-drag approximation, and a user-entered *other* parasite drag coefficient. **Do not double-count friction** in the latter.
- The thermal calculation is a 1-D boundary-condition model, not transient or conjugate CFD; the wing skin is treated as the selected material but not separately weighed.
- Mach above 0.3 is flagged outside the low-Mach screening envelope. Exceeding supplied CLmax, minimum safety factor or maximum deflection similarly causes a failure flag.
- Mechanical property presets are rounded illustrative figures; values depend on alloy, temper, direction, processing, temperature and design allowables.
- The carbon factors are **explicitly illustrative placeholders**, not authoritative environmental declarations. Mission CO₂e is an incomplete comparison proxy, **not** a full flight footprint.
- No fatigue, fracture, local buckling, torsion, flutter, load paths, damage tolerance, manufacturing constraints, cooling design, climb or takeoff performance are validated.

See **[docs/METHODOLOGY.md](docs/METHODOLOGY.md)** for derivations, assumptions, checks, interpretation and extension ideas.

## Check the tests

```powershell
.venv\Scripts\python.exe -m pytest -q
```

The project contains independent regression, scaling, input-validation and batch/optimizer tests. The GitHub Actions workflow runs numerical tests and Streamlit AppTest smoke tests for Python 3.11 and 3.13 on pushes and pull requests, when Actions is enabled. Confirm the latest result in the Actions tab; merely having a workflow file does not prove a successful run. The tests check the implementation's consistency against simplified model equations; they are **not experimental validation**.

## Repo contents

```text
aeromat-lab/
├── app.py                      # Streamlit UI
├── aeromat/
│   ├── __init__.py
│   ├── model.py                # Coupled numerical engine, inputs, presets
│   └── analysis.py             # Comparisons, batch parsing and optimization
├── tests/                     # Numerical regression and Streamlit UI smoke tests
├── data/                     # Ready-to-upload scenario CSV + sample results
├── scripts/generate_demo.py  # Offline example-result generator
├── docs/
│   ├── METHODOLOGY.md
│   ├── ENGINEERING_SCOPE.md
│   ├── DEVELOPMENT_TASKS.md
│   ├── DEPLOYMENT.md
│   └── TEST_REPORT.md
├── .github/workflows/ci.yml  # Continuous integration
├── .streamlit/config.toml
├── requirements.txt
├── .gitignore
└── LICENSE
```

## Engineering scope

AeroMAT Lab is a standalone, open-source educational project. It connects aerodynamic, structural, materials and thermal calculations with cruise energy and illustrative emissions estimates, so users can explore how design choices affect multiple engineering outcomes. It is **not affiliated with or endorsed by any educational institution or external organisation**. See **[docs/ENGINEERING_SCOPE.md](docs/ENGINEERING_SCOPE.md)** for the modules, use cases and limits.

## References for the physics *concepts*

- [NASA Glenn Research Center: Drag Equation](https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/drag-equation/)
- [NASA Glenn Research Center: Induced Drag Coefficient](https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/induced-drag-coefficient/)
- [NASA Glenn Research Center: Lift-to-Drag Ratio](https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/lift-to-drag-ratio/)

NASA references explain the aerodynamic physics; they do **not** independently validate this specific software, the preset material values, or the simplified thermal and structural assumptions.

## License

MIT (see `LICENSE`). Software is provided as-is without fitness or safety certification.
