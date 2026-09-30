import unicodedata


def normalize_answer(value: str) -> str:
    return " ".join(
        unicodedata.normalize("NFKC", value).strip().casefold().replace("’", "'").split()
    )


def answer_matches(answer: str, question: dict) -> bool:
    accepted = [question["answer"], *question.get("accepted_answers", [])]
    return normalize_answer(answer) in {normalize_answer(value) for value in accepted}
