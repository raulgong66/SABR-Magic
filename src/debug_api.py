import urllib.request
import json

game_pk = "780546"
url = f"https://statsapi.mlb.com/api/v1.1/game/{game_pk}/feed/live"

print(f"🔍 Consultando la API de la MLB para el juego PK: {game_pk}...")

req = urllib.request.Request(
    url, 
    headers={'User-Agent': 'Mozilla/5.0'}
)

try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        
        live_data = data.get('liveData', {})
        linescore = live_data.get('linescore', {})
        plays = live_data.get('plays', {})
        current_play = plays.get('currentPlay', {})
        matchup = current_play.get('matchup', {})
        
        pitcher = matchup.get('pitcher', {})
        print("\n--- ⚾ DATOS DEL LANZADOR EN EL MATCHUP ---")
        print(json.dumps(pitcher, indent=2))
        
        print("\n--- 🏏 DATOS DEL BATEADOR ---")
        print(json.dumps(matchup.get('batter', {}), indent=2))
        
        print("\n--- 📋 EVENTOS DEL TURNO ACTUAL (playEvents) ---")
        events = current_play.get('playEvents', [])
        print(f"Total de eventos en este turno: {len(events)}")
        for i, ev in enumerate(events):
            print(f"  Evento {i}: tipo={ev.get('details', {}).get('type', {}).get('description')}, esPitcheo={ev.get('isPitch', False)}")

except Exception as e:
    print(f"❌ Error al conectar con la API: {e}")