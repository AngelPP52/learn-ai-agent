"""Print command sequences for running the official AgentBench repository.

The real AgentBench benchmark lives in https://github.com/THUDM/AgentBench and
requires Docker plus task-specific assets. This helper keeps the commands close
to the learning demos without vendoring the benchmark itself.

Run:
    python3 demo/evaluation_frameworks/agentbench_runbook.py --mode fc-docker
    python3 demo/evaluation_frameworks/agentbench_runbook.py --mode v02-lite
"""

from __future__ import annotations

import argparse
import textwrap


FC_DOCKER_COMMANDS = """
# Current main branch: AgentBench FC / AgentRL containerized stack.
git clone https://github.com/THUDM/AgentBench.git
cd AgentBench

# Required images for the low-level task environments.
docker pull mysql:8
docker build -t local-os/default -f ./data/os_interaction/res/dockerfiles/default data/os_interaction/res/dockerfiles
docker build -t local-os/packages -f ./data/os_interaction/res/dockerfiles/packages data/os_interaction/res/dockerfiles
docker build -t local-os/ubuntu -f ./data/os_interaction/res/dockerfiles/ubuntu data/os_interaction/res/dockerfiles

# KnowledgeGraph additionally needs Freebase data mounted at:
# ./virtuoso_db/virtuoso.db

docker compose -f extra/docker-compose.yml up
"""


V02_LITE_COMMANDS = """
# Classic AgentBench v0.2 flow used by many tutorials and papers.
git clone https://github.com/THUDM/AgentBench.git
cd AgentBench
git checkout v0.2

conda create -n agent-bench python=3.9
conda activate agent-bench
pip install -r requirements.txt

docker ps
docker pull mysql
docker pull ubuntu
docker build -f data/os_interaction/res/dockerfiles/default data/os_interaction/res/dockerfiles --tag local-os/default
docker build -f data/os_interaction/res/dockerfiles/packages data/os_interaction/res/dockerfiles --tag local-os/packages
docker build -f data/os_interaction/res/dockerfiles/ubuntu data/os_interaction/res/dockerfiles --tag local-os/ubuntu

# Fill configs/agents/openai-chat.yaml or point configs/agents/api_agents.yaml
# to your own API-compatible agent.
python -m src.client.agent_test --config configs/agents/api_agents.yaml --agent gpt-3.5-turbo-0613

# Terminal 1: start one worker each for dbbench-std and os-std.
python -m src.start_task -a --config configs/start_task_lite.yaml

# Terminal 2: run the lite assignment and write outputs/{TIMESTAMP}.
python -m src.assigner --config configs/assignments/lite.yaml
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=("fc-docker", "v02-lite"),
        default="v02-lite",
        help="Which official AgentBench command sequence to print.",
    )
    args = parser.parse_args()

    commands = FC_DOCKER_COMMANDS if args.mode == "fc-docker" else V02_LITE_COMMANDS
    print(textwrap.dedent(commands).strip())


if __name__ == "__main__":
    main()
