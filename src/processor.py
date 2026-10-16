import urllib.request
import json

GAME_PK = "849810"

def fetch_live_game_data(game_pk: str = GAME_PK) -> dict:
    url = f"https://statsapi.mlb.com/api/v1.1/game/{game_pk}/feed/live"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"❌ Error al consultar la MLB StatsAPI para el juego {game_pk}: {e}")
        return {}

def extract_play_context(play_data: dict, all_plays_history: list) -> dict:
    """
    Extrae el contexto de una jugada real del juego 849810,
    calculando con precisión los pitcheos acumulados del lanzador en el partido.
    """
    about = play_data.get('about', {})
    count = play_data.get('count', {})
    matchup = play_data.get('matchup', {})
    
    inning = about.get('inning', 1)
    inning_half = "Top" if about.get('isTopInning', True) else "Bottom"
    outs = count.get('outs', 0)
    
    pitcher_info = matchup.get('pitcher', {})
    pitcher_name = pitcher_info.get('fullName', 'Desconocido')
    pitcher_id = pitcher_info.get('id')
    
    batter_info = matchup.get('batter', {})
    batter_name = batter_info.get('fullName', 'Desconocido')
    
    balls = count.get('balls', 0)
    strikes = count.get('strikes', 0)

    # 🧮 CÁLCULO DE PITCHEOS ACUMULADOS EN EL JUEGO HASTA ESTE AT-BAT
    accumulated_pitches = 0
    if pitcher_id:
        for p in all_plays_history:
            p_matchup = p.get('matchup', {})
            if p_matchup.get('pitcher', {}).get('id') == pitcher_id:
                events = p.get('playEvents', [])
                accumulated_pitches += len([e for e in events if e.get('isPitch', False)])
                if p.get('atBatIndex') == play_data.get('atBatIndex'):
                    break

    runners = play_data.get('runners', [])
    active_runners = [r for r in runners if r.get('end', {}).get('isOut') is False and r.get('end', {}).get('base') is not None]
    runners_count = len(active_runners)
    result_description = play_data.get('result', {}).get('description', 'En proceso...')

    return {
        "at_bat_index": play_data.get('atBatIndex', 0),
        "inning": inning,
        "inning_half": inning_half,
        "outs": outs,
        "pitcher": {
            "id": pitcher_id,
            "name": pitcher_name,
            "total_pitches": max(accumulated_pitches, 1)
        },
        "batter": {
            "name": batter_name,
            "count": f"{balls}-{strikes}"
        },
        "runners_count": runners_count,
        "result": result_description
    }

def calculate_mei(pitcher_data: dict, game_context: dict) -> float:
    total_pitches = pitcher_data.get("total_pitches", 1)
    runners = game_context.get("runners_count", 0)
    outs = game_context.get("outs", 0)
    stress_base = (total_pitches / 15.0) + (runners * 0.8) - (outs * 0.2)
    return round(max(stress_base, 0.5), 2)

def calculate_nate(game_context: dict, metrics: dict) -> dict:
    runners = game_context.get("runners_count", 0)
    outs = game_context.get("outs", 0)
    inning = game_context.get("inning", 1)
    
    li = 1.0 + (runners * 0.5) + (max(7 - inning, 0) * 0.1) - (outs * 0.15)
    li = round(max(li, 0.5), 2)
    nate = round(li * (metrics.get("mei", 1.0) * 0.5), 2)
    
    alert_status = "NORMAL"
    if li > 2.0 or nate > 3.0:
        alert_status = "¡ALERTA ROJA - ALTO APALANCAMIENTO!"
    elif li > 1.5:
        alert_status = "PRECAUCIÓN - SITUACIÓN CLAVE"

    return {
        "leverage_index": li,
        "nate": nate,
        "mei": metrics.get("mei", 1.0),
        "alert_status": alert_status
    }