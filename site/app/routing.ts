export type Connection = "imported" | "claimed" | "connected" | "verified";

export type RouteNode = {
  id: string;
  name: string;
  capabilities: string[];
  connection: Connection;
};

export type RoutedMatch<T extends RouteNode = RouteNode> = {
  node: T;
  score: number;
  reasons: string[];
};

const statusWeight: Record<Connection, number> = {
  imported: 0,
  claimed: 5,
  connected: 12,
  verified: 20,
};

const keywordCapabilities: ReadonlyArray<readonly [readonly string[], string]> = [
  [["video", "mtv", "ai mv", "漫剧", "视频", "短片", "电影", "动画", "广告"], "video.generate"],
  [["script", "story", "storyboard", "剧本", "故事", "分镜", "世界观"], "script.write"],
  [["music", "song", "soundtrack", "音乐", "歌曲", "配乐", "虚拟歌手"], "music.compose"],
  [["podcast", "self-media", "social media", "播客", "自媒体", "图文", "直播"], "social.publish"],
  [["subtitle", "字幕"], "subtitle.generate"],
  [["dub", "配音"], "audio.dub"],
  [["localize", "翻译", "本地化"], "video.localize"],
  [["gpu", "compute", "算力"], "compute.provide"],
  [["distribute", "channel", "渠道", "分发", "推广"], "channel.distribute"],
  [["launch", "openforge", "community", "create", "make", "社区", "开放", "创作", "制作", "发布"], "community.coordinate"],
];

export function inferCapabilities(summary: string): string[] {
  const lowered = summary.toLocaleLowerCase("en");
  return keywordCapabilities
    .filter(([keywords]) => keywords.some((keyword) => lowered.includes(keyword)))
    .map(([, capability]) => capability)
    .sort();
}

export function routeNodes<T extends RouteNode>(
  nodes: T[],
  desiredCapabilities: string[],
  limit = 6,
): RoutedMatch<T>[] {
  const desired = new Set(
    desiredCapabilities.length ? desiredCapabilities : ["community.coordinate"],
  );
  return nodes
    .map((node) => {
      const reasons = [...new Set(node.capabilities.filter((capability) => desired.has(capability)))].sort();
      return {
        node,
        reasons,
        score: reasons.length * 100 + statusWeight[node.connection],
      };
    })
    .filter((match) => match.reasons.length > 0)
    .sort(
      (a, b) =>
        b.score - a.score ||
        a.node.name.toLocaleLowerCase("en").localeCompare(b.node.name.toLocaleLowerCase("en")) ||
        a.node.id.localeCompare(b.node.id),
    )
    .slice(0, limit);
}
