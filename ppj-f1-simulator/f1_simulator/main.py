from f1_simulator.web_api import simulate


def main() -> None:
    # ======= INPUTS GIỐNG WEB =======
    grand_prix = input("Grand Prix (e.g. Silverstone, Monaco, Monza): ").strip() or "Silverstone"

    driver = input("Driver ID (e.g. A1, B1...): ").strip() or "A1"
    team = input("Team name (optional, e.g. Alpha): ").strip() or None

    quali_raw = input("Quali fastest lap time in seconds (optional, e.g. 88.732): ").strip()
    quali_lap_time = float(quali_raw) if quali_raw else None

    current_lap_raw = input("Current lap (optional, press Enter to skip): ").strip()
    current_lap = int(current_lap_raw) if current_lap_raw else None

    current_pos_raw = input("Current position of this car (optional, e.g. 3): ").strip()
    current_position = int(current_pos_raw) if current_pos_raw else None

    runs_raw = input("Monte Carlo runs (default 200): ").strip()
    try:
        runs = int(runs_raw) if runs_raw else 200
    except ValueError:
        runs = 200

    # Tyre timeline input đơn giản (có thể mở rộng sau).
    print("Tyres timeline (optional, format: from-to-compound, ví dụ: 1-10-M;11-20-I).")
    tyres_raw = input("Enter timeline or leave empty: ").strip()
    tyres_timeline = []
    if tyres_raw:
        segments = tyres_raw.split(";")
        for seg in segments:
            try:
                span, compound = seg.split("-")[0:2], seg.split("-")[2]
                from_lap = int(span[0])
                to_lap = int(span[1])
                tyres_timeline.append({"from": from_lap, "to": to_lap, "compound": compound.upper()})
            except Exception:
                continue

    payload = {
        "grand_prix": grand_prix,
        "runs": runs,
        "driver": driver,
        "team": team,
        "quali_lap_time": quali_lap_time,
        "current_lap": current_lap,
        "current_position": current_position,
        "tyres_timeline": tyres_timeline,
    }

    result = simulate(payload)

    print(f"\n=== Simulation summary for {result['meta']['grand_prix']} (runs={result['meta']['runs']}) ===")
    if "driver" in result["meta"]:
        print(f"Driver focus: {result['meta']['driver']}")

    # Safety Car implement
    print("\n=== Safety Car implement (Race order after SC pit stops) ===")
    sc = result["safety_car_implement"]
    print(f"Order: {', '.join(sc['order'])}  (P≈{sc['probability']:.0%})")

    # Rain coming
    print("\n=== Rain coming (Race order after all cars switch to rain tyres) ===")
    rain = result["rain_coming"]
    print(f"Order: {', '.join(rain['order'])}  (P≈{rain['probability']:.0%})")

    # Position (hiện dùng gaps cuối race, có thể nâng cấp thành timeline sau)
    print("\n=== Position (average gaps vs leader at end of lap 20) ===")
    for name, gap in sorted(result["position"]["avg_gaps_end_lap20"].items(), key=lambda kv: kv[1]):
        print(f"{name}: {gap:.2f}s")

    # Predict (overtake)
    print("\n=== Predict (average catch lap & P(overtake) for cars behind) ===")
    for car, data in result["predict"].items():
        catch_lap = data["avg_catch_lap"]
        prob = data["avg_overtake_probability"]
        if catch_lap == float("inf"):
            print(f"{car}: will not catch the car ahead (P(overtake)≈{prob:.0%}).")
        else:
            print(f"{car}: avg catch lap ≈ {catch_lap:.1f}, P(overtake)≈{prob:.0%}.")


if __name__ == "__main__":
    main()

