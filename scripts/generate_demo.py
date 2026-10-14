"""Generate a transparent set of example results without the Streamlit UI.

Run from repository root: python scripts/generate_demo.py
"""
from __future__ import annotations
import csv
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from aeromat.analysis import from_record
from aeromat.model import Inputs, MATERIALS, calculate


def main() -> None:
    source = REPO_ROOT / 'data' / 'example_scenarios.csv'
    target = REPO_ROOT / 'data' / 'example_results.csv'
    output = []
    with source.open(newline='', encoding='utf-8') as stream:
        for i, record in enumerate(csv.DictReader(stream), start=2):
            name = record['material']
            parameters = from_record(record, Inputs())
            result = calculate(parameters, MATERIALS[name])
            output.append({'scenario_row': i, **result.flat()})
    with target.open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(output[0]))
        writer.writeheader()
        writer.writerows(output)
    print(f'Generated {len(output)} sample engineering result rows: {target.relative_to(REPO_ROOT)}')
    for row in output:
        print(f"  {row['material']}: {row['spar_mass_kg']:.1f} kg spars, "
              f"{row['mission_electricity_kwh']:.1f} kWh, screening_pass={row['screening_pass']}")


if __name__ == '__main__':
    main()
