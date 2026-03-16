from dataclasses import dataclass


@dataclass
class Driver:
    name: str
    aggression: float = 0.5  # 0–1
    wet_skill: float = 0.5   # 0–1

