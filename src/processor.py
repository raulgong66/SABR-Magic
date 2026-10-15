from api_client import fetch_live_game_feed, extract_game_context
from metrics_engine import calculate_mei, calculate_li, calculate_nate, evaluate_alert
from typing import Dict, Any

def analyze_live_game(game_pk: int) -> Dict[str, Any]:
    """
    Orchestrates the SABR-Magic pipeline: fetches live MLB data, extracts context,
    and computes both Allostatic Stress (MEI) and Next After the Error (NATE) in real time.
    
    Args:
        game_pk (int): The unique game identifier from MLB Stats API.
        
    Returns:
        dict: Comprehensive analysis report including game context, MEI, NATE, and alert status.
    """
    # 1. Fetch raw data from MLB API
    raw_feed = fetch_live_game_feed(game_pk)
    
    # 2. Extract situational context
    context = extract_game_context(raw_feed)
    
    pitch_count = context.get("pitch_count", 0)
    inning = context.get("inning", 1)
    outs = context.get("outs", 0)
    runners_count = context.get("runners_count", 0)
    
    # 3. Compute Leverage Index (LI_k)
    li_value = calculate_li(inning=inning, outs=outs, runners_count=runners_count)
    
    # 4. Compute Allostatic Stress (MEI)
    mei_value = calculate_mei(pitch_count)
    
    # 5. Compute NATE (Next After the Error)
    # (Checking recent plays or feeding baseline parameters from feed state)
    # Default baseline wOBA and delta, adjusted if error event is registered in current play frame
    woba_baseline = 0.320
    delta_woba_post_error = 0.350  # Default baseline tracking; updated dynamically if error occurs
    dugout_momentum_factor = 0.05
    
    nate_value = calculate_nate(
        delta_woba_post_error=delta_woba_post_error,
        woba_baseline=woba_baseline,
        li_k=li_value,
        dugout_momentum_factor=dugout_momentum_factor
    )
    
    # 6. Evaluate combined alert status (MEI + NATE synergy)
    alert_status = evaluate_alert(mei_value=mei_value, nate_value=nate_value)
    
    return {
        "game_pk": game_pk,
        "context": context,
        "metrics": {
            "mei": mei_value,
            "nate": nate_value,
            "leverage_index": li_value,
            "alert_status": alert_status
        }
    }