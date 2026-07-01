"""DeepEval demo with a deterministic custom metric.

This example shows the pytest-like DeepEval workflow without calling an LLM
judge. It is useful for CI smoke checks, exact policy checks, or teaching the
shape of a DeepEval test before introducing GEval.

Install:
    python3 -m pip install -r demo/evaluation_frameworks/requirements.txt

Run as a script:
    python3 demo/evaluation_frameworks/deepeval_custom_metric_demo.py

Run through DeepEval's test runner:
    deepeval test run demo/evaluation_frameworks/deepeval_custom_metric_demo.py
"""

from __future__ import annotations

from dataclasses import dataclass

from deepeval import assert_test
from deepeval.metrics import BaseMetric
from deepeval.test_case import LLMTestCase


def support_agent(question: str) -> str:
    """A tiny stand-in for a real LLM application."""

    if "refund" in question.lower() or "退款" in question:
        return (
            "You can request a full refund within 30 days. "
            "Please include the order number so support can verify the purchase."
        )

    return "Please contact support with more details."


@dataclass(frozen=True)
class PhraseHit:
    phrase: str
    matched: bool


class RequiredPhrasesMetric(BaseMetric):
    """Score an answer by checking required business facts."""

    def __init__(self, required_phrases: list[str], threshold: float = 1.0):
        self.required_phrases = required_phrases
        self.threshold = threshold
        self.score = 0.0
        self.success = False
        self.reason = ""
        self.error = None

    def measure(self, test_case: LLMTestCase) -> float:
        normalized_output = test_case.actual_output.lower()
        hits = [
            PhraseHit(phrase=phrase, matched=phrase.lower() in normalized_output)
            for phrase in self.required_phrases
        ]
        matched_count = sum(hit.matched for hit in hits)

        self.score = matched_count / len(self.required_phrases)
        self.success = self.score >= self.threshold
        self.reason = ", ".join(
            f"{hit.phrase}={'yes' if hit.matched else 'no'}" for hit in hits
        )
        return self.score

    async def a_measure(self, test_case: LLMTestCase) -> float:
        return self.measure(test_case)

    def is_successful(self) -> bool:
        if self.error is not None:
            self.success = False
        else:
            self.success = self.score >= self.threshold
        return self.success

    @property
    def __name__(self) -> str:
        return "Required Phrases"


def build_refund_test_case() -> LLMTestCase:
    question = "Can I get a refund if the shoes do not fit?"
    return LLMTestCase(
        input=question,
        actual_output=support_agent(question),
        expected_output=(
            "Customers can request a full refund within 30 days and should "
            "provide the order number."
        ),
    )


def test_refund_answer_contains_policy_facts() -> None:
    test_case = build_refund_test_case()
    metric = RequiredPhrasesMetric(
        required_phrases=["full refund", "30 days", "order number"],
        threshold=1.0,
    )

    assert_test(test_case, [metric], run_async=False)


def main() -> None:
    test_case = build_refund_test_case()
    metric = RequiredPhrasesMetric(
        required_phrases=["full refund", "30 days", "order number"],
        threshold=1.0,
    )

    score = metric.measure(test_case)
    print(f"input: {test_case.input}")
    print(f"actual_output: {test_case.actual_output}")
    print(f"metric: {metric.__name__}")
    print(f"score: {score:.2f}")
    print(f"success: {metric.is_successful()}")
    print(f"reason: {metric.reason}")


if __name__ == "__main__":
    main()
