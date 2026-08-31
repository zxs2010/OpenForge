# Verifiable Without Blockchain v0.1

**OpenForge technical position / OpenForge 技术立场**  
**Published:** 2026-08-31  
**Languages:** [中文](#中文) · [English](#english)

## 中文

### 结论

OpenForge V1 不需要区块链，也不会发行 OpenForge Token。

**贡献可验证，不等于必须上链；开发者获得收益，也不等于必须发行 Token。**

OpenForge 要解决的核心问题是：一个真实需求如何找到合适的人、AI、项目、工具、算力与渠道，如何形成可追踪的协作活动，以及如何留下可信的贡献和交付证据。这些目标可以使用开放协议、标准密码学和普通互联网基础设施实现。

### V1 使用什么

- **GitHub PR、Issue 与 Discussions：** 证明谁提出、讨论、评审和完成了什么；
- **OpenForge Activity：** 记录参与者、任务、进展、人工审核与产物；
- **追加式事件日志：** 新事件可以继续追加，已有历史不能被悄悄覆盖；
- **文件哈希与数字签名：** 验证贡献凭证、请求和作品是否被修改；
- **Provider receipt：** 记录任务状态、产物、来源和已知成本；
- **法币赏金与项目结算：** 使用事前确认的任务条款、合同和正常支付渠道；
- **公开贡献者账本：** 让贡献、署名与治理资格能够被检查和引用。

V1 的第一项可信记录，不是金融资产，而是一个可以被人和机器验证的 **Contribution Receipt（贡献凭证）**。

### 贡献凭证应该记录什么

```json
{
  "receipt_version": "0.1",
  "contributor": "github:zxs2010",
  "activity_id": "activity:001",
  "contribution_type": "protocol.review",
  "evidence": [
    "https://github.com/zxs2010/OpenForge/pull/123"
  ],
  "artifact_sha256": "…",
  "accepted_at": "2026-08-31T12:00:00Z",
  "accepted_by": ["github:reviewer"],
  "signature": "…"
}
```

这个结构只是公开协议示例，不包含个人隐私、客户数据、私有代码、合同、报价或内部商业信息。

### 可携带证书也不需要区块链

如果未来贡献者需要把身份和贡献带到其他社区，OpenForge 可以支持 [W3C Verifiable Credentials Data Model 2.0](https://www.w3.org/TR/vc-data-model-2.0/)：由可信发行者签发、贡献者持有、其他平台验证。W3C 标准提供密码学安全、隐私保护和机器可验证的数据模型，并不要求使用区块链。

### 什么时候才重新考虑区块链

只有以下条件同时成为真实需求时，OpenForge 才会公开重新评估区块链或其他分布式账本：

1. 网络中存在大量互不信任、又必须共同写入记录的独立组织；
2. 参与者有证据表明不能接受 OpenForge、GitHub或其他明确发行者保存记录；
3. 确实需要跨平台自动清算数字资产，而不是普通法币支付；
4. 钱包、密钥恢复、隐私、交易费用、不可逆错误和适用合规成本都能被接受；
5. 区块链方案比签名数据库、透明日志或联邦协议提供了可测量的额外价值。

如果未来只需要更强的公开时间证明，可以选择把一批贡献记录的 Merkle Root 或哈希摘要作为可选外部存证。原始代码、个人信息、客户数据和项目素材永远不应直接写入公共链。

### 为什么 V1 不发行 Token

OpenForge 不使用“现在贡献、以后换币”“贡献积分未来升值”或“永久享受平台流水分红”吸引开发者。

这类承诺会把开放协作变成不透明的金融预期，并带来钱包安全、资产托管、税务、消费者保护、证券和虚拟货币监管等问题。中国人民银行等十部门明确指出，虚拟货币不具有与法定货币等同的法律地位，并对相关交易炒作风险作出严格规定。[中国人民银行：银发〔2021〕237号](https://www.pbc.gov.cn/tiaofasi/144941/3581332/4348658/index.html)

其他司法辖区同样需要具体判断。美国 SEC 的公开说明指出，即使某种加密资产本身不是证券，当发行安排包含投入资金、共同事业、利润预期以及对他人关键管理努力的依赖时，相关交易仍可能构成投资合同。[SEC：Transactions Involving Crypto Assets](https://www.sec.gov/resources-small-businesses/capital-raising-building-blocks/transactions-involving-crypto-assets)

OpenForge V1 的激励方式是：公开贡献记录、治理成长路径、资金已经确认的法币赏金，以及真实 Activity 开始前单独约定的项目报酬。详见 [Founding Contributor Program v0.1](founding-contributor-program-v0.1.md)。

### 开发者现在可以建设什么

我们欢迎社区围绕以下普通、开放、可测试的技术共同建设：

- Contribution Receipt JSON Schema；
- Activity 追加式事件与状态转换；
- Artifact 哈希、签名和验证工具；
- GitHub PR、Issue、Discussion 证据连接器；
- Provider estimate、status、result 与 receipt 一致性测试；
- W3C Verifiable Credentials 的可选导出原型；
- 隐私、撤销、密钥轮换、冒名与重复贡献防护；
- 人类审核、利益冲突和贡献归属的公开规则。

所有实现都应保持可替换、可导出、可独立验证，不把 OpenForge 变成唯一可信中心。

### 我们的方向

> 协议开放、节点独立、贡献可验证、结算透明——但底层不必区块链化。

OpenForge 的开放性来自任何人和系统都能使用同一套公开契约参与、退出和验证，而不是来自某一种特定数据库技术。

## English

### Position

OpenForge V1 does not require a blockchain and will not issue an OpenForge Token.

**Verifiable contribution does not require on-chain storage. Developer compensation does not require a Token.**

OpenForge coordinates real needs across people, AI systems, projects, tools, compute, and channels. The engineering problem is to make participation, progress, artifacts, review, and contribution evidence portable and auditable. Open protocols, standard cryptography, and ordinary Internet infrastructure can meet that goal.

### What V1 uses

- GitHub pull requests, issues, and discussions as public collaboration evidence;
- OpenForge Activities for participants, work, progress, human review, and artifacts;
- append-only events so history cannot be silently overwritten;
- hashes and digital signatures for tamper evidence;
- Provider receipts for state, artifacts, provenance, and known cost;
- fiat bounties and project compensation with terms confirmed before work;
- a public contributor ledger for attribution and governance evidence.

The first trustworthy OpenForge record is not a financial asset. It is a machine-verifiable **Contribution Receipt**.

### Portable credentials do not require a blockchain

If contributors later need portable credentials, OpenForge can support the [W3C Verifiable Credentials Data Model 2.0](https://www.w3.org/TR/vc-data-model-2.0/). It provides a cryptographically secure, privacy-respecting, machine-verifiable data model in which an issuer signs, a holder presents, and a verifier checks a credential. The standard does not require a blockchain.

### When we would reconsider

OpenForge will publicly reconsider blockchain or another distributed ledger only if all of the following become real, evidenced requirements:

1. many mutually distrustful organizations must write to a shared record;
2. participants cannot accept OpenForge, GitHub, or another explicit issuer as the record keeper;
3. cross-platform digital-asset settlement is genuinely required instead of fiat payment;
4. wallet recovery, privacy, fees, irreversible errors, and applicable compliance costs are acceptable; and
5. the design provides measurable value beyond signed databases, transparency logs, or federation.

If stronger public timestamp evidence is ever needed, a batch Merkle root or digest could be anchored externally as an optional mechanism. Source code, personal information, customer data, and project assets must not be written directly to a public chain.

### Why V1 has no Token

OpenForge will not recruit developers with claims that contribution points will later become Tokens, appreciate in value, or provide permanent platform revenue.

Such promises create financial expectations and substantial wallet, custody, tax, consumer-protection, securities, and virtual-currency compliance risks. China has strict rules for virtual-currency-related activity, and other jurisdictions apply their own tests to crypto-asset arrangements. See the official [People's Bank of China notice](https://www.pbc.gov.cn/tiaofasi/144941/3581332/4348658/index.html) and the [U.S. SEC explanation](https://www.sec.gov/resources-small-businesses/capital-raising-building-blocks/transactions-involving-crypto-assets).

OpenForge V1 instead uses public attribution, a governance growth path, fiat bounties only when funding is confirmed, and separately agreed compensation for real Activities. See the [Founding Contributor Program v0.1](founding-contributor-program-v0.1.md).

### What developers can build now

Community contributions are welcome around:

- a Contribution Receipt JSON Schema;
- append-only Activity events and state transitions;
- artifact hashing, signing, and verification tools;
- GitHub PR, Issue, and Discussion evidence connectors;
- Provider estimate, status, result, and receipt conformance tests;
- an optional W3C Verifiable Credentials export prototype;
- privacy, revocation, key rotation, impersonation, and duplicate-contribution defenses;
- public rules for human review, conflicts of interest, and attribution.

Implementations should remain replaceable, exportable, and independently verifiable. OpenForge must not become the only party capable of checking the evidence.

### Direction

> Open protocol. Independent nodes. Verifiable contributions. Transparent settlement. No blockchain required.

OpenForge is open because any person or system can participate, leave, and verify work through the same public contract—not because it chooses one particular database technology.
