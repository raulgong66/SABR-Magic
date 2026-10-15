import time
from src.api_client import MLBApiClient
from src.metrics_engine import calculate_mei, calculate_li, evaluate_alert

def run_monitor(game_pk: int, interval_seconds: int = 30):
    """
    Main monitoring loop. Fetches live play-by-play data, calculates MEI and LI_k,
    and prints real-time tactical alerts to the console.
    """
    client = MLBApiClient()
    print(f"Starting SABR-Magic real-time monitor for Game PK: {game_pk}")
    print("Press Ctrl+C to stop.\n")

    try:
        while True:
            data = client.get_play_by_play(game_pk)
            if not data:
                print("Waiting for game data...")
                time.sleep(interval_seconds)
                continue

            all_plays = data.get('allPlays', [])
            if not all_plays:
                print("Game has not started or no plays recorded yet.")
                time.sleep(interval_seconds)
                continue

            last_play = all_plays[-1]
            matchup = last_play.get('matchup', {})
            count = last_play.get('count', {})
            about = last_play.get('about', {})

            pitcher_name = matchup.get('pitcher', {}).get('fullName', 'Unknown')
            batter_name = matchup.get('batter', {}).get('fullName', 'Unknown')
            inning = about.get('inning', 1)
            half = "Top" if about.get('isTopInning', True) else "Bottom"
            outs = count.get('outs', 0)

            # Calculate cumulative pitch count for the current pitcher
            pitcher_id = matchup.get('pitcher', {}).get('id')
            pitch_count = 0
            for play in all_plays:
                if play.get('matchup', {}).get('pitcher', {}).get('id') == pitcher_id:
                    pitch_count += len(play.get('playEvents', []))

            # Estimate runners on base count from match-up info
            runners_count = 0
            if last_play.get('matchup', {}).get('postOnFirst'): runners_count += 1
            if last_play.get('matchup', {}).get('postOnSecond'): runners_count += 1
            if last_play.get('matchup', {}).get('postOnThird'): runners_count += 1

            # Core SABR-Magic Calculations
            mei = calculate_mei(pitch_count)
            li = calculate_li(inning, outs, runners_count)
            alert = evaluate_alert(mei)

            # Console Telemetry Output
            print("=" * 65)
            print(f"SABR-MAGIC LIVE MONITOR | {half} {inning}th Inning - {outs} Outs")
            print(f"Pitcher: {pitcher_name} ({pitch_count} pitches)")
            print(f"Batter:  {batter_name} | Count: {count.get('balls', 0)}-{count.get('strikes', 0)}")
            print("-" * 65)
            print(f" ► MEI (Allostatic Stress): {mei}")
            print(f" ► LI  (Leverage Index):    {li}")
            print(f" ► Tactical Status:         [{alert}]")
            print("=" * 65 + "\n")

            time.sleep(interval_seconds)

    except KeyboardInterrupt:
        print("\nSABR-Magic monitor stopped by user.")

if __name__ == "__main__":
    client = MLBApiClient()
    games = client.get_todays_games()
    
    if games:
        sample_game_pk = games[0]['gamePk']
        run_monitor(sample_game_pk)
    else:
        print("No MLB games found scheduled for today to run the monitor.")
