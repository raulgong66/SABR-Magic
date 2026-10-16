import os
import sys

sys.path.append(os.path.abspath("src"))

from processor import fetch_live_game_data, extract_play_context, calculate_mei, calculate_nate
from ai_advisor import get_bench_coach_advice

GAME_PK = "849810"

def run_step_by_step_simulation():
    print("=" * 70)
    print(f"⚾ SIMULADOR PASO A PASO REAL (MLB StatsAPI Game PK {GAME_PK})")
    print("=" * 70)

    raw_data = fetch_live_game_data(GAME_PK)
    if not raw_data:
        print("❌ No se pudieron descargar los datos de la MLB StatsAPI.")
        return

    all_plays = raw_data.get('liveData', {}).get('plays', {}).get('allPlays', [])
    if not all_plays:
        print("❌ No se encontraron jugadas registradas en el feed de este partido.")
        return

    print(f"✅ Se cargaron {len(all_plays)} jugadas reales del partido {GAME_PK}.\n")

    for idx, play in enumerate(all_plays):
        context = extract_play_context(play, all_plays)
        
        mei = calculate_mei(context['pitcher'], context)
        sabermetrics = calculate_nate(context, {"mei": mei})

        p_info = context['pitcher']
        b_info = context['batter']

        print("-" * 70)
        print(f"📍 JUGADA #{idx + 1} (At-Bat Index: {context['at_bat_index']})")
        print(f"• Entrada: {context['inning_half']} de la {context['inning']}a | {context['outs']} Outs")
        print(f"• Enfrentamiento: 🤼‍♂️ {p_info['name']} vs 🏏 {b_info['name']}")
        print(f"• Pitcheos Acumulados del Lanzador: {p_info['total_pitches']}")
        print(f"• Conteo del Turno: {b_info['count']} | Corredores en Base: {context['runners_count']}")
        print(f"• Resultado: {context['result']}")
        
        print(f"\n📊 MÉTRICAS SABERMÉTRICAS:")
        print(f"• MEI (Estrés Lanzador): {sabermetrics['mei']} | LI_k: {sabermetrics['leverage_index']} | NATE: {sabermetrics['nate']}")
        print(f"• Estado de Alerta: {sabermetrics['alert_status']}")

        print("\n🤖 [BENCH COACH AI ADVICE]:")
        advice = get_bench_coach_advice(context, sabermetrics)
        print(advice)
        print("-" * 70)

        try:
            user_input = input("\n👉 Presiona [ENTER] para avanzar al siguiente at-bat (o 'q' para salir): ")
            if user_input.lower() == 'q':
                print("🛑 Simulación finalizada por el usuario.")
                break
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    run_step_by_step_simulation()