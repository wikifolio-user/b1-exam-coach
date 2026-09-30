"""Transparent, local practice feedback for B1 writing.

The scores below are deliberately conservative heuristics. Keyword clues and
surface structure are useful for a first revision, but are not examiner scores.
"""

from __future__ import annotations

import re
from typing import Any


SCORE_NAMES = ("Content", "Communicative Achievement", "Organisation", "Language")
_WORDS = re.compile(r"\b[^\W_]+(?:['’\-][^\W_]+)*\b", re.UNICODE)
_CONNECTORS = re.compile(
    r"\b(?:and|but|because|so|first|then|finally|also|however|after|when|while|"
    r"although|for example|in the end)\b", re.IGNORECASE
)
_PHRASES = {
    "Email": ["Thanks for your email.", "I'd be happy to ...", "Why don't we ...?", "Best wishes,"],
    "Article": ["Have you ever ...?", "In my opinion, ...", "One reason is that ...", "To sum up, ..."],
    "Story": ["At first, ...", "Suddenly, ...", "A few minutes later, ...", "In the end, ..."],
}
OFFLINE_DISCLAIMER = (
    "Offline practice estimates use word count, surface structure and keyword clues. "
    "They cannot verify meaning, grammatical accuracy or Cambridge marking standards. "
    "A clue does not prove that a task point is fully answered."
)


def word_count(text: str) -> int:
    """Count words consistently for local and optional AI feedback."""
    return len(_WORDS.findall(text))


def _has_clue(text: str, keyword: str) -> bool:
    keyword = " ".join(keyword.casefold().split())
    if not keyword:
        return False
    variants = {keyword}
    # A small, explicit morphology approximation; never presented as semantics.
    if " " not in keyword and len(keyword) >= 4:
        variants.update({keyword + "s", keyword + "es", keyword + "ed", keyword + "ing"})
        if keyword.endswith("e"):
            variants.update({keyword + "d", keyword[:-1] + "ing"})
        if keyword.endswith("y"):
            variants.update({keyword[:-1] + "ies", keyword[:-1] + "ied"})
    return any(re.search(r"(?<!\w)" + re.escape(value) + r"(?!\w)", text) for value in variants)


def evaluate_offline(text: str, task: dict[str, Any]) -> dict[str, Any]:
    """Return actionable feedback without an API, a fabricated rewrite or data transfer."""
    if not isinstance(text, str):
        raise TypeError("Writing text must be a string.")
    kind = task.get("kind", "Email")
    if kind not in _PHRASES:
        raise ValueError("Writing kind must be Email, Article or Story.")
    normalized = " ".join(text.casefold().replace("’", "'").split())
    words = _WORDS.findall(text)
    count = len(words)
    points = list(task.get("points", []))
    keywords = task.get("keywords", [])
    matched = []
    missing = []
    unchecked = []
    for index, point in enumerate(points):
        clues = keywords[index] if index < len(keywords) else []
        if not clues:
            unchecked.append(point)
        elif any(_has_clue(normalized, clue.casefold().replace("’", "'")) for clue in clues):
            matched.append(point)
        else:
            missing.append(point)

    strengths: list[str] = []
    improvements: list[str] = []
    if not count:
        missing = points.copy()
        scores = {name: 0.0 for name in SCORE_NAMES}
        improvements.extend([
            "Write a complete response of about 100 words before reviewing it.",
            "Use the task points as a checklist and answer each one.",
        ])
    else:
        if 80 <= count <= 120:
            strengths.append(f"Your {count}-word response is close to the 100-word target.")
        elif count < 80:
            improvements.append(f"You wrote {count} words. Add useful detail and aim for about 100 words.")
        else:
            improvements.append(f"You wrote {count} words. Remove repetition and aim for about 100 words.")
        if matched:
            strengths.append(f"Keyword clues were found for {len(matched)} of {len(points)} task points; check their meaning yourself.")
        for point in missing:
            improvements.append(f"No keyword clue was found for this point: {point} Check that you answer it clearly.")
        if unchecked:
            improvements.append("Some task points have no keyword checklist. Check every point against the prompt yourself.")

        checked_count = len(matched) + len(missing)
        content = 4.0 * len(matched) / checked_count if checked_count else 2.0
        format_score, format_strengths, format_improvements = _format_feedback(text, kind, task)
        strengths.extend(format_strengths)
        improvements.extend(format_improvements)

        sentences = [part for part in re.split(r"[.!?]+", text) if _WORDS.search(part)]
        paragraphs = [part for part in re.split(r"\n\s*\n", text.strip()) if part.strip()]
        connectors = _CONNECTORS.findall(text)
        organisation = min(4.0, 1.5 + (0.8 if len(sentences) >= 3 else 0)
                           + (0.8 if len(paragraphs) >= 2 else 0)
                           + (0.9 if len(connectors) >= 2 else 0))
        if len(paragraphs) < 2:
            improvements.append("Group related ideas into short paragraphs so the reader can follow them.")
        else:
            strengths.append("The text is divided into separate paragraphs.")
        if len(connectors) < 2:
            improvements.append("Connect ideas with words such as because, but, then or finally.")
        else:
            strengths.append("The text includes linking-word clues.")

        unique_ratio = len({word.casefold() for word in words}) / count
        average_sentence = count / max(1, len(sentences))
        language = min(4.0, 1.3 + (0.8 if unique_ratio >= 0.45 else 0)
                       + (0.7 if 5 <= average_sentence <= 22 else 0)
                       + (0.6 if re.search(r"[.!?]", text) else 0)
                       + (0.6 if len(connectors) >= 2 else 0))
        if average_sentence > 25:
            improvements.append("Break very long sentences into shorter sentences and check full stops.")
        if unique_ratio < 0.4:
            improvements.append("Replace repeated words where possible, while keeping your meaning clear.")
        if re.search(r"(?<!\w)i(?!\w)", text):
            improvements.append("Write the pronoun I with a capital letter.")
            language -= 0.4
        common_errors = [
            (r"\bi am agree\b", "Use 'I agree', without am."),
            (r"\bi have \d+ years(?: old)?\b", "Give your age with 'I am ... years old'."),
            (r"\b(?:he|she) go\b", "Check the present simple: he/she goes."),
            (r"\bpeople is\b", "Use 'people are' because people is plural."),
        ]
        for pattern, advice in common_errors:
            if re.search(pattern, normalized):
                improvements.append(advice)
                language -= 0.4
        # Sparse responses must not receive high scores for a few format clues.
        cap = 1.0 if count < 20 else 2.0 if count < 50 else 3.0 if count < 70 else 4.0
        scores = dict(zip(SCORE_NAMES, [
            round(max(0.0, min(cap, value)), 1)
            for value in (content, format_score, organisation, language)
        ]))
        improvements.append("Read the prompt again, check your verb forms and spelling, and make sure each idea is clear.")

    return {
        "provider": "offline",
        "word_count": count,
        "scores": scores,
        "total": round(sum(scores.values()), 1),
        "strengths": strengths,
        "improvements": improvements,
        "missing_points": missing,
        "useful_phrases": _PHRASES[kind].copy(),
        "exam_tip": _exam_tip(kind),
        "improved_version": "",
        "disclaimer": OFFLINE_DISCLAIMER,
    }


