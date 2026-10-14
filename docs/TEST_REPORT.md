# Verification Report — AeroMAT Lab

**Preparation date:** 14 October 2026  
**Scope:** Tests of the numerical engine, CSV conversion and parameter sweep. These are *software-level* equation and regression tests, not aircraft-specific experimental validation.

## Continuous integration and app smoke verification

The repository includes `.github/workflows/ci.yml`, triggered by pushes to `main`, pull requests, and manual dispatch. The workflow installs `requirements.txt`, checks Python compilation, and executes `pytest` on Python 3.11 and 3.13.

The `tests/test_app.py` Streamlit AppTest suite adds three UI smoke checks:

1. The application starts without Streamlit exceptions and renders all five interface tabs.
2. Changing airspeed updates the displayed Mach number.
3. Switching materials updates the displayed spar mass.

**Clean-repository baseline (14 October 2026):** After publishing a new history with one privacy-protected root commit (`5623e4ee1e2a42979847c98ecba44ab6502f1dd6`), GitHub Actions completed [run 38634871313](https://github.com/chibuzorvictorobih-web/AeroMAT-Lab/actions/runs/38634871313) successfully on Python 3.11 and Python 3.13. The recorded job logs report **39 passed** on each Python version: 36 numerical/analysis checks and three Streamlit AppTest smoke tests. This verifies that repository version, not subsequent untested edits. Automated AppTest checks do not independently establish responsive/mobile appearance or CSV-file-upload behaviour.

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

The project owner confirmed on 14 October 2026 that the public Streamlit website opens and runs following the clean repository release. The CI smoke tests exercise application startup and reactive inputs but do not render a real mobile browser. Manual mobile-layout and batch-CSV upload checks remain separate acceptance tasks. See `docs/DEPLOYMENT.md` for a concise verification checklist.

## Engineering validation still required

No CFD, experimental aerofoil, wind tunnel, FEA, physical wing spar tests or verified LCA/EPD benchmarks are included. Even if the code tests pass, true engineering validation would need appropriate physical measurements, external models, calibrated coefficients and independent peer review.
