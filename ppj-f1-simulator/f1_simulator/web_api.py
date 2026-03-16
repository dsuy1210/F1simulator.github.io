from typing import Any, Dict

from f1_simulator.monte_carlo import run_monte_carlo


def simulate(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Thin API wrapper to be called from the web backend.

    Expected payload fields (you can extend this over time):
    - grand_prix: str  (required)
    - runs: int        (optional, default 200)
    - driver: str      (optional, for the frontend to know which car to highlight)
    - current_lap, current_position, tyres_timeline, quali_lap_time, etc.
      are accepted in payload but not yet fully wired into the physics model.
    """
    grand_prix = payload.get("grand_prix", "Silverstone")
    runs = int(payload.get("runs", 200))

    mc = run_monte_carlo(grand_prix, runs)

    # Map to web-facing keys you described.
    response: Dict[str, Any] = {
        "meta": {
            "grand_prix": grand_prix,
            "runs": mc["runs"],
        },
        "safety_car_implement": {
            "order": mc["a_most_likely_order_after_sc"]["order"],
            "probability": mc["a_most_likely_order_after_sc"]["probability"],
        },
        "rain_coming": {
            "order": mc["b_most_likely_order_after_rain"]["order"],
            "probability": mc["b_most_likely_order_after_rain"]["probability"],
        },
        # Position-over-laps requires per-lap logging in the core engine.
        # For now we only return final average gaps; frontend can infer relative
        # strength, and we can extend this later to a full lap-by-lap timeline.
        "position": {
            "avg_gaps_end_lap20": mc["c_avg_gaps_end_lap20"],
        },
        "predict": mc["f_overtake_summary"],
        "best_sc_beneficiary": mc["d_best_sc_beneficiary"],
        "worst_rain_team": mc["e_worst_rain_team"],
    }

    if "driver" in payload:
        response["meta"]["driver"] = payload["driver"]

    return response

