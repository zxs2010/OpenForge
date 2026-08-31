"""Deterministic, explainable matching for the first OpenForge node."""

from __future__ import annotations

from openforge.network import ConnectionStatus, Intent, Match, NetworkNode

_STATUS_WEIGHT = {
    ConnectionStatus.IMPORTED: 0,
    ConnectionStatus.CLAIMED: 5,
    ConnectionStatus.CONNECTED: 12,
    ConnectionStatus.VERIFIED: 20,
}

_KEYWORD_CAPABILITIES: tuple[tuple[tuple[str, ...], str], ...] = (
    (("video", "mtv", "ai mv", "漫剧", "视频", "短片", "电影", "动画", "广告"), "video.generate"),
    (
        ("script", "story", "storyboard", "剧本", "故事", "分镜", "世界观"),
        "script.write",
    ),
    (
        ("music", "song", "soundtrack", "音乐", "歌曲", "配乐", "虚拟歌手"),
        "music.compose",
    ),
    (
        ("podcast", "self-media", "social media", "播客", "自媒体", "图文", "直播"),
        "social.publish",
    ),
    (("subtitle", "字幕"), "subtitle.generate"),
    (("dub", "配音"), "audio.dub"),
    (("localize", "翻译", "本地化"), "video.localize"),
    (("gpu", "compute", "算力"), "compute.provide"),
    (("distribute", "channel", "渠道", "分发", "推广"), "channel.distribute"),
    (
        (
            "launch",
            "openforge",
            "community",
            "create",
            "make",
            "社区",
            "开放",
            "创作",
            "制作",
            "发布",
        ),
        "community.coordinate",
    ),
)


class IntentRouter:
    """Rank nodes by declared capability and connection evidence."""

    def route(
        self, intent: Intent, nodes: tuple[NetworkNode, ...], limit: int = 6
    ) -> tuple[Match, ...]:
        desired = set(intent.desired_capabilities) or set(self.infer_capabilities(intent.summary))
        if not desired:
            desired.add("community.coordinate")

        matches: list[Match] = []
        for node in nodes:
            overlap = desired.intersection(node.capabilities)
            if not overlap:
                continue
            reasons = tuple(sorted(overlap))
            score = len(overlap) * 100 + _STATUS_WEIGHT[node.status]
            matches.append(Match(node=node, score=score, reasons=reasons))
        matches.sort(key=lambda item: (-item.score, item.node.name.casefold(), item.node.id))
        return tuple(matches[:limit])

    def infer_capabilities(self, summary: str) -> tuple[str, ...]:
        lowered = summary.casefold()
        inferred = {
            capability
            for keywords, capability in _KEYWORD_CAPABILITIES
            if any(keyword in lowered for keyword in keywords)
        }
        return tuple(sorted(inferred))
