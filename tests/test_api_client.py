import pytest
from unittest.mock import patch
from api_client import fetch_live_game_feed, extract_game_context, MLBAPIError

@patch("requests.get")
def test_fetch_live_game_feed_success(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"gameData": {}, "liveData": {}}
    
    data = fetch_live_game_feed(718293)
    assert "liveData" in data

def test_extract_game_context_rich():
    sample_feed = {
        "liveData": {
            "linescore": {
                "currentInning": 7,
                "isTopInning": False,
                "outs": 2,
                "teams": {
                    "home": {"runs": 3},
                    "away": {"runs": 4}
                },
                "offense": {
                    "first": {"id": 1},
                    "second": {"id": 2},
                    "third": None
                }
            },
            "plays": {
                "currentPlay": {
                    "matchup": {
                        "batter": {"fullName": "Rafael Devers"},
                        "batSide": {"code": "L"},
                        "pitcher": {"fullName": "Gerrit Cole"},
                        "pitchHand": {"code": "R"}
                    },
                    "count": {
                        "balls": 3,
                        "strikes": 2,
                        "pitches": 6
                    }
                }
            }
        }
    }
    
    context = extract_game_context(sample_feed)
    assert context["inning"] == 7
    assert context["outs"] == 2
    assert context["batter"]["name"] == "Rafael Devers"
    assert context["pitcher"]["name"] == "Gerrit Cole"
    assert context["batter"]["count"] == "3-2"
    assert context["runners_count"] == 2