from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TyreModel:
    name: str  # "M", "S", "H", "I", "W"
    base_delta: float
    degradation_per_lap: float


TYRE_MODELS = {
    "M": TyreModel("M", base_delta=0.0, degradation_per_lap=0.05),
    "S": TyreModel("S", base_delta=-0.8, degradation_per_lap=0.07),
    "H": TyreModel("H", base_delta=0.6, degradation_per_lap=0.04),
    # Intermediates and wets are referenced against dry base,
    # but their effective behaviour depends on conditions.
    "I": TyreModel("I", base_delta=-2.0, degradation_per_lap=0.06),
    "W": TyreModel("W", base_delta=1.0, degradation_per_lap=0.04),
}


def get_tyre_model(compound: str) -> TyreModel:
    return TYRE_MODELS[compound]

