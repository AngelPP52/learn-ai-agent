# DeepEval 与 AgentBench 示例

这个目录放两个评估框架的入门 demo。DeepEval 更像面向 LLM 应用的 pytest，可以把单轮输出、RAG 片段、agent trace 变成可回归的测试；AgentBench 更像面向 agent 能力的 benchmark，把 agent 放进 OS、DB、WebShop 等交互环境里跑任务并统计成功率。

这些示例围绕同一个问题展开：如何判断一个 AI 应用或 agent 的改动有没有让质量变差。这里不先追求完整 benchmark，而是先把评估对象、评分口径和运行入口讲清楚。

## 1. 使用框架和不使用框架的区别

不用 DeepEval 或 AgentBench 也能做评估。最小做法是写一个 Python 脚本：准备几条输入，调用 agent，拿输出做 `assert`，最后打印通过率。这个方式适合早期探索，成本最低。

框架的价值在于：当评估样本变多、评分口径变复杂、agent 有多轮工具调用、结果要进入 CI 或报告时，它把这些重复基础设施标准化。区别不是“能不能评估”，而是“评估能不能稳定复现、横向比较、失败可追踪”。

| 维度 | 不使用评估框架 | 使用 DeepEval | 使用 AgentBench |
|---|---|---|---|
| 评估对象 | 通常是自己脚本里的输入和输出。 | `LLMTestCase` 把输入、实际输出、期望输出、上下文组织成测试样本。 | task、environment、agent、transcript 组成完整任务交互。 |
| 评分方式 | 手写 `assert`、字符串匹配或临时脚本统计。 | 内置 metric、自定义 metric、`GEval`、RAG metrics，可设置 threshold。 | 由任务环境判断成功失败，并按任务类型统计成功率。 |
| 多轮过程 | 需要自己记录每轮消息、工具调用和环境反馈。 | 可以接应用 trace，但更偏 LLM 应用测试。 | 原生围绕多轮任务交互设计，transcript 是核心产物。 |
| 可复现性 | 取决于脚本是否保存输入、输出、版本和随机性配置。 | 测试文件、metric、阈值和运行命令固定，容易接 CI。 | 任务配置、worker、assigner 和输出目录固定，适合 benchmark 对比。 |
| 失败诊断 | 需要自己决定保存什么日志。 | 失败时能看到 test case、metric 分数和 reason。 | 失败时能回放 agent 动作和环境反馈。 |
| 横向比较 | 需要自己写报表，容易每次口径不同。 | 适合比较 prompt、模型、RAG 配置在同一测试集上的表现。 | 适合比较不同 agent / model 在同一批任务环境里的成功率。 |
| 工程成本 | 初期最低，后期会不断补 case 管理、报告和并发。 | 中等，适合应用级质量门禁。 | 较高，适合多环境 agent benchmark，不适合很小的单轮测试。 |

简单判断：

| 当前阶段 | 建议 |
|---|---|
| 只有 5-10 条固定规则，评估只给自己看。 | 先写普通 Python 脚本。 |
| 已经有一批回归 case，希望 PR 阶段自动阻断质量退化。 | 用 DeepEval。 |
| 需要评估 RAG、客服、问答、摘要等 LLM 应用输出质量。 | 用 DeepEval 或类似应用评估框架。 |
| 需要比较 agent 在 DB、OS、Web、工具环境里的任务完成能力。 | 用 AgentBench 或自建类似 harness。 |
| 业务 agent 的任务环境和公司系统强绑定。 | 借鉴 AgentBench 结构，自建 task environment，再用 DeepEval 做局部输出评估。 |

## 2. 这些示例分别解决什么问题

| 你遇到的问题 | 示例 | 为什么这样用 |
|---|---|---|
| 客服 agent 回答“退款政策”时，必须包含固定业务事实，例如退款类型、退款期限、订单号。 | `deepeval_custom_metric_demo.py` | 这是确定性规则，不需要 LLM judge。用 DeepEval 的 `LLMTestCase` 包住输入和输出，再用自定义 `BaseMetric` 检查关键事实，适合放进 CI。 |
| 回答不是简单关键词能判断，需要看语义是否和标准答案一致。 | `deepeval_geval_test.py` | 这类问题更接近人工 review。用 `GEval` 把输入、实际输出、期望输出交给评审模型，让它按 criteria 打分。 |
| 想理解 AgentBench 为什么需要 task、environment、assigner，而不是只对最终回答打分。 | `agentbench_mini_harness.py` | AgentBench 评估的是“做任务的过程”。本地迷你 harness 用 DB / OS 两个轻量任务模拟多轮交互、环境反馈、轨迹和成功率。 |
| 想真的跑官方 AgentBench，但不知道从哪个命令入口开始。 | `agentbench_runbook.py` | 官方仓库有 current main 和 v0.2 两套常见入口。runbook 只输出命令序列，不把 Docker、数据集和模型配置塞进本仓库。 |

