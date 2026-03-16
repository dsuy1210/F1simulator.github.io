# F1simulator.github.io
The simulation must consider:
1. Track parameters
2. Car performance
3. Tyre degradation
4. Pit stop losses
5. Safety Car compression
6. Weather changes
7. F1 2026 regulations
F1 2026 regulation changes to include:
- DRS is removed
- Active Aero allows low-drag mode on straights
- Overtake Mode available when gap ≤ 1s
- Boost Button allows temporary energy deployment
- Power unit now has 50% electric power
- ERS recharge doubled
- Cars have less downforce and slightly slower corner speeds
Race simulation rules:
Lap time model:
LapTime =
BaseLap
+ TyreDelta
+ (TyreDeg × TyreAge)
+ TrackConditionModifier
- ActiveAeroBonus
- OvertakeModeBonus
- PitOutTyreBonus
Safety Car rules:
- Lap time increases by 40%
- Gaps shrink to 30%
Pit stop rules:
PitLoss =
PitLaneTravelTime
+ PitStopTime
Pit during Safety Car reduces pit loss by 10 seconds.
Rain tyre models:
Intermediate:
- 2.0s faster per lap
- 20% probability of +2s loss due to aquaplaning
Wet:
- slower but stable
- no extra loss

Simulation requirements:
Run deterministic lap simulation combined with probabilistic weather tyre effects.
Return the following outputs:
