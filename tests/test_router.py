from __future__ import annotations

import pytest
from openforge.router import IntentRouter


@pytest.mark.parametrize(
    ("summary", "expected"),
    [
        (
            "Create an AI music video with an original song",
            ("community.coordinate", "music.compose", "video.generate"),
        ),
        ("写一个漫剧剧本和分镜", ("script.write", "video.generate")),
        ("制作一档自媒体播客", ("community.coordinate", "social.publish")),
    ],
)
def test_infers_open_content_capabilities(
    summary: str, expected: tuple[str, ...]
) -> None:
    assert IntentRouter().infer_capabilities(summary) == expected
