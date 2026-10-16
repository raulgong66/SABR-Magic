import time
import sys
import os
from datetime import datetime
import zoneinfo

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from processor import analyze_live_game
from api_client import find_active_or_next_game, fetch_live_game_feed, MLBAPIError
from ai_advisor import get_bench_coach_advice

def format_time_stockholm(utc_date_str: str) -> str:
    if not utc_date_str:
        return "Hora por confirmar"
    try:
        dt_utc = datetime.strptime(utc_date_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=zoneinfo.ZoneInfo("UTC"))
        dt_stockholm = dt_utc.astimezone(zoneinfo.ZoneInfo("Europe/Stockholm"))
        return dt_stockholm.strftime("%Y-%m-%d %H:%M:%S (%I:%M %p %Z)")
    except Exception:
        return utc_date_str

def extract_rosters(game_data: dict) -> dict:
    teams = game_data.get("teams", {})
    away_team = teams.get("away", {}).get("name", "Visitante")
    home_team = teams.get("home", {}).get("name", "Local")
    
    away_probable = game_data.get("probablePitchers", {}).get("away", {}).get("fullName", "Por confirmar")
    home_probable = game_data.get("probablePitchers", {}).get("home", {}).get("fullName", "Por confirmar")
    
    players = game_data.get("players", {})
    away_players = [f"{p.get('fullName')} ({p.get('primaryPosition', {}).get('abbreviation', '')})" for p in players.values() if p.get("currentTeam", {}).get("id") == teams.get("away", {}).get("id")]
    home_players = [f"{p.get('fullName')} ({p.get('primaryPosition', {}).get('abbreviation', '')})" for p in players.values() if p.get("currentTeam", {}).get("id") == teams.get("home", {}).get("id")]
            
    return {
        "away_team": away_team, "home_team": home_team,
        "away_probable": away_probable, "home_probable": home_probable,
        "away_roster_sample": away_players[:8] if away_players else ["No disponible"],
        "home_roster_sample": home_players[:8] if home_players else ["No disponible"]
    }

def start_auto_monitor(interval_seconds: int = 30):
    print("=" * 70)
    print("  ⚾ SABR-MAGIC AI MONITOR: Sintonizando cartelera y conectando IA...")
    print("=" * 70)
    
    game_pk = find_active_or_next_game()
    if not game_pk:
        print("⚠️ No se encontraron partidos programados para hoy.")
        return
        
    try:
        initial_feed = fetch_live_game_feed(game_pk)
        game_data = initial_feed.get("gameData", {})
        venue_name = game_data.get("venue", {}).get("name", "Estadio no especificado")
        stockholm_time = format_time_stockholm(game_data.get("datetime", {}).get("dateTime", ""))
        roster_info = extract_rosters(game_data)
        
        print("\n" + "=" * 70)
        print("🎯 ¡PARTIDO DETECTADO PARA MONITOREO AUTOMÁTICO!")
        print(f"   🏟️  Encuentro: {roster_info['away_team']} @ {roster_info['home_team']}")
        print(f"   📍  Campo / Estadio: {venue_name}")
        print(f"   ⏰  Hora de Inicio (Estocolmo, Suecia): {stockholm_time}")
        print(f"   🆔  Game ID: {game_pk}")
        print("   -------------------------------------------------------------------")
        print(f"   • {roster_info['away_team']} (Abridor: {roster_info['away_probable']})")
        print(f"   • {roster_info['home_team']} (Abridor: {roster_info['home_probable']})")
        print("=" * 70 + "\n")
        
    except Exception as e:
        print(f"⚠️ Aviso al extraer metadatos ({e}), continuando con ID: {game_pk}\n")
    
    last_state_signature = None
    
    try:
        while True:
            try:
                raw_feed = fetch_live_game_feed(game_pk)
                status_abstract = raw_feed.get("gameData", {}).get("status", {}).get("abstractGameState", "Preview")
                status_detailed = raw_feed.get("gameData", {}).get("status", {}).get("detailedState", "Scheduled")
                
                if status_abstract == "Preview":
                    print(f"[{time.strftime('%H:%M:%S')}] ⏳ Esperando inicio ({status_detailed}). Sintonizado para Estocolmo...", end="\r")
                    time.sleep(60)
                    continue
                elif status_abstract == "Final":
                    print(f"\n🏁 El partido ha finalizado ({status_detailed}). Deteniendo monitor.")
                    break
                
                # Ejecutar análisis analítico con nuestro motor
                result = analyze_live_game(game_pk)
                context = result["context"]
                metrics = result["metrics"]
                
                current_signature = (
                    context.get("inning"), context.get("inning_half"),
                    context.get("outs"), context.get("batter", {}).get("count"),
                    context.get("pitch_count")
                )
                
                if current_signature != last_state_signature:
                    print("\n" + "-" * 70)
                    print(f"🕒 [{time.strftime('%H:%M:%S')}] EN VIVO | {context.get('inning_half')} de la {context.get('inning')} | Outs: {context.get('outs')} | Marcador: {context.get('score')}")
                    print(f"   👤 Lanzador: {context.get('pitch_count')} lanzamientos | Bateador: {context.get('batter', {}).get('name')} ({context.get('batter', {}).get('count')})")
                    print(f"   📊 MEI: {metrics['mei']}  |  LI_k: {metrics['leverage_index']}  |  NATE: {metrics['nate']}")
                    print(f"   🚨 ESTADO: {metrics['alert_status']}")
                    print("-" * 70)
                    
                    # Llamar a Gemini (Bench Coach) para obtener recomendación de IA
                    print("🤖 [GEMINI BENCH COACH] Analizando situación táctica...")
                    ai_advice = get_bench_coach_advice(context, metrics)
                    print(f"\n{ai_advice}")
                    print("=" * 70 + "\n")
                    
                    last_state_signature = current_signature
                else:
                    print(f"[{time.strftime('%H:%M:%S')}] Monitoreando jugada actual...", end="\r")
                
            except MLBAPIError as e:
                print(f"\n⚠️ Error de conexión con la API de MLB: {e}")
            except Exception as e:
                print(f"\n⚠️ Error inesperado en el ciclo: {e}")
                
            time.sleep(interval_seconds)
            
    except KeyboardInterrupt:
        print("\n\nMonitor automático detenido por el usuario.")

if __name__ == "__main__":
    start_auto_monitor(interval_seconds=30)