def _format_feedback(text: str, kind: str, task: dict[str, Any]) -> tuple[float, list[str], list[str]]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    strengths: list[str] = []
    improvements: list[str] = []
    score = 2.0
    if kind == "Email":
        if lines and re.match(r"^(hi|hello|dear)\b", lines[0], re.IGNORECASE):
            strengths.append("The email starts with a greeting.")
            score += 1.0
        else:
            improvements.append("Start your email with a greeting, for example Hi Alex,.")
        if re.search(r"\b(best wishes|all the best|see you|bye|love|regards)\b", " ".join(lines[-3:]), re.IGNORECASE):
            strengths.append("The email includes a closing phrase.")
            score += 1.0
        else:
            improvements.append("Finish with a friendly closing, for example Best wishes, and your name.")
    elif kind == "Article":
        # A standalone short first line is a title clue, not proof of a good title.
        if len(lines) >= 2 and 1 <= word_count(lines[0]) <= 12 and not lines[0].endswith((".", ",", ";")):
            strengths.append("The article has a short title line.")
            score += 1.0
        else:
            improvements.append("Add a short, interesting title on its own line.")
        if re.search(r"\byou(?:r)?\b|\?", text, re.IGNORECASE):
            strengths.append("The article contains clues that address the reader.")
            score += 1.0
        else:
            improvements.append("Interest your reader with a question or a clear personal opinion.")
    else:
        starter = task.get("starter", "").strip()
        if starter:
            if text.strip().casefold().startswith(starter.casefold()):
                strengths.append("The story starts with the supplied opening sentence.")
                score += 1.0
            else:
                improvements.append(f"Start with the exact supplied sentence: {starter}")
                score -= 0.5
        else:
            score += 0.5
        if re.search(r"\b(was|were|went|saw|had|got|took|found|felt|decided|opened|heard|left|arrived|started|looked)\b", text, re.IGNORECASE):
            strengths.append("The story contains past-tense narrative clues.")
            score += 1.0
        else:
            improvements.append("Tell the main events in a consistent past tense.")
        if not re.search(r"\b(finally|in the end|at last|happy|safe|smiled|learned)\b", text, re.IGNORECASE):
            improvements.append("Give the story a clear ending that shows what happened or how you felt.")
    return min(4.0, score), strengths, improvements


def _exam_tip(kind: str) -> str:
    if kind == "Email":
        return "In the exam, answer the email task and each note. Use a friendly tone and write about 100 words."
    if kind == "Article":
        return "An article is one option in Writing Part 2. Give it a title, answer the question and interest the reader in about 100 words."
    return "A story is one option in Writing Part 2. Use the given opening sentence and tell a clear sequence of events in about 100 words."
