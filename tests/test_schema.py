from dataclasses import asdict

from schemas.story_setting import StorySetting


def test_story_setting_dataclass():
    setting = StorySetting(
        genre="校园悬疑",
        theme="未知系统",
        initial_location="大学宿舍",
        initial_time="深夜",
        core_incident="收到未来邮件",
    )

    data = asdict(setting)

    assert data["genre"] == "校园悬疑"
    assert data["tone"] == []

