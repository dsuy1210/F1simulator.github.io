"""
f1_simulator package

Provides a lightweight Formula 1 race simulation engine tailored to 2026
regulations, including:
- Active aero (no DRS)
- Overtake mode and boost deployment
- Hybrid power unit modelling at a coarse level
- Weather and tyre strategy effects
"""

from .race_engine import run_simulation

__all__ = ["run_simulation"]
