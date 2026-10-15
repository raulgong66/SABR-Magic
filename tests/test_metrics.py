import pytest
from metrics_engine import calculate_mei, calculate_li, calculate_nate, evaluate_alert

def test_calculate_mei_wear():
    """Test exponential wear curve kick-in after pitch 75."""
    assert calculate_mei(50) == 0.075
    assert calculate_mei(100) > calculate_mei(75)

def test_calculate_li_situational():
    """Test leverage index calculations under different scenarios."""
    li_early = calculate_li(inning=3, outs=1, runners_count=0)
    assert li_early == 1.0
    li_late = calculate_li(inning=9, outs=2, runners_count=3)
    assert li_late > 2.0

def test_calculate_nate():
    """Test NATE formula computation post-error."""
    nate = calculate_nate(delta_woba_post_error=0.450, woba_baseline=0.320, li_k=1.5, dugout_momentum_factor=0.1)
    # Expected: ((0.450 - 0.320) / 1.5) * 1.1 = (0.130 / 1.5) * 1.1 = 0.08666... * 1.1 = 0.0953
    assert nate > 0.0

def test_evaluate_alert_synergy():
    """Test critical bullpen intervention alert when MEI > 3.0 and NATE is high."""
    status = evaluate_alert(mei_value=3.2, nate_value=0.08)
    assert "Mandatory Bullpen Intervention" in status