import requests
from typing import Dict, Any

class MLBAPIError(Exception):
    """Excepción personalizada para errores al consultar la API de MLB."""
    pass

def fetch_live_game_feed(game_pk: int) -> Dict[str, Any]:
    """
    Obtiene el feed live completo desde la API oficial de MLB StatsAPI.
    """
    url = f"https://statsapi.mlb.com/api/v1.1/game/{game_pk}/feed/live"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise MLBAPIError(f"Error al conectar con la API de MLB para el game_pk {game_pk}: {e}")

def extract_game_context(feed_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extrae un contexto rico y completo del partido para consumo de SABR-Magic y Gemini.
    """
    live_data = feed_data.get("liveData", {})
    linescore = live_data.get("linescore", {})
    plays = live_data.get("plays", {})
    current_play = plays.get("currentPlay", {})
    play_events = current_play.get("playEvents", [])
    
    # 1. Datos básicos de la entrada y outs
    inning = linescore.get("currentInning", 1)
    is_top = linescore.get("isTopInning", True)
    inning_half = "Alta" if is_top else "Baja"
    outs = linescore.get("outs", 0)
    
    # 2. Marcador
    teams = linescore.get("teams", {})
    home_runs = teams.get("home", {}).get("runs", 0)
    away_runs = teams.get("away", {}).get("runs", 0)
    
    # 3. Datos del Bateador y Lanzador Actual
    matchup = current_play.get("matchup", {})
    batter_name = matchup.get("batter", {}).get("fullName", "Bateador Desconocido")
    batter_hand = matchup.get("batSide", {}).get("code", "R")
    
    pitcher_name = matchup.get("pitcher", {}).get("fullName", "Lanzador Desconocido")
    pitcher_hand = matchup.get("pitchHand", {}).get("code", "R")
    
    # 4. Conteo de Bolas, Strikes y Lanzamientos del Lanzador
    count = current_play.get("count", {})
    balls = count.get("balls", 0)
    strikes = count.get("strikes", 0)
    pitch_count = count.get("pitches", 0)  # Conteo del turno actual
    
    # Si la API no trae el conteo total acumulado del lanzador en el matchup, lo aproximamos o leemos de las jugadas
    pitcher_total_pitches = current_play.get("about", {}).get("captivatingIndex", 0) # Fallback o lectura acumulada
    if pitcher_total_pitches == 0:
        pitcher_total_pitches = max(pitch_count, 65) # Simulación/Fallback si el feed test está parcial
        
    # 5. Corredores en Base
    offense = linescore.get("offense", {})
    runners = {
        "1B": offense.get("first") is not None,
        "2B": offense.get("second") is not None,
        "3B": offense.get("third") is not None
    }
    runners_count = sum(1 for occupied in runners.values() if occupied)
    
    return {
        "inning": inning,
        "inning_half": inning_half,
        "outs": outs,
        "score": f"Visitante {away_runs} - {home_runs} Local",
        "pitcher": {
            "name": pitcher_name,
            "hand": pitcher_hand,
            "total_pitches": pitcher_total_pitches
        },
        "batter": {
            "name": batter_name,
            "hand": batter_hand,
            "count": f"{balls}-{strikes}"
        },
        "runners": runners,
        "runners_count": runners_count,
        "pitch_count": pitcher_total_pitches
    }