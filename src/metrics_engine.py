import math

def calculate_mei(pitches: int, base_mei: float = 0.075) -> float:
    """
    Calculates the Allostatic Stress Index (MEI) based on cumulative pitch count.
    Applies an exponential allostatic wear curve starting after pitch 75.
    """
    if pitches <= 75:
        mei = base_mei + (pitches * 0.0015)
    else:
        mei = base_mei + (75 * 0.0015) + (math.pow(pitches - 75, 1.45) * 0.008)
    return round(mei, 3)

def calculate_li(inning: int, outs: int, runners_count: int) -> float:
    """
    Calculates the situational Leverage Index (LI) in real time.
    """
    base_li = 1.0
    # Tension increases progressively starting from the 7th inning
    inning_factor = 1.0 if inning < 7 else 1.25 + (inning - 7) * 0.15
    runners_factor = 1.0 + (runners_count * 0.45)
    outs_factor = 1.2 if outs == 2 else (1.1 if outs == 0 else 1.0)
    
    return round(base_li * inning_factor * runners_factor * outs_factor, 2)

def evaluate_alert(mei: float) -> str:
    """
    Evaluates the neurocognitive threshold and returns the tactical alert level.
    """
    if mei >= 0.350:
        return "CRITICAL: ALLOSTATED SATURATION (EXTREME RED ZONE) - IMMEDIATE PULL"
    elif mei >= 0.300:
        return "WARNING: SEVERE RED ZONE - READY BULLPEN"
    elif mei >= 0.200:
        return "MODERATE: MONITOR RELEASE POINT"
    else:
        return "OPTIMAL: FRESH PITCHER"
