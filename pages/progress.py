import pandas as pd
import streamlit as st

from components.common import get_repository, heading
from services.adaptive_service import topic_stats
from services.progress_service import learning_summary


def render():
    repository = get_repository()
    attempts, writing = repository.get_attempts(), repository.get_writing()
    heading("Progress", "See practice frequency, topic performance and saved writing estimates.")
    summary = learning_summary(attempts, writing)
    cols = st.columns(4)
    cols[0].metric("Answers", summary["attempts"])
    cols[1].metric(
        "Accuracy", f"{summary['accuracy']:.0%}" if summary["accuracy"] is not None else "—"
    )
    cols[2].metric("Writing drafts", len(writing))
    cols[3].metric("Study streak", f"{summary['streak']} days")
    if not attempts and not writing:
        st.info("Complete your first practice activity. Charts will appear here afterwards.")
        return
    if attempts:
        frame = pd.DataFrame(attempts)
        frame["date"] = pd.to_datetime(frame["created_at"], utc=True).dt.date
        st.subheader("Answers per study day")
        st.bar_chart(frame.groupby("date").size().rename("Answers"))
        st.subheader("Topic performance")
        stats = pd.DataFrame(topic_stats(attempts))
        st.dataframe(
            stats[["skill", "topic", "attempts", "correct", "accuracy", "mastery"]],
            hide_index=True,
            use_container_width=True,
            column_config={
                "accuracy": st.column_config.ProgressColumn(
                    "Accuracy", min_value=0, max_value=1, format="%.2f"
                ),
                "mastery": st.column_config.ProgressColumn(
                    "Estimated mastery", min_value=0, max_value=1, format="%.2f"
                ),
            },
        )
        st.caption(
            "Mastery is a smoothed estimate. Vocabulary accuracy comes from self-rated recall. These are not exam readiness predictions."
        )
    if writing:
        st.subheader("Writing estimates over time")
        rows = [
            {
                "Date": pd.to_datetime(item["created_at"], utc=True),
                "Type": item["kind"],
                "Provider": item["feedback"]["provider"],
                "Estimate /20": item["feedback"]["total"],
            }
            for item in writing
        ]
        st.line_chart(pd.DataFrame(rows).set_index("Date")["Estimate /20"])
        st.dataframe(rows, hide_index=True, use_container_width=True)
        st.caption(
            "Offline heuristics and AI estimates are different measures. Compare drafts using the same provider and task type."
        )
