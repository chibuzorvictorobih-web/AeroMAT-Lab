# Verification Report — AeroMAT Lab

**Preparation date:** 14 October 2026  
**Scope:** Tests of the numerical engine, CSV conversion and parameter sweep. These are *software-level* equation and regression tests, not aircraft-specific experimental validation.

## Continuous integration and app smoke verification

The repository includes `.github/workflows/ci.yml`, triggered by pushes to `main`, pull requests, and manual dispatch. The workflow installs `requirements.txt`, checks Python compilation, and executes `pytest` on Python 3.11 and 3.13.

The `tests/test_app.py` Streamlit AppTest suite adds three UI smoke checks:

1. The application starts without Streamlit exceptions and renders all five interface tabs.
2. Changing airspeed updates the displayed Mach number.
3. Switching materials updates the displayed spar mass.

**Verification status (14 October 2026):** GitHub Actions completed successfully on commit `c6cbd84` on both Python 3.11 and 3.13. The workflow job log reports **39 passed tests**, consisting of 36 existing numerical/analysis checks and three new Streamlit UI smoke tests. This confirms execution on hosted CI for that commit; newer changes must be verified by their own workflow runs. GitHub Actions checks Streamlit behaviour programmatically, not pixel-level mobile layout. Mobile-browser appearance and CSV uploads still require separate manual checks.

**How to verify:** Visit the repository's **Actions → Software quality checks** page. A green result for both Python versions is evidence that CI passed on that commit. If no workflow appears, inspect repository Actions settings and refresh; do not presume success. Upload `data/example_scenarios.csv` to the deployed Batch CSV tab and confirm that successful scenario rows and CSV export work.

## Original preparation checks

- `python -m pytest -q`: **36 tests passed** in the preparation environment.
- `python -m py_compile app.py`: Streamlit application syntax compiled without errors.
- Default input scenario: four preset materials calculate successfully; no out-of-envelope conditions at Mach ≈ 0.194.
- Design explorer: finds a candidate meeting the supplied nominal structural and low-Mach constraints.
- `python scripts/generate_demo.py`: generated four example scenario result rows, all with screening-pass flags (this is **not** a safety approval).

### Coverage by theme

- Standard-atmosphere reference conditions and density change with altitude.
- Two-spar volume/mass and finite-wing induced-drag formula.
- Reconstruction of total drag from its components.
- Maneuver load scaling for beam stress and tip deflection.
- Elastic modulus sensitivity and spar height/mass trade-off.
- Total mass feedback into induced drag, electric mission energy and emissions.
- Heat-flow sign and material conductivity influence.
- Out-of-range Mach, CLmax violations, geometry and property validation.
- Reproducible height sweeps, feasible-objective filtering and CSV field parsing.

## Runtime/browser verification

The application passed Python syntax checks in the preparation environment. It has also been launched successfully in the project owner's local Streamlit browser, where the dashboard and numerical result cards rendered. Full interactive browser smoke tests (editing input values, every tab and CSV processing) have **not yet been independently confirmed**. Follow `docs/DEPLOYMENT.md` to complete those checks before publicly sharing the app. A GitHub Actions workflow is included; check the latest run result rather than assuming the workflow has executed.

## Engineering validation still required

No CFD, experimental aerofoil, wind tunnel, FEA, physical wing spar tests or verified LCA/EPD benchmarks are included. Even if the code tests pass, true engineering validation would need appropriate physical measurements, external models, calibrated coefficients and independent peer review.
