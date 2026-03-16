from collections import Counter, defaultdict
from statistics import mean
from typing import Dict, List, Tuple

from f1_simulator.race_engine import RaceResult, run_simulation


def _order_key(cars) -> Tuple[str, ...]:
    return tuple(c.name for c in cars)


def run_monte_carlo(grand_prix_name: str, runs: int = 10000) -> Dict:
    """
    Run many stochastic simulations and aggregate answers for (a)-(f).
    """
    order_after_sc_counts: Counter[Tuple[str, ...]] = Counter()
    order_after_rain_counts: Counter[Tuple[str, ...]] = Counter()

    sc_gain_by_car: defaultdict[str, List[float]] = defaultdict(list)
    rain_team_penalty_by_team: defaultdict[str, List[float]] = defaultdict(list)
    gaps_samples: defaultdict[str, List[float]] = defaultdict(list)
    worst_rain_team_counts: Counter[str] = Counter()

    overtake_catch_laps: defaultdict[str, List[float]] = defaultdict(list)
    overtake_probs: defaultdict[str, List[float]] = defaultdict(list)

    for i in range(runs):
        result: RaceResult = run_simulation(grand_prix_name, seed=i)

        order_after_sc_counts[_order_key(result.order_after_sc)] += 1
        order_after_rain_counts[_order_key(result.order_after_first_rain_tyres)] += 1

        # Store SC gain for the reported best beneficiary in this run.
        car_name, gain = result.best_sc_beneficiary
        sc_gain_by_car[car_name].append(gain)

        # Store worst rain team for this run.
        team, penalty = result.worst_rain_team
        worst_rain_team_counts[team] += 1
        rain_team_penalty_by_team[team].append(penalty)

        # Gaps at end of lap 20
        for name, gap in result.gaps_end_lap20.items():
            gaps_samples[name].append(gap)

        # Overtake predictions
        for car, pred in result.overtake_predictions.items():
            overtake_catch_laps[car].append(pred["catch_lap"])
            overtake_probs[car].append(pred["overtake_probability"])

    # a) Most likely race order after SC
    most_common_sc_order, sc_order_freq = order_after_sc_counts.most_common(1)[0]

    # b) Most likely race order after first rain-tyre phase
    most_common_rain_order, rain_order_freq = order_after_rain_counts.most_common(1)[0]

    # d) Car benefitting most from SC pits (average gain)
    avg_sc_gain_by_car = {
        name: mean(gains) for name, gains in sc_gain_by_car.items()
    }
    best_sc_car = max(avg_sc_gain_by_car.items(), key=lambda kv: kv[1])

    # e) Team with least efficient rain-tyre decision (most often worst)
    worst_team, worst_team_count = worst_rain_team_counts.most_common(1)[0]
    avg_penalty_worst_team = mean(rain_team_penalty_by_team[worst_team])

    # c) Average gaps at end of lap 20
    avg_gaps = {name: mean(vals) for name, vals in gaps_samples.items()}

    # f) Aggregate catch lap and overtake probability
    overtake_summary = {}
    for car, laps in overtake_catch_laps.items():
        overtake_summary[car] = {
            "avg_catch_lap": mean(laps),
            "avg_overtake_probability": mean(overtake_probs[car]),
        }

    return {
        "runs": runs,
        "a_most_likely_order_after_sc": {
            "order": most_common_sc_order,
            "probability": sc_order_freq / runs,
        },
        "b_most_likely_order_after_rain": {
            "order": most_common_rain_order,
            "probability": rain_order_freq / runs,
        },
        "c_avg_gaps_end_lap20": avg_gaps,
        "d_best_sc_beneficiary": {
            "car": best_sc_car[0],
            "avg_gain": best_sc_car[1],
        },
        "e_worst_rain_team": {
            "team": worst_team,
            "probability": worst_team_count / runs,
            "avg_penalty": avg_penalty_worst_team,
        },
        "f_overtake_summary": overtake_summary,
    }

