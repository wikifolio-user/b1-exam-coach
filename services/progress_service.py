from datetime import date, datetime, timedelta, timezone


def learning_summary(attempts: list[dict], writing: list[dict], today: date | None = None) -> dict:
    today = today or datetime.now(timezone.utc).date()
    dates = {attempt["created_at"][:10] for attempt in [*attempts, *writing]}
    cursor = today if today.isoformat() in dates else today - timedelta(days=1)
    streak = 0
    while cursor.isoformat() in dates:
        streak += 1
        cursor -= timedelta(days=1)
    return {
        "attempts": len(attempts),
        "accuracy": sum(bool(attempt["correct"]) for attempt in attempts) / len(attempts)
        if attempts
        else None,
        "writing_count": len(writing),
        "today_count": sum(
            item["created_at"][:10] == today.isoformat() for item in [*attempts, *writing]
        ),
        "streak": streak,
    }