## 3. 示例文件

| 文件 | 评估对象 | 评分口径 | 是否需要外部服务 |
|---|---|---|---|
| `deepeval_custom_metric_demo.py` | 单轮客服回答。 | 是否包含 `full refund`、`30 days`、`order number` 三个必须事实。 | 不需要 LLM API；需要安装 `deepeval`。 |
| `deepeval_geval_test.py` | 单轮客服回答。 | 评审模型判断实际回答是否保留退款窗口、退款类型和客户动作。 | 需要 `OPENAI_API_KEY` 或 DeepEval 支持的其他模型配置。 |
| `agentbench_mini_harness.py` | 两个 agent 在两个轻量任务上的表现。 | 每个任务是否完成，最后统计 `success_rate`。 | 不需要。 |
| `agentbench_runbook.py` | 官方 AgentBench 仓库。 | 不评分，只给可执行入口命令。 | 真正运行时需要 Docker、模型 API 和任务数据。 |

## 4. DeepEval 为什么这样用

DeepEval 适合解决“我的 LLM 应用改完之后有没有退化”这类问题。它的核心不是跑榜单，而是把应用输出变成测试用例。

在 `deepeval_custom_metric_demo.py` 里，问题是：客服回答退款问题时，有些业务事实不能丢。比如回答必须说明“30 天内可全额退款，并提供订单号”。如果只靠人工抽查，每次改 prompt 都很难稳定复验；如果用普通单元测试直接 `assert output == expected_output`，又会把模型的合理改写误判成失败。

所以示例用三层结构：

| 层次 | 代码位置 | 解决的问题 |
|---|---|---|
| 被测应用 | `support_agent(question)` | 模拟真实 LLM 应用，输入用户问题，输出回答。 |
| 测试样本 | `LLMTestCase(...)` | 固定本次评估的输入、实际输出和期望输出。 |
| 评分器 | `RequiredPhrasesMetric` | 只检查业务必须事实，不要求逐字相同。 |

这样用的原因是：业务规则明确时，确定性 metric 更便宜、更稳定，也更适合 CI。这个 demo 不是在评估语言是否优美，而是在评估“关键政策事实是否被保留”。

在 `deepeval_geval_test.py` 里，问题换成：如果回答换了一种表达，关键词不完全匹配，但语义仍然正确，应该怎么评估。这时用硬编码关键词容易误判，所以示例用 `GEval`：

| 参数 | 为什么需要 |
|---|---|
| `criteria` | 把人工评审标准写清楚，例如保留退款窗口、退款类型和客户动作。 |
| `evaluation_params` | 告诉评审模型可以看哪些字段，例如输入、实际输出、期望输出。 |
| `threshold` | 把主观评分变成可执行门槛，低于阈值就失败。 |

这个 demo 的价值是说明 LLM-as-judge 应该被约束在明确 criteria 里，而不是泛泛问模型“这个回答好吗”。它适合语义正确性、相关性、语气、安全性等无法靠简单字符串判断的场景。

DeepEval 的基本结构是：

| 概念 | 作用 | 示例 |
|---|---|---|
| `LLMTestCase` | 一条被评估的交互，包含输入、实际输出、期望输出或检索上下文。 | 退款问题、agent 实际回答、标准政策回答。 |
| Metric | 评分器，输出 `0-1` 分数，并用 `threshold` 判断是否通过。 | `GEval`、`AnswerRelevancyMetric`、自定义 `BaseMetric`。 |
| `assert_test` | 把 test case 和 metrics 接到测试断言里。 | 分数低于阈值时失败。 |
| `deepeval test run` | DeepEval 的测试运行入口，适合接入 CI。 | `deepeval test run demo/evaluation_frameworks/deepeval_custom_metric_demo.py` |

先运行不需要 LLM judge 的本地示例：

```bash
python3 -m venv .venv-eval
source .venv-eval/bin/activate
python3 -m pip install -r demo/evaluation_frameworks/requirements.txt

python3 demo/evaluation_frameworks/deepeval_custom_metric_demo.py
deepeval test run demo/evaluation_frameworks/deepeval_custom_metric_demo.py
```

再运行 G-Eval 示例：

```bash
export OPENAI_API_KEY="..."
export DEEPEVAL_EVAL_MODEL="gpt-4o-mini"
deepeval test run demo/evaluation_frameworks/deepeval_geval_test.py
```

使用边界：

