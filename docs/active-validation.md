# OpenForge Active Validation / 公开验证日志

**Last updated / 最后更新：** 2026-09-01

**Status / 状态：** Active experiment / 真实项目验证中

OpenForge does not count a repository link, a mock request, or one successful
demo as proof of an ecosystem. This log publishes what real projects have
tested, what remains unproven, and what must happen before an experiment becomes
part of the public protocol.

OpenForge 不把一个仓库链接、一次模拟请求或一次成功演示当成生态证明。本日志只
公开真实项目验证了什么、还有什么没有证明，以及一项实验成为公共协议之前必须通过
哪些关口。

## Validation 002: Creative collaboration node / 创作者协作节点

An independent real-world project is defining a private system for coordinating
creative work. Its expected domain includes tasks, progress, artifact review,
acceptance, contribution evidence, and compensation records. Client identity,
personal data, contracts, prices, internal rules, source code, and operating
data remain private.

一个独立的真实项目正在定义私有的创作者协作系统，预期覆盖任务、进度、作品审核、
验收、贡献依据和收益记录。客户身份、个人资料、合同、价格、内部规则、源代码与经营
数据继续保留在独立系统中，不进入 OpenForge 公共仓库。

### Evidence available now / 当前已有证据

- The independent project has entered requirements validation.
- A milestone-triggered, privacy-preserving handshake with the OpenForge
  development activity has completed its first message exchange.
- The node keeps a durable local status record and sends sanitized summaries
  when scope, milestones, blockers, tests, deployment status, or integration
  decisions change.
- Each progress packet separates completed work, next steps, risks, ecosystem
  impact, and decisions requested from OpenForge.

- 独立项目已经进入需求确认阶段。
- 项目与 OpenForge 开发活动之间已经完成第一次里程碑触发、脱敏的握手消息交换。
- 节点保留持久状态记录，并在范围、里程碑、阻塞、测试、部署或接口决策变化时发送
  脱敏摘要。
- 每个进度包分别记录已完成、下一步、风险、生态影响和需要 OpenForge 决定的事项。

### Not yet proven / 尚未证明

- The client has not authorized a public connector or public project details.
- The handshake is not yet a stable, third-party implementable protocol.
- No public capability schema, authentication profile, or transport binding has
  been frozen.
- The node is not labeled `connected` or `verified` in the public network.
- OpenForge does not automate salaries, client payments, contracts, or financial
  settlement through this experiment.

- 客户尚未授权公开连接器或项目细节。
- 当前握手还不是稳定、可由第三方直接实现的公共协议。
- 公共能力声明、身份认证方案和传输绑定尚未定版。
- 该节点不会在公共网络中被标记为 `connected` 或 `verified`。
- 本实验不通过 OpenForge 自动发放工资、收取客户款项、签署合同或完成财务结算。

### Gates before a public handshake draft / 发布握手协议草案前的关口

1. Exercise the handshake through real scope changes, milestones, blockers, and
   acceptance events.
2. Define message identity, acknowledgement, idempotency, retry, ordering, and
   version negotiation.
3. Map sanitized node updates to OpenForge Activity events without copying
   private project state into the public network.
4. Validate the same abstraction with at least one additional independent
   project.
5. Remove local paths, task identifiers, client assumptions, and implementation
   details before publishing `Node Handshake Protocol v0.1`.

1. 用真实的范围变化、里程碑、阻塞和验收事件运行握手。
2. 明确消息身份、确认、幂等、重试、顺序和版本协商。
3. 将脱敏节点更新映射为 OpenForge Activity 事件，同时不复制私有项目状态。
4. 至少再用一个独立项目验证相同抽象。
5. 删除本地路径、任务标识、客户假设和内部实现后，再发布
   `Node Handshake Protocol v0.1`。

## Participate / 参与验证

Developers can help define interoperable event envelopes, acknowledgement and
retry semantics, selective disclosure, and conformance fixtures. Bring a real
independent project if you want to test the boundary rather than merge into one
platform.

开发者可以共同设计可互操作的事件封装、确认与重试语义、选择性披露和一致性测试。
如果你有真实的独立项目，可以在保留自身仓库、许可和商业模式的前提下参与边界验证。

[Join the Founding Builders discussion / 加入首批建设者讨论](https://github.com/zxs2010/OpenForge/discussions/5)
