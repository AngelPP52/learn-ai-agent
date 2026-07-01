"""DeepEval GEval demo.

GEval uses an LLM judge, so this example needs an evaluation model provider.
For OpenAI-compatible default usage, set OPENAI_API_KEY before running.

Install:
    python3 -m pip install -r demo/evaluation_frameworks/requirements.txt

Run:
    export OPENAI_API_KEY="..."
    deepeval test run demo/evaluation_frameworks/deepeval_geval_test.py
"""

from __future__ import annotations

import os

from deepeval import assert_test
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, SingleTurnParams


def test_support_answer_correctness_with_geval() -> None:
    test_case = LLMTestCase(
        input="Can I get a refund if the shoes do not fit?",
        actual_output=(
            "You can request a full refund within 30 days. "
            "Please include the order number so support can verify the purchase."
        ),
        expected_output=(
            "Customers can request a full refund within 30 days and should "
            "provide the order number."
        ),
    )

    correctness = GEval(
        name="Refund Policy Correctness",
        criteria=(
            "Determine whether the actual output preserves the refund window, "
            "refund type, and required customer action from the expected output."
        ),
        evaluation_params=[
            SingleTurnParams.INPUT,
            SingleTurnParams.ACTUAL_OUTPUT,
            SingleTurnParams.EXPECTED_OUTPUT,
        ],
        threshold=0.7,
        model=os.getenv("DEEPEVAL_EVAL_MODEL", "gpt-4o-mini"),
    )

    assert_test(test_case, [correctness])
