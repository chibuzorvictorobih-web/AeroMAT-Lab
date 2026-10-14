"""Reproducible comparison, bounded parameter sweeps and batch helpers."""

from dataclasses import fields, replace
from typing import Iterable

from .model import Inputs, Material, Result, calculate


INPUT_FIELDS = {field.name for field in fields(Inputs)}


def compare_materials(inputs: Inputs, materials: Iterable[Material]) -> list[Result]:
    return [calculate(inputs, material) for material in materials]


def height_sweep(inputs: Inputs, materials: Iterable[Material], lower_m: float,
                 upper_m: float, steps: int = 41) -> list[Result]:
    if not 2 <= steps <= 1000:
        raise ValueError("Steps must be between 2 and 1000")
    if not 0 < lower_m < upper_m:
        raise ValueError("Choose 0 < minimum height < maximum height")
    materials = list(materials)
    if not materials:
        raise ValueError("Choose at least one material")
    output = []
    for material in materials:
        for i in range(steps):
            height = lower_m + (upper_m - lower_m) * i / (steps - 1)
            scenario = replace(inputs, spar_height_m=height)
            output.append(calculate(scenario, material))
    return output


def best_feasible(results: Iterable[Result], objective: str = "spar_mass_kg") -> Result | None:
    options = {"spar_mass_kg", "mission_electricity_kwh", "total_mission_kgco2e"}
    if objective not in options:
        raise ValueError(f"Unsupported objective: {objective}")
    feasible = [x for x in results if x.screening_pass]
    return min(feasible, key=lambda x: getattr(x, objective)) if feasible else None


def from_record(row: dict, baseline: Inputs) -> Inputs:
    """Override any subset of numeric Inputs fields from a CSV record.

    Empty cells mean 'use baseline'. Unknown columns intentionally ignored.
    """
    update = {}
    for name in INPUT_FIELDS:
        if name in row:
            value = row[name]
            if value is None or str(value).strip() == "" or str(value).strip().lower() in {"nan", "none"}:
                continue
            try:
                update[name] = float(value)
            except (ValueError, TypeError) as exc:
                raise ValueError(f"Invalid numeric input for '{name}': {value!r}") from exc
    return replace(baseline, **update)
