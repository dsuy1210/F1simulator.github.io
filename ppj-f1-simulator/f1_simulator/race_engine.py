from __future__ import annotations

from dataclasses import dataclass
from random import Random
from typing import Dict, List, Tuple

from f1_simulator.models.car import CarState, TyreState, clone_for_counterfactual
from f1_simulator.models.track import Track
from f1_simulator.physics.energy import (
    active_aero_bonus,
    boost_button_bonus,
    overtake_mode_bonus,
)
from f1_simulator.physics.tyres import get_tyre_model
from f1_simulator.physics.weather import (
    WeatherPhase,
    intermediate_stochastic_aquaplaning_loss,
    track_condition_modifier,
)
from f1_simulator.strategy.overtake import update_mode_flags
from f1_simulator.strategy.pitstop import apply_pit_stop
from f1_simulator.grandprix_loader import load_track_from_grandprix


@dataclass
class RaceResult:
    final_order: List[CarState]
    order_after_sc: List[CarState]
    order_after_first_rain_tyres: List[CarState]
    gaps_end_lap20: Dict[str, float]
    best_sc_beneficiary: Tuple[str, float]
    worst_rain_team: Tuple[str, float]
    overtake_predictions: Dict[str, Dict[str, float]]


def _initial_cars(track: Track) -> List[CarState]:
    """Initialise six cars with the scenario described in the analysis."""
    cars = [
        CarState("A1", "Alpha", base_delta=-0.5, tyre=TyreState("M"), fuel_laps_remaining=track.laps, position_index=0),
        CarState("B1", "Beta", base_delta=-0.2, tyre=TyreState("M"), fuel_laps_remaining=track.laps, position_index=1),
        CarState("G1", "Gamma", base_delta=0.0, tyre=TyreState("M"), fuel_laps_remaining=track.laps, position_index=2),
        CarState("A2", "Alpha", base_delta=0.3, tyre=TyreState("M"), fuel_laps_remaining=track.laps, position_index=3),
        CarState("B2", "Beta", base_delta=0.5, tyre=TyreState("M"), fuel_laps_remaining=track.laps, position_index=4),
        CarState("G2", "Gamma", base_delta=0.7, tyre=TyreState("M"), fuel_laps_remaining=track.laps, position_index=5),
    ]
    return cars


def _weather_profile() -> List[WeatherPhase]:
    return [
        WeatherPhase(1, 9, "dry"),
        WeatherPhase(10, 15, "light_rain"),
        WeatherPhase(16, 20, "heavy_rain"),
    ]


def _weather_for_lap(lap: int, phases: List[WeatherPhase]) -> str:
    for p in phases:
        if p.start_lap <= lap <= p.end_lap:
            return p.condition
    return "dry"


def _is_safety_car_lap(lap: int) -> bool:
    return lap in (5, 6)


def _pit_strategy_decision(car: CarState, lap: int, condition: str) -> str | None:
    """
    Encodes the strategy used in the narrative:
    - Lap 5 SC: A1, B2, G1 pit M->M.
    - Lap 10: A1, B2, G1 pit -> I.
    - Lap 11: A2, G2 pit -> W.
    - Lap 12: B1 pit -> I.
    - Lap 16: All on I pit -> W.
    """
    if lap == 5 and car.name in {"A1", "B2", "G1"}:
        return "M"
    if lap == 10 and car.name in {"A1", "B2", "G1"}:
        return "I"
    if lap == 11 and car.name in {"A2", "G2"}:
        return "W"
    if lap == 12 and car.name == "B1":
        return "I"
    if lap == 16 and car.tyre.compound == "I":
        return "W"
    return None


def _lap_time_for_car(car: CarState, track: Track, lap: int, condition: str, safety_car: bool, rng: Random) -> float:
    tyre_model = get_tyre_model(car.tyre.compound)
    base = track.base_lap_time

    # Tyre effects
    tyre_delta = tyre_model.base_delta
    tyre_deg = tyre_model.degradation_per_lap * car.tyre.age_laps

    # Track condition
    on_slicks = car.tyre.compound in {"M", "S", "H"}
    condition_modifier = track_condition_modifier(condition, on_slicks=on_slicks)

    # Rain-tyre stochastic effect: 20% chance of +2s aquaplaning loss on inters.
    if car.tyre.compound == "I" and condition != "dry":
        tyre_delta += intermediate_stochastic_aquaplaning_loss(rng)

    # Active aero and modes
    aero_bonus = active_aero_bonus(car.in_active_aero)
    overtake_bonus = overtake_mode_bonus(car.in_overtake_mode)
    boost_bonus = boost_button_bonus(car.using_boost)

    pit_out_bonus = -0.5 if car.last_lap_time is None or car.tyre.age_laps == 0 else 0.0

    # Small random lap-time noise to reflect driver variability / wind / track evolution.
    noise = rng.gauss(0.0, 0.1)

    lap_time = (
        base
        + car.base_delta
        + tyre_delta
        + tyre_deg
        + condition_modifier
        - aero_bonus
        - overtake_bonus
        - boost_bonus
        + pit_out_bonus
        + noise
    )

    if safety_car:
        lap_time *= 1.4

    return lap_time


