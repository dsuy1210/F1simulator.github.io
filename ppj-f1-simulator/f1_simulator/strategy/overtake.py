from f1_simulator.models.car import CarState


def update_mode_flags(cars: list[CarState]) -> None:
    """
    Update Active Aero / Overtake Mode / Boost flags based on gaps.
    """
    if not cars:
        return

    # Leader has clean air and active aero, may use boost defensively when needed.
    leader = cars[0]
    leader.in_active_aero = True
    leader.in_overtake_mode = False
    leader.using_boost = False

    for idx in range(1, len(cars)):
        car = cars[idx]
        ahead = cars[idx - 1]
        gap_to_ahead = car.total_race_time - ahead.total_race_time

        # Simple model: if gap <= 1.0s, car can use overtake mode and boost.
        if gap_to_ahead <= 1.0:
            car.in_overtake_mode = True
            car.using_boost = True
        else:
            car.in_overtake_mode = False
            car.using_boost = False

        # Following car has slightly less active aero benefit due to reduced straight-line efficiency.
        car.in_active_aero = gap_to_ahead > 0.5

