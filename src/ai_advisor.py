import os
from google import genai
from google.genai import errors

def get_bench_coach_advice(context: dict, sabermetrics: dict) -> str:
    """
    Genera un consejo táctico de Bench Coach de MLB de nivel avanzado,
    específicamente calibrado según el estrés (MEI) y la tensión (NATE/LI_k).
    """
    # Inicializamos el cliente de GenAI usando las credenciales del entorno
    client = genai.Client()
    
    p_info = context.get('pitcher', {})
    b_info = context.get('batter', {})
    
    pitcher_name = p_info.get('name', 'Lanzador')
    total_pitches = p_info.get('total_pitches', 0)
    batter_name = b_info.get('name', 'Bateador')
    count = b_info.get('count', '0-0')
    
    inning = context.get('inning', 1)
    inning_half = context.get('inning_half', 'Top')
    outs = context.get('outs', 0)
    runners = context.get('runners_count', 0)
    
    mei = sabermetrics.get('mei', 1.0)
    li = sabermetrics.get('leverage_index', 1.0)
    nate = sabermetrics.get('nate', 1.0)
    alert = sabermetrics.get('alert_status', 'NORMAL')

    prompt = f""\"
    Actúa como un Manager y Bench Coach de Grandes Ligas experto en analítica avanzada y sabermetría en plena Serie de Campeonato (NLCS). 
    Tienes que tomar decisiones críticas inmediatas basadas en los siguientes datos en vivo:

    - SITUACIÓN: {inning_half} del inning {inning} | {outs} Outs | Corredores en base: {runners}
    - LANZADOR ACTUAL: {pitcher_name} | Pitcheos acumulados: {total_pitches}
    - BATEADOR EN TURNO: {batter_name} | Conteo: {count}
    - MÉTRICAS: MEI (Estrés) = {mei} | LI_k (Apalancamiento) = {li} | NATE (Tensión) = {nate}
    - ESTADO DE ALERTA: {alert}

    Instrucciones estrictas para tu respuesta:
    1. Si el MEI es alto (>2.5) o la alerta es roja, NO des consejos genéricos. Ordena acciones específicas: ¿Quién debe calentar en el bullpen de inmediato (zurdos/diestros)?, ¿Cuál es la estrategia exacta de ubicación con este bateador para evitar daño?
    2. Mantén un tono de jerga de béisbol profesional de Grandes Ligas (conciso, urgente, analítico).
    3. Estructura tu respuesta en 3 viñetas cortas y contundentes:
       - 🚨 **Diagnóstico del Peligro** (Por qué el lanzador está al límite o la situación es crítica).
       - 🎯 **Plan de Pitcheo Inmediato** (Zona, tipo de lanzamiento o planteamiento al bateador).
       - 📞 **Orden al Bullpen** (Quién calienta o si se mantiene al lanzador).
    ""\"

    try:
        # Usamos el modelo estándar de Gemini disponible en el SDK oficial
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text.strip()
    except Exception as e:
        return f"⚠️ [Aviso del Sistema]: No se pudo conectar con el Bench Coach de IA ({e}). Mantener plan de juego conservador."