def run_simulation(grand_prix_name: str = "Silverstone", seed: int | None = None) -> RaceResult:
    track = load_track_from_grandprix(grand_prix_name)
    weather_phases = _weather_profile()
    cars = _initial_cars(track)

    order_after_sc: List[CarState] | None = None
    order_after_first_rain: List[CarState] | None = None

    # Simple counterfactual copy of A1 without SC pit for benefit estimation.
    a1_counterfactual = clone_for_counterfactual(next(c for c in cars if c.name == "A1"))

    rng = Random(seed)

    for lap in range(1, track.laps + 1):
        condition = _weather_for_lap(lap, weather_phases)
        safety_car = _is_safety_car_lap(lap)

        # Update mode flags based on current running order.
        cars.sort(key=lambda c: c.total_race_time)
        update_mode_flags(cars)

        # Apply pit decisions and compute lap times.
        for car in cars:
            new_compound = _pit_strategy_decision(car, lap, condition)
            pit_loss = 0.0
            if new_compound:
                pit_loss = apply_pit_stop(
                    car,
                    track,
                    lap,
                    under_safety_car=safety_car,
                    new_compound=new_compound,
                )
                if new_compound in {"I", "W"} and car.rain_tyre_lap is None:
                    car.rain_tyre_lap = lap

            lap_time = _lap_time_for_car(car, track, lap, condition, safety_car, rng)
            car.last_lap_time = lap_time
            car.total_race_time += lap_time + pit_loss
            car.tyre.age_laps += 1
            car.fuel_laps_remaining -= 1.0

        # Safety car compression of gaps at start of SC.
        if lap == 5:
            cars.sort(key=lambda c: c.total_race_time)
            leader_time = cars[0].total_race_time
            for car in cars[1:]:
                gap = car.total_race_time - leader_time
                car.total_race_time = leader_time + gap * 0.3

        cars.sort(key=lambda c: c.total_race_time)

        if lap == 6:
            order_after_sc = [c for c in cars]

        # Once the last car has switched to a rain tyre, capture order.
        if order_after_first_rain is None and all(
            (c.rain_tyre_lap is not None) for c in cars
        ):
            order_after_first_rain = [c for c in cars]

        # Counterfactual A1: skip SC pit and instead pit under green on lap 8.
        if lap in (5, 6):
            # Under SC, no pit for counterfactual.
            lap_time = _lap_time_for_car(
                a1_counterfactual, track, lap, condition, safety_car=True, rng=rng
            )
            a1_counterfactual.total_race_time += lap_time
            a1_counterfactual.tyre.age_laps += 1
        elif lap == 8:
            # Green flag pit for mediums.
            lap_time = _lap_time_for_car(
                a1_counterfactual, track, lap, condition, safety_car=False, rng=rng
            )
            a1_counterfactual.total_race_time += lap_time + track.normal_pit_loss
            a1_counterfactual.tyre = TyreState("M", age_laps=0)
            a1_counterfactual_pit_done = True
        else:
            lap_time = _lap_time_for_car(
                a1_counterfactual, track, lap, condition, safety_car=False, rng=rng
            )
            a1_counterfactual.total_race_time += lap_time
            a1_counterfactual.tyre.age_laps += 1

    cars.sort(key=lambda c: c.total_race_time)
    final_order = [c for c in cars]

    # Gaps at end of lap 20
    leader_time = final_order[0].total_race_time
    gaps_end = {c.name: c.total_race_time - leader_time for c in final_order}

    # SC benefit for A1
    a1_actual = next(c for c in final_order if c.name == "A1")
    sc_gain = a1_counterfactual.total_race_time - a1_actual.total_race_time
    best_sc_beneficiary = (a1_actual.name, sc_gain)

    # Very lightweight estimation of worst rain-team decision:
    # penalise teams whose drivers switched either too late or to wets in light rain.
    rain_penalty_by_team: Dict[str, float] = {"Alpha": 0.0, "Beta": 0.0, "Gamma": 0.0}
    for c in final_order:
        if c.rain_tyre_lap is None:
            continue
        # Late inters: B1 laps 10–12 on slicks in rain => ~6s.
        if c.name == "B1":
            rain_penalty_by_team[c.team] += 6.0
        # Early wets: A2, G2 => ~5s each.
        if c.name in {"A2", "G2"}:
            rain_penalty_by_team[c.team] += 5.0

    worst_team = max(rain_penalty_by_team.items(), key=lambda kv: kv[1])

    # Overtake predictions: simple, based on final gaps and relative pace.
    overtake_predictions: Dict[str, Dict[str, float]] = {}
    for idx in range(1, len(final_order)):
        car = final_order[idx]
        ahead = final_order[idx - 1]
        gap = car.total_race_time - ahead.total_race_time
        # Approximate pace diff by base delta.
        pace_diff = ahead.base_delta - car.base_delta
        if pace_diff >= 0:
            overtake_predictions[car.name] = {
                "catch_lap": float("inf"),
                "overtake_probability": 0.0,
            }
        else:
            # Would catch in abs(gap / pace_diff) laps, but we cap probability.
            laps_to_catch = gap / abs(pace_diff)
            prob = min(0.5, 0.1 * abs(pace_diff))
            overtake_predictions[car.name] = {
                "catch_lap": track.laps + laps_to_catch,
                "overtake_probability": prob,
            }

    return RaceResult(
        final_order=final_order,
        order_after_sc=order_after_sc or [],
        order_after_first_rain_tyres=order_after_first_rain or [],
        gaps_end_lap20=gaps_end,
        best_sc_beneficiary=best_sc_beneficiary,
        worst_rain_team=worst_team,
        overtake_predictions=overtake_predictions,
    )

