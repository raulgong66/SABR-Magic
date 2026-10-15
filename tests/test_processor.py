import pytest
from unittest.mock import patch
from processor import analyze_live_game

@patch("processor.fetch_live_game_feed")
def test_analyze_live_game_pipeline_dual_metrics(mock_fetch):
    """Test that the pipeline computes both MEI and NATE successfully."""
    mock_fetch.return_value = {
        "liveData": {
            "linescore": {
                "currentInning": 7,
                "outs": 1,
                "offense": {
                    "first": {"id": 10},
                    "second": None,
                    "third": None
                }
            }
        }
    }

    result = analyze_live_game(718293)
    
    assert result["game_pk"] == 718293
    metrics = result["metrics"]
    
    # Verify both core metrics are computed
    assert "mei" in metrics
    assert "nate" in metrics
    assert "leverage_index" in metrics
    assert "alert_status" in metrics
    assert isinstance(metrics["mei"], float)
    assert isinstance(metrics["nate"], float)