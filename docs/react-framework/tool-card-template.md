# Tool Card 模板

资料来源：[AgentGuide/examples/tool-card-template.md](https://github.com/adongwanai/AgentGuide/blob/main/examples/tool-card-template.md)

## 阅读目标

一个好工具不是“能被调用”就够了，而是要让模型知道什么时候该用、怎么用、失败后怎么恢复，以及哪些场景不能用。

这个模板适合用于 ReAct、workflow agent 或其他 tool calling 系统中的工具说明。

## 名词解释

| 名词 | 解释 | 简单例子 |
|---|---|---|
| Tool Card | 面向模型和工程维护者的工具说明卡，描述用途、边界、输入输出、错误和安全要求。 | `search_papers` 的用途、参数、错误码和调用示例。 |
| Use When | 工具适用条件，告诉模型什么时候应该选择它。 | 用户需要查找论文元数据时使用。 |
| Do Not Use When | 工具不适用条件，减少误调用。 | 用户要求只基于已上传 PDF 回答时不要搜索外部论文。 |
| Input Schema | 工具入参结构和约束。 | `query` 必填，`max_results` 默认 5、最大 20。 |
| Output Schema | 工具返回结构，便于模型理解 observation。 | 返回 `items`、`next_page_token` 和数据来源。 |
| Permission Tier | 工具权限等级，用于区分只读、写入、高风险动作。 | 搜索论文是只读；付款、删除、发消息属于高风险。 |

## 1. 模板

````markdown
## Tool: search_papers

**Purpose**: 按关键词搜索论文元数据，返回标题、摘要、作者、年份、链接和引用信息。

**Use When**:
- 用户需要查找某个主题的代表论文。
- Agent 需要为答案补充可引用证据。
- 需要比较不同方法的提出时间和核心贡献。

**Do Not Use When**:
- 用户已经给了具体 PDF，并要求只基于该 PDF 回答。
- 问题需要网页实时信息而不是学术论文。

**Input Schema**:

```json
{
  "query": "string, required",
  "year_from": "integer, optional",
  "year_to": "integer, optional",
  "max_results": "integer, default 5, max 20"
}
```

**Output Schema**:

```json
{
  "ok": true,
  "items": [
    {
      "title": "string",
      "authors": ["string"],
      "year": 2025,
      "abstract": "string, truncated to 800 chars",
      "url": "string",
      "source": "arXiv | Semantic Scholar | OpenAlex"
    }
  ],
  "next_page_token": "string | null"
}
```

**Errors**:

| error | retryable | Agent 应对 |
|---|---:|---|
| `rate_limited` | yes | 降低 `max_results` 或稍后重试 |
| `empty_result` | no | 改写 query 或放宽年份 |
| `source_unavailable` | yes | 切换备用数据源 |

**Security**:
- 只访问公开论文元数据。
- 不抓取付费墙内容。
- 不把 API key 写入 trace。

**Example**:

```json
{
  "query": "agentic rag evaluation",
  "year_from": 2023,
  "max_results": 5
}
```
````

## 2. 编写检查表

| 维度 | 检查项 | 期望状态 |
|---|---|---|
| 目的 | Purpose 是否说明工具解决什么问题。 | 模型能区分这个工具和相似工具。 |
| 适用边界 | Use When 和 Do Not Use When 是否成对出现。 | 模型知道什么时候选择、什么时候避开。 |
| 参数 | Input Schema 是否包含必填、可选、默认值和范围。 | 参数可被程序校验，非法参数能被拒绝。 |
| 返回 | Output Schema 是否短而稳定。 | observation 能支持下一步决策，不被噪声淹没。 |
| 错误 | Errors 是否区分可重试和不可重试。 | Agent 能选择重试、改写参数或停止。 |
| 安全 | Security 是否说明权限、隐私和敏感信息边界。 | 高风险动作不会被模型直接执行。 |
| 示例 | Example 是否贴近真实任务。 | 模型能模仿正确参数结构。 |

## 3. 常见问题

### 工具描述要不要写很长？

可以长，但必须结构化。模型更容易理解 `Use When`、`Do Not Use When`、`Input Schema`、`Output Schema`、`Errors` 这类稳定格式。

如果描述很长，应把信息拆到固定字段里，而不是写成连续段落。

### 工具返回越全越好吗？

不是。返回越长，上下文越容易被噪声污染。工具应该返回下一步决策需要的信息，并保留可追溯引用。

例如搜索论文时，返回标题、年份、摘要短片段和链接通常足够；完整论文正文不应直接塞进 observation。

### 要不要让模型自己生成 API 参数？

可以，但参数范围必须由 schema 限制。对真实外部 API，建议加一层适配器做校验、分页、截断和重试。

模型负责提出参数意图，确定性代码负责验证这些参数是否可以执行。

## 关键结论

1. Tool Card 是 tool calling 系统的接口文档，不只是给人看的说明。
2. 好的工具说明必须同时写清楚适用场景和不适用场景。
3. 输入输出 schema 要短、稳定、可校验。
4. 错误类型要能指导 agent 下一步是重试、改写参数、切换工具还是停止。
5. 高风险工具必须显式说明权限和人工确认要求。
