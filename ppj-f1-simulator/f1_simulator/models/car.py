from dataclasses import dataclass, field
from typing import Optional


@dataclass
class TyreState:
    compound: str  # "M", "S", "H", "I", "W"
    age_laps: int = 0


@dataclass
class CarState:
    name: str
    team: str
    base_delta: float  # performance offset vs base car (s/lap)
    tyre: TyreState
    fuel_laps_remaining: float
    position_index: int  # grid position index (0 = pole)
    gap_to_leader: float = 0.0
    last_lap_time: Optional[float] = None
    total_race_time: float = 0.0
    has_pitted_under_sc: bool = False

    # Flags updated per lap
    in_active_aero: bool = True
    in_overtake_mode: bool = False
    using_boost: bool = False
    pit_this_lap: bool = False

    # Strategy bookkeeping for analysis
    pit_stops: list = field(default_factory=list)
    rain_tyre_lap: Optional[int] = None
    sc_pit_gain_seconds: float = 0.0


def clone_for_counterfactual(car: CarState) -> CarState:
    """Shallow clone suitable for simple counterfactual comparisons."""
    return CarState(
        name=car.name,
        team=car.team,
        base_delta=car.base_delta,
        tyre=TyreState(compound=car.tyre.compound, age_laps=car.tyre.age_laps),
        fuel_laps_remaining=car.fuel_laps_remaining,
        position_index=car.position_index,
        gap_to_leader=car.gap_to_leader,
    )

