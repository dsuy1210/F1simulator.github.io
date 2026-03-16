from dataclasses import dataclass
from random import Random


@dataclass
class WeatherPhase:
    start_lap: int
    end_lap: int
    condition: str  # "dry", "light_rain", "heavy_rain"


def track_condition_modifier(condition: str, on_slicks: bool) -> float:
    """
    Deterministic modifier for track conditions.
    Positive values slow the lap.
    """
    if condition == "dry":
        return 0.0
    if condition == "light_rain":
        return 2.5 if on_slicks else 0.0
    if condition == "heavy_rain":
        return 5.0 if on_slicks else 0.0
    return 0.0


def intermediate_stochastic_aquaplaning_loss(rng: Random) -> float:
    """
    20% probability of +2s loss due to aquaplaning on intermediates.
    """
    return 2.0 if rng.random() < 0.2 else 0.0

