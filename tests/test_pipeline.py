from app import run_pipeline


def test_pipeline_generates_outputs():
    result = run_pipeline("校园悬疑，主角收到未来邮件", 1)

    assert result["story_setting"]["genre"] == "校园悬疑"
    assert len(result["world_states"]) == 2
    assert len(result["events"]) == 1
    assert len(result["scenes"]) == 1
    assert len(result["image_prompts"]) == 1

