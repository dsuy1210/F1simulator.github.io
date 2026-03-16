from dataclasses import dataclass


@dataclass
class Track:
    name: str
    base_lap_time: float  # reference lap time in seconds (dry, fresh medium)
    laps: int
    pit_lane_travel_time: float
    pit_stop_time: float
    length_km: float | None = None
    corners: int | None = None
    track_type: str | None = None
    longest_straight_m: float | None = None
    avg_straight_length_m: float | None = None
    overtake_difficulty: int | None = None
    top_speed_kmh: float | None = None
    braking_zones: int | None = None

    @property
    def normal_pit_loss(self) -> float:
        return self.pit_lane_travel_time + self.pit_stop_time

