from dataclasses import dataclass

from f1_simulator.models.car import CarState, TyreState
from f1_simulator.models.track import Track


@dataclass
class PitStopDecision:
    pit_this_lap: bool
    new_compound: str | None = None


def apply_pit_stop(
    car: CarState,
    track: Track,
    lap: int,
    under_safety_car: bool,
    new_compound: str | None,
) -> float:
    """
    Apply pit stop timings and tyre change to car.
    Returns the pit loss (seconds) applied this lap.
    """
    if not new_compound:
        return 0.0

    pit_loss = track.normal_pit_loss
    if under_safety_car:
        pit_loss -= 10.0
        car.has_pitted_under_sc = True

    car.tyre = TyreState(compound=new_compound, age_laps=0)
    car.pit_stops.append({"lap": lap, "compound": new_compound, "under_sc": under_safety_car})
    car.pit_this_lap = False
    return pit_loss

