import csv
from pathlib import Path

from f1_simulator.models.track import Track


CSV_PATH = Path(__file__).resolve().parent.parent / "grandprix" / "grandprix.csv"


def load_track_from_grandprix(name: str) -> Track:
    """
    Load track parameters from grandprix.csv given a grand prix name.

    Example input names accepted (case-insensitive, trimmed):
    - "Silverstone"
    - "British Grand Prix @ Silverstone" -> will still match "Silverstone" if you pre-clean.
    """
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"grandprix CSV not found at {CSV_PATH}")

    normalized = name.strip().lower()

    with CSV_PATH.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            track_name = row["track_name"].strip()
            if track_name.lower() == normalized:
                length_km = float(row["length_km"])
                corners = int(row["corners"])
                laps = int(row["laps"])
                track_type = row["track_type"]
                longest_straight_m = float(row["longest_straight_m"])
                avg_straight_length_m = float(row["avg_straight_length_m"])
                overtake_difficulty = int(row["overtake_difficulty"])
                top_speed_kmh = float(row["top_speed_kmh"])
                braking_zones = int(row["braking_zones"])

                # Rough heuristic: base lap time from length and top speed,
                # then reduce a bit for corners and braking demand.
                base_time = (length_km / (top_speed_kmh / 3600.0)) * 0.8
                base_time += 0.15 * corners
                base_time += 0.1 * braking_zones

                # Simple pit timing heuristic scaled with length.
                pit_lane_travel_time = 18.0 * (length_km / 5.0)
                pit_stop_time = 2.5

                return Track(
                    name=track_name,
                    base_lap_time=base_time,
                    laps=laps,
                    pit_lane_travel_time=pit_lane_travel_time,
                    pit_stop_time=pit_stop_time,
                    length_km=length_km,
                    corners=corners,
                    track_type=track_type,
                    longest_straight_m=longest_straight_m,
                    avg_straight_length_m=avg_straight_length_m,
                    overtake_difficulty=overtake_difficulty,
                    top_speed_kmh=top_speed_kmh,
                    braking_zones=braking_zones,
                )

    raise ValueError(f"Grand Prix '{name}' not found in {CSV_PATH}")

