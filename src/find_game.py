import urllib.request
import json

def search_playoff_games():
    # Buscamos en el rango de octubre (mes de postemporada / NLCS)
    url = "https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-01&endDate=2026-10-31&gameTypes=F,D,L,W"
    
    print("🔍 Consultando el calendario oficial de postemporada en la MLB StatsAPI...")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            dates = data.get('dates', [])
            
            found = False
            for d in dates:
                date_str = d.get('date')
                games = d.get('games', [])
                for g in games:
                    game_pk = g.get('gamePk')
                    teams = g.get('teams', {})
                    away = teams.get('away', {}).get('team', {}).get('name', 'Visitor')
                    home = teams.get('home', {}).get('team', {}).get('name', 'Home')
                    game_type = g.get('gameType') # L = League Championship Series (NLCS/ALCS)
                    
                    # Filtramos o listamos los juegos de postemporada
                    print(f"Fecha: {date_str} | GamePk: {game_pk} | Tipo: {game_type} | {away} @ {home}")
                    found = True
            
            if not found:
                print("ℹ️ No se encontraron partidos con esos filtros. Probemos buscando por temporada general...")
                
    except Exception as e:
        print(f"❌ Error al consultar el calendario: {e}")

if __name__ == "__main__":
    search_playoff_games()