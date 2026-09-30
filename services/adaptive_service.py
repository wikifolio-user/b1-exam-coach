"""Explainable practice selection and daily allocations from saved attempts."""

from __future__ import annotations

from collections import defaultdict
from math import floor


def topic_stats(attempts: list[dict]) -> list[dict]:
    """Return empirical accuracy and Bayesian mastery with a neutral prior.

    One correct answer cannot establish mastery: a Beta(1, 1) prior keeps
    low-evidence estimates conservative. Weakness is the remaining probability
    of an incorrect answer rather than an invented exam grade.
    """
    totals = defaultdict(lambda: [0, 0])
    for attempt in attempts:
        if not isinstance(attempt, dict):
            raise ValueError("Attempts must be dictionaries.")
        skill, topic = attempt.get("skill"), attempt.get("topic")
        if not isinstance(skill, str) or not skill or not isinstance(topic, str) or not topic:
            raise ValueError("Attempts must include skill and topic strings.")
        correct = attempt.get("correct")
        if type(correct) is not bool:
            raise ValueError("Attempt correctness must be a boolean.")
        totals[(skill, topic)][0] += 1
        totals[(skill, topic)][1] += int(correct)
    result = []
    for (skill, topic), (count, correct) in sorted(totals.items()):
        mastery = (correct + 1) / (count + 2)
        result.append({"skill": skill, "topic": topic, "attempts": count, "correct": correct,
                       "accuracy": correct / count, "mastery": mastery, "weakness": 1 - mastery})
    return result


def choose_question(questions: list[dict], attempts: list[dict], topic: str | None = None) -> dict | None:
    candidates = [question for question in questions if topic is None or question["topic"] == topic]
    if not candidates:
        return None
    weaknesses = {(row["skill"], row["topic"]): row["weakness"] for row in topic_stats(attempts)}
    count, last = defaultdict(int), {}
    for index, attempt in enumerate(attempts):
        key = (attempt["skill"], attempt.get("question_id"))
        count[key] += 1
        last[key] = index

    def priority(question: dict) -> tuple:
        key = (question["skill"], question["id"])
        weakness = weaknesses.get((question["skill"], question["topic"]), 0.65)
        novelty = 0.45 / (count[key] + 1)
        freshness = 0.2 if key not in last else 0.2 * (len(attempts) - last[key]) / (len(attempts) + 1)
        return (2 * weakness + novelty + freshness, -count[key])

    return max(candidates, key=priority)


def build_study_plan(attempts: list[dict], settings: dict, due_count: int, writing_count: int = 0) -> list[dict]:
    """Give every skill time, then allocate remaining minutes to learning needs."""
    minutes = settings.get("daily_minutes", 20)
    if type(minutes) is not int or not 5 <= minutes <= 240:
        raise ValueError("daily_minutes must be an integer between 5 and 240.")
    for name, value in (("due_count", due_count), ("writing_count", writing_count)):
        if type(value) is not int or value < 0:
            raise ValueError(f"{name} must be a non-negative integer.")
    stats = topic_stats(attempts)
    skills = ("Reading", "Grammar", "Vocabulary", "Writing")
    plan, weights = [], []
    for skill in skills:
        practiced = [row for row in stats if row["skill"] == skill]
        weakest = max(practiced, key=lambda row: (row["weakness"], row["attempts"])) if practiced else None
        topic = weakest["topic"] if weakest else "initial practice"
        weakness = weakest["weakness"] if weakest else 0.65
        weight = 1 + 2 * weakness
        if weakest:
            reason = f"Focus on {topic}: {weakest['correct']}/{weakest['attempts']} answers correct; estimated mastery {weakest['mastery']:.0%}."
        else:
            reason = "Start with a short practice to establish your current level."
        if skill == "Vocabulary":
            weight += min(due_count / 5, 2)
            reason = f"{due_count} cards are due for review. " + reason
        elif skill == "Writing":
            if writing_count < 3:
                weight += 0.5
                reason = f"Complete a writing task for initial feedback ({writing_count}/3 calibration samples)."
            else:
                reason = "Use feedback from your saved writing to practise content, organisation and language."
        plan.append({"title": f"{skill} practice", "skill": skill, "topic": topic, "minutes": 1, "reason": reason})
        weights.append(weight)
    remaining = minutes - len(plan)
    allocations = [remaining * weight / sum(weights) for weight in weights]
    for item, allocation in zip(plan, allocations):
        item["minutes"] += floor(allocation)
    leftover = minutes - sum(item["minutes"] for item in plan)
    order = sorted(range(len(plan)), key=lambda index: (allocations[index] - floor(allocations[index]), weights[index]), reverse=True)
    for index in order[:leftover]:
        plan[index]["minutes"] += 1
    return plan
