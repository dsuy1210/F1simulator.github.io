from dataclasses import dataclass


@dataclass
class EnergyModel:
    electric_fraction: float = 0.5  # 50% electric power
    ers_recharge_factor: float = 2.0  # 2x recharge vs old regs


def active_aero_bonus(in_active_aero: bool) -> float:
    return 0.6 if in_active_aero else 0.0


def overtake_mode_bonus(in_overtake_mode: bool) -> float:
    return 0.4 if in_overtake_mode else 0.0


def boost_button_bonus(using_boost: bool) -> float:
    return 0.2 if using_boost else 0.0

