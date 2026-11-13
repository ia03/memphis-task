import json

from scripts.check_trials import problems


def make(tmp_path, seconds, exception=None):
    trial = tmp_path / "r0-s10" / "r0-s10-hinted__abc"
    (trial / "verifier").mkdir(parents=True)
    (trial / "artifacts" / "out").mkdir(parents=True)
    (trial / "result.json").write_text(json.dumps({"exception_info": exception}))
    (trial / "verifier" / "score.json").write_text("{}")
    (trial / "artifacts" / "out" / "simulator.jsonl").write_text("".join(json.dumps({"seconds": s}) + "\n" for s in seconds))
    return trial


def test_healthy_trial_is_valid(tmp_path):
    assert problems(make(tmp_path, [40, 90, 352])) == []


def test_stalled_world_voids_the_trial(tmp_path):
    assert problems(make(tmp_path, [40, 1319])) == ["the world stalled 22 min on one simulator call"]


def test_agent_error_voids_the_trial(tmp_path):
    found = problems(make(tmp_path, [40], {"exception_type": "AgentTimeoutError"}))
    assert found == ["agent run ended with AgentTimeoutError"]
