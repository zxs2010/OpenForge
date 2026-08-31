# OpenForge Founding Builders Call 001

**Help build the open collaboration network for AI-native content.**  
**一起建设面向 AI 原生内容的开放协作网络。**

[中文](#中文招募) · [English](#english-call)

## 中文招募

### 我们正在建设什么

今天，一个独立创作者可能同时需要剧本、视觉、音乐、视频模型、Agent、算力、人工审核和发布渠道，但这些能力分散在不同的人、项目和平台里。

OpenForge 希望建立一套开放连接协议：让一个真实需求进入网络后，能够找到合适的人与 AI，形成可追踪的协作 Activity，调用独立 Provider 完成工作，并留下产物、审核和贡献证据。

```text
真实需求 → 能力匹配 → 协作 Activity → Provider Job → 人工审核 → 作品与贡献凭证
```

OpenForge 不是一个封闭的 AI 工具商店。每个项目保留自己的仓库、许可证、知识产权和商业模式，通过公开契约选择加入或退出。

### 为什么现在加入

V1 已经拥有：

- 面向人类的中英文公开入口；
- 面向 AI 和外部系统的参考 API；
- Node、Intent、Match、Activity 和 Provider Job 基础模型；
- 可解释的能力路由；
- 追加式 Activity 事件；
- 第一个可运行的视频 Provider Adapter；
- Founding Contributor 公开激励与治理成长计划。

但我们不会假装生态已经形成。现在最重要的工作，是连接第一个独立 AI 生产系统，跑通第一条真实任务闭环，再让更多人、AI、工具、算力和渠道加入。

### 第一批共同建设方向

#### Protocol 与 API

- Contribution Receipt JSON Schema；
- Agent、Skill 与 Provider manifest；
- Activity 事件、状态转换与人工审核边界；
- Todo Bridge 任务交换契约；
- Provider estimate、status、result 与 receipt 一致性测试。

#### Agent 与自动化

- OpenForge Coordinator Agent；
- 只领取明确允许 AI 参与的任务；
- 人工门禁、失败恢复和幂等执行；
- Agent 权限、版本、来源与审计记录。

#### 可信记录与安全

- Artifact 哈希、数字签名和验证工具；
- GitHub PR、Issue、Discussion 贡献证据连接器；
- 密钥轮换、撤销、冒名和重复贡献防护；
- 可选的 W3C Verifiable Credentials 导出。

#### Provider 与真实工作流

- AI 剧本、音乐、图片、视频、配音与发布工具 Adapter；
- ComfyUI、OpenMontage、VideoLingo 等候选节点连接；
- 一个独立 AI 漫剧生产系统的首个 Todo Bridge；
- 真实需求、产物、人工审核和公开复盘。

#### 产品、设计与社区

- 双语文档、可访问性与开发者体验；
- 面向创作者的需求入口；
- 真实案例、演示和社区维护；
- 对协议、隐私、许可证与治理的公开评审。

### 谁适合加入

- Go、Python、TypeScript、API、工作流或分布式系统开发者；
- Agent、MCP、Skill、ComfyUI 或 AI 视频工具作者；
- 安全、密码学、身份凭证和开放协议贡献者；
- 设计师、技术写作者、翻译者与社区维护者；
- 有真实创作需求，愿意一起验证流程的人。

你不需要先成为“专家”。能够提出一个可复现问题、完善一个测试、连接一个真实节点、改进一段文档或认真评审一项协议，都是建设网络的一部分。

### 贡献者获得什么

符合公开标准的早期实质贡献可以申请 `OpenForge Founding Contributor · 2026`：

- 永久、公开、可验证的贡献记录；
- 在相关版本、演示与案例中的准确署名；
- Contributor → Reviewer → Maintainer 的公开成长路径；
- 参与 RFC、工作组和匹配真实 Activity 的机会；
- 只有资金已经确认并提前公布规则时才成立的法币赏金；
- 真实项目开始前单独约定的项目报酬。

这不是股权、Token、雇佣、合伙关系、永久分红或未来订单保证。OpenForge 不用模糊的未来财富承诺换取社区免费劳动。

### 如何开始

在 [Founding Builders 招募讨论](https://github.com/zxs2010/OpenForge/discussions/5) 回复：

1. 你是谁，或者你正在建设什么？
2. 你能贡献什么能力？
3. 你最想参与上面的哪一个方向？
4. 你希望通过 OpenForge 完成什么真实结果？

然后阅读：

- [OpenForge README](../README.md)
- [Contributing Guide](../CONTRIBUTING.md)
- [Founding Contributor Program v0.1](founding-contributor-program-v0.1.md)
- [Verifiable Without Blockchain v0.1](verifiable-without-blockchain-v0.1.md)
- [Build Task 001](https://github.com/zxs2010/OpenForge/discussions/2)

请只提交你有权公开的信息。不要发布 API 密钥、私有仓库内容、客户数据、内部 Prompt、合同、报价、未公开漏洞或其他商业机密。

## English call

### What we are building

An independent creator may need writing, visual direction, music, video models, Agents, compute, human review, and distribution—but those capabilities live across disconnected people, projects, and platforms.

OpenForge is building an open connection protocol. A real need should be able to discover compatible people and AI, become a traceable Activity, dispatch portable Provider Jobs, pass human review, and leave verifiable evidence of artifacts and contribution.

```text
Real need → capability match → Activity → Provider Job → human review → artifact + contribution receipt
```

OpenForge is not a closed AI-tool marketplace. Independent projects retain their repositories, licenses, intellectual property, and business models, and connect through public contracts.

### Why join now

V1 already includes a bilingual public entrance, a reference API, Node/Intent/Match/Activity/Job models, explainable routing, append-only Activity events, a working video Provider adapter, and a public Founding Contributor program.

We will not pretend the ecosystem already exists. The immediate milestone is to connect the first independent AI production system, complete one real work loop, and make it possible for more people, AI systems, tools, compute providers, and channels to join.

### First build areas

- Contribution Receipt JSON Schema;
- Agent, Skill, and Provider manifests;
- Activity events, transitions, and human approval boundaries;
- a Todo Bridge contract and Coordinator Agent;
- Provider conformance tests;
- artifact hashing, signing, and verification;
- GitHub contribution-evidence connectors;
- privacy, revocation, key rotation, and impersonation defense;
- optional W3C Verifiable Credentials export;
- adapters for AI writing, music, image, video, dubbing, and distribution tools;
- bilingual docs, accessibility, developer experience, and community review.

### Who should join

We welcome Go, Python, TypeScript, API, workflow, and distributed-systems developers; Agent, MCP, Skill, ComfyUI, and AI-video builders; security and identity contributors; designers, technical writers, translators, community maintainers; and creators with a real need to test.

You do not need to arrive as an expert. A reproducible issue, a stronger test, a real node connection, a documentation improvement, or a careful protocol review can be a substantial contribution.

### What contributors receive

Qualifying early work may apply for `OpenForge Founding Contributor · 2026` recognition: a permanent verifiable record, accurate attribution, a Contributor → Reviewer → Maintainer path, participation in public RFCs and working groups, funded fiat bounties only when confirmed in advance, and separately agreed compensation for real Activities.

This is not equity, a Token, employment, partnership, permanent revenue, or guaranteed future work. OpenForge will not exchange vague promises of future wealth for unpaid community labor.

### Start here

Reply to the [Founding Builders discussion](https://github.com/zxs2010/OpenForge/discussions/5) with:

1. Who are you, or what are you building?
2. What capability can you contribute?
3. Which build area interests you most?
4. What real outcome would you like to make through OpenForge?

Then read the [README](../README.md), [Contributing Guide](../CONTRIBUTING.md), [Founding Contributor Program](founding-contributor-program-v0.1.md), [technical position](verifiable-without-blockchain-v0.1.md), and [Build Task 001](https://github.com/zxs2010/OpenForge/discussions/2).

Share only information you are authorized to make public. Never post API keys, private-repository content, customer data, internal prompts, contracts, pricing, undisclosed vulnerabilities, or other confidential information.
