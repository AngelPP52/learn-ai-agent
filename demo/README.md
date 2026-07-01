# Demo 说明

这个目录用于存放 AI Agent 相关示例代码。当前示例围绕提示词路由展开，从普通 Python 控制流逐步过渡到 LangChain classic `RouterChain` 和 LangGraph。

## 示例顺序

| 文件 | 说明 |
|---|---|
| `00_if_else_router.py` | 用普通 `if/else` 实现提示词路由，说明 router 的本质就是条件分发。 |
| `langchain_router_chain_demo.py` | 用 LangChain classic `RouterChain` + `MultiRouteChain` 把路由逻辑封装成可组合 chain。 |
| `02_langgraph_router_state_loop.py` | 用 LangGraph `StateGraph`、条件边和循环展示多步状态、路由、质量门和可观测更新。 |
| `03_langgraph_human_interrupt_visualize.py` | 用 LangGraph `interrupt`、checkpointer 和 Mermaid 图展示人工确认、暂停恢复和结构可视化。 |
| `evaluation_frameworks/` | 用 DeepEval 和 AgentBench 说明 LLM 应用测试、agent benchmark、多轮任务环境和成功率报告。 |

## 安装依赖

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r demo/requirements.txt
```

## 运行示例

```bash
python3 demo/00_if_else_router.py
python3 demo/langchain_router_chain_demo.py
python3 demo/02_langgraph_router_state_loop.py
python3 demo/03_langgraph_human_interrupt_visualize.py
```

评估框架示例使用独立依赖，避免和 LangChain classic 示例互相影响：

```bash
python3 -m venv .venv-eval
source .venv-eval/bin/activate
python3 -m pip install -r demo/evaluation_frameworks/requirements.txt

python3 demo/evaluation_frameworks/deepeval_custom_metric_demo.py
python3 demo/evaluation_frameworks/agentbench_mini_harness.py
```

## 关键理解

简单路由优先使用普通 Python。只有当路由开始涉及共享状态、多步流程、循环、人工确认、暂停恢复或运行时观测时，LangGraph 这类状态图才开始体现价值。
