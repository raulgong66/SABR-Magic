import pytest
from metrics_engine import calculate_mei, calculate_li, evaluate_alert

def test_calculate_mei_early():
    """Test MEI calculation for low pitch counts."""
    assert calculate_mei(0) == 0.075
    assert calculate_mei(50) == 0.150

def test_calculate_mei_wear():
    """Test exponential wear curve kick-in after pitch 75."""
    mei_normal = calculate_mei(75)
    mei_heavy = calculate_mei(100)
    assert mei_heavy > mei_normal

def test_calculate_li_situational():
    """Test leverage index calculations under different scenarios."""
    # Early inning, low stress (baseline 1.0)
    li_early = calculate_li(inning=3, outs=1, runners_count=0)
    assert li_early == 1.0

    # Late inning, bases loaded, 2 outs (high leverage)
    li_late = calculate_li(inning=9, outs=2, runners_count=3)
    assert li_late > 2.0

def test_evaluate_alert_levels():
    """Test alert status thresholds."""
    assert "OPTIMAL" in evaluate_alert(0.100)
    assert "CRITICAL" in evaluate_alert(0.380)