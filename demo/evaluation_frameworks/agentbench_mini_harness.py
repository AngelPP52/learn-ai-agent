"""A local miniature harness inspired by AgentBench's execution model.

This is not the official AgentBench package. It demonstrates the core shape:
tasks expose an interactive environment, agents act over one or more turns,
the assigner runs agent-task pairs, and the report focuses on task success.

Run:
    python3 demo/evaluation_frameworks/agentbench_mini_harness.py
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True)
class TaskSpec:
    name: str
    prompt: str
    required_terms: tuple[str, ...]
    max_turns: int = 2


@dataclass
class Turn:
    role: str
    content: str


@dataclass
class TrialResult:
    agent_name: str
    task_name: str
    success: bool
    transcript: list[Turn] = field(default_factory=list)


class Agent(Protocol):
    name: str

    def act(self, task_name: str, history: list[Turn]) -> str:
        ...


class RuleAgent:
    def __init__(self, name: str, behavior: dict[str, str]):
        self.name = name
        self.behavior = behavior

    def act(self, task_name: str, history: list[Turn]) -> str:
        return self.behavior.get(task_name, "I need more information.")


class TaskEnvironment:
    def __init__(self, spec: TaskSpec):
        self.spec = spec

    def start(self) -> Turn:
        return Turn(role="task", content=self.spec.prompt)

    def interact(self, action: str) -> tuple[Turn, bool]:
        normalized = action.lower()
        success = all(term.lower() in normalized for term in self.spec.required_terms)

        if success:
            feedback = "success: all required operations were completed."
        else:
            missing = [
                term for term in self.spec.required_terms if term.lower() not in normalized
            ]
            feedback = "feedback: missing " + ", ".join(missing)

        return Turn(role="task", content=feedback), success


class Assigner:
    def __init__(self, agents: list[Agent], tasks: list[TaskSpec]):
        self.agents = agents
        self.tasks = tasks

    def run(self) -> list[TrialResult]:
        results: list[TrialResult] = []

        for agent in self.agents:
            for task in self.tasks:
                results.append(self._run_trial(agent, task))

        return results

    def _run_trial(self, agent: Agent, task: TaskSpec) -> TrialResult:
        env = TaskEnvironment(task)
        transcript = [env.start()]
        success = False

        for _ in range(task.max_turns):
            action = agent.act(task.name, transcript)
            transcript.append(Turn(role=agent.name, content=action))
            feedback, success = env.interact(action)
            transcript.append(feedback)
            if success:
                break

        return TrialResult(
            agent_name=agent.name,
            task_name=task.name,
            success=success,
            transcript=transcript,
        )


def print_report(results: list[TrialResult]) -> None:
    print("AgentBench-style success rate report")
    print("=" * 72)

    by_agent: dict[str, list[TrialResult]] = {}
    for result in results:
        by_agent.setdefault(result.agent_name, []).append(result)
        status = "PASS" if result.success else "FAIL"
        print(f"{result.agent_name:16} {result.task_name:16} {status}")

    print("-" * 72)
    for agent_name, agent_results in by_agent.items():
        passed = sum(result.success for result in agent_results)
        total = len(agent_results)
        print(f"{agent_name:16} success_rate={passed / total:.2f} ({passed}/{total})")


def main() -> None:
    tasks = [
        TaskSpec(
            name="dbbench-lite",
            prompt=(
                "Find how many refunded orders exist. Respond with the SQL you "
                "would execute."
            ),
            required_terms=("select", "count", "orders", "refunded"),
        ),
        TaskSpec(
            name="os-lite",
            prompt=(
                "Archive all .log files under /tmp/app into logs.tar.gz. "
                "Respond with the shell command."
            ),
            required_terms=("tar", "logs.tar.gz", ".log"),
        ),
    ]

    agents = [
        RuleAgent(
            name="careful-agent",
            behavior={
                "dbbench-lite": (
                    "SELECT COUNT(*) FROM orders WHERE status = 'refunded';"
                ),
                "os-lite": "find /tmp/app -name '*.log' -print0 | tar --null -czf logs.tar.gz --files-from -",
            },
        ),
        RuleAgent(
            name="vague-agent",
            behavior={
                "dbbench-lite": "Look at the orders table and count the rows.",
                "os-lite": "Use an archive command for the logs.",
            },
        ),
    ]

    results = Assigner(agents=agents, tasks=tasks).run()
    print_report(results)

    print("\nExample transcript")
    print("=" * 72)
    for turn in results[0].transcript:
        print(f"{turn.role}: {turn.content}")


if __name__ == "__main__":
    main()
