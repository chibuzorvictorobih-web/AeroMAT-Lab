# Engineering Scope — AeroMAT Lab

AeroMAT Lab is an independent educational software project for exploring simplified aircraft wing design trade-offs. The application accepts user-configured engineering parameters and automatically recalculates coupled, preliminary estimates. Its intended audience includes learners, engineers exploring first-order models, and developers interested in reproducible scientific computing.

## Integrated engineering modules

| Module | Model contribution | Boundary or limitation |
|---|---|---|
| Atmosphere and fluid mechanics | Standard troposphere quantities, Reynolds and Mach estimates | Low-altitude atmosphere and low-Mach screening assumptions |
| Aerodynamics | Approximate lift requirement, parasite/induced drag, lift-to-drag ratio | Not a CFD calculation or measured airfoil polar |
| Structural mechanics | Idealized hollow wing spar mass, bending stress, safety factor, deflection | Beam approximation only; no torsion, buckling or structural certification |
| Material selection | Illustrative metal-property presets and editable custom properties | Materials are not certified design allowables; no composites model |
| Thermal engineering | Flat-plate heat transfer and one-dimensional skin conduction | Not transient/conjugate thermal simulation |
| Electric-cruise energy | Estimated electricity for a constant-condition segment | No battery sizing or complete aircraft mission |
| Environmental screening | Editable electricity intensity and illustrative material factors | A partial proxy, not a life-cycle assessment |
| Numerical exploration | Material comparison, bounded spar-height sweeps and batch CSV | Not global optimization or external model validation |

## Intended use

Try alternative geometry, flight conditions, loads or material assumptions and examine the implications. Export the calculated values and compare scenarios. Review `METHODOLOGY.md` before interpreting results: each equation has simplified assumptions that limit applicability.

## Independent status

The project has no educational-programme affiliation or endorsement. Its name, source, documentation and web interface are presented exclusively as a standalone aerospace engineering calculator.

## Safety and accuracy

Not suitable for real aircraft component design, manufacturing approvals, operational planning or flight safety. Do not treat test success as experimental/physical validation.