| 场景 | 更适合的 DeepEval 用法 |
|---|---|
| 明确的业务规则、格式、关键词 | 自定义 `BaseMetric`，稳定且便宜。 |
| 正确性、相关性、语气等需要语义判断的问题 | `GEval` 或内置 LLM-as-judge metric。 |
| RAG 质量 | answer relevancy、faithfulness、contextual relevancy 等 RAG metrics。 |
| Agent 流程质量 | tracing + task completion、tool correctness 等 agentic metrics。 |

## 5. AgentBench 为什么这样用

AgentBench 适合解决“一个模型或 agent 是否真的会在环境里完成任务”这类问题。它关注的不是单轮回答质量，而是 agent 在任务环境中的行动过程。

在 `agentbench_mini_harness.py` 里，问题是：如果一个 agent 被要求写 SQL 或 shell command，只看最终文本还不够。评估需要知道它面对了什么任务、采取了什么动作、环境给了什么反馈、最后是否完成。

所以示例刻意拆出几类对象：

| 对象 | 为什么要拆出来 | 对应代码 |
|---|---|---|
| `TaskSpec` | 任务定义要可复用、可版本化。 | DB 任务和 OS 任务。 |
| `TaskEnvironment` | 任务环境负责反馈成功或失败，不让 agent 自己给自己打分。 | `interact(action)` |
| `RuleAgent` | agent 只负责根据历史轨迹输出下一步动作。 | `act(...)` |
| `Assigner` | 统一调度多个 agent 和多个 task，便于横向比较。 | `run()` |
| `TrialResult.transcript` | 保留完整轨迹，失败后能回放和定位。 | `transcript` |

这个本地 demo 不是在复刻 AgentBench 的全部环境，而是在说明 AgentBench 的评估单位为什么是“任务交互轨迹”。真实 AgentBench 里的 DBBench、OS、WebShop、KnowledgeGraph 等任务，只是把这个迷你结构换成更真实、更重的环境。

`agentbench_runbook.py` 解决的是另一个问题：官方 AgentBench 不是一个简单 pip 包，真实运行依赖 Docker、任务数据、模型 API 和配置文件。把命令单独列出来，可以让读者先理解入口，再决定是否投入机器资源跑完整 benchmark。

AgentBench 的核心不是“给一个答案打分”，而是让 agent 和任务环境多轮交互。经典结构可以拆成：

| 组件 | 作用 | 在 demo 中的对应物 |
|---|---|---|
| Task Worker / Environment | 托管一个可交互任务环境。 | `TaskEnvironment` |
| Agent Client | 接收历史轨迹并输出下一步动作。 | `RuleAgent` |
| Assigner | 按 agent、task 和并发配置分配样本。 | `Assigner` |
| Transcript | 保存任务提示、agent 动作和环境反馈。 | `TrialResult.transcript` |
| Report | 统计每个 agent 在每类任务上的结果。 | `success_rate` |

先运行本地迷你版本理解流程：

```bash
python3 demo/evaluation_frameworks/agentbench_mini_harness.py
```

查看官方仓库的运行命令：

```bash
python3 demo/evaluation_frameworks/agentbench_runbook.py --mode v02-lite
python3 demo/evaluation_frameworks/agentbench_runbook.py --mode fc-docker
```

官方仓库当前 `main` 分支优先介绍 AgentBench FC 和 Docker Compose；许多旧教程仍对应 v0.2 的 `src.start_task` + `src.assigner` 流程。实际跑完整 benchmark 前要先确认机器资源，官方 README 明确提示 WebShop 启动大约需要 16GB RAM，部分任务还依赖额外数据或 Docker 镜像。

## 6. 两者怎么选

| 评估目标 | 优先选型 | 原因 |
|---|---|---|
| 应用级回归测试、CI 门禁、prompt 或 RAG 质量检查 | DeepEval | 接入成本低，可以按测试文件逐步积累。 |
| 比较模型作为 agent 的综合任务能力 | AgentBench | 有多环境、多轮交互和成功率口径。 |
| 业务 agent 上线前质量保障 | DeepEval + 自建任务集 | 更容易贴合真实业务输入、工具和审批规则。 |
| 论文复现或标准 benchmark 对比 | AgentBench | 更接近公开 benchmark 的报告方式。 |

参考来源：

| 框架 | 链接 |
|---|---|
| DeepEval quickstart | <https://deepeval.com/docs/getting-started> |
| DeepEval custom metrics | <https://deepeval.com/docs/metrics-custom> |
| AgentBench 官方仓库 | <https://github.com/THUDM/AgentBench> |
| AgentBench framework introduction | <https://github.com/THUDM/AgentBench/blob/main/docs/Introduction_en.md> |
