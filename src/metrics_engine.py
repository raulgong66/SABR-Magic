def calculate_mei(pitch_count: int) -> float:
    """
    Calculates Allostatic Stress (MEI) based on pitch count with an
    exponential wear curve kick-in after pitch 75.
    """
    if pitch_count <= 75:
        return round(pitch_count * 0.0015, 3)
    else:
        # Exponential wear curve past threshold
        excess = pitch_count - 75
        base_mei = 75 * 0.0015
        wear_factor = excess * 0.0035 * (1 + (excess / 50))
        return round(base_mei + wear_factor, 3)

def calculate_li(inning: int, outs: int, runners_count: int) -> float:
    """
    Calculates Leverage Index (LI_k) based on situational context
    (inning, outs, and base runners).
    """
    base_weight = 1.0
    if inning >= 7:
        base_weight += 0.5
    
    runner_multiplier = 1.0 + (runners_count * 0.4)
    out_modifier = 0.8 if outs == 2 else 1.0
    
    li = base_weight * runner_multiplier * out_modifier
    return round(max(0.5, li), 2)

def calculate_nate(delta_woba_post_error: float, woba_baseline: float, li_k: float, dugout_momentum_factor: float = 0.0) -> float:
    """
    Calculates NATE (Next After the Error):
    Quantifies immediate offensive damage in the subsequent 2 plate appearances following an error.
    
    Formula:
    NATE = [ (ΔwOBA_post-error - wOBA_baseline) / LI_k ] × (1 + Dugout Momentum Factor)
    """
    if li_k <= 0:
        li_k = 1.0  # Prevent division by zero
        
    nate_value = ((delta_woba_post_error - wOBA_baseline) / li_k) * (1.0 + dugout_momentum_factor)
    return round(nate_value, 4)

def evaluate_alert(mei_value: float, nate_value: float = 0.0) -> str:
    """
    Evaluates alert status based on MEI and NATE synergy.
    Triggers mandatory bullpen intervention if MEI > 3.0 and NATE indicates high vulnerability.
    """
    if mei_value > 3.0 and nate_value > 0.05:
        return "CRITICAL: Mandatory Bullpen Intervention (MEI > 3.0 + High NATE Synergy)"
    elif mei_value > 0.300:
        return "CRITICAL: High Allostatic Stress"
    elif mei_value > 0.150:
        return "WARNING: Moderate Fatigue"
    else:
        return "OPTIMAL: Pitcher Stable"