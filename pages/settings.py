from datetime import date, timedelta
import json

import streamlit as st

from components.common import api_key, get_repository, heading


def render():
    repository = get_repository()
    settings = repository.get_settings()
    heading("Settings", "Personalise your study goal. Your profile and results stay in SQLite.")
    with st.form("settings_form"):
        name = st.text_input("Learner name", value=settings["learner_name"], max_chars=100)
        minutes = st.number_input(
            "Daily study minutes",
            min_value=5,
            max_value=240,
            value=settings["daily_minutes"],
            step=5,
        )
        has_exam = st.checkbox("Set an exam date", value=bool(settings["exam_date"]))
        exam_date = st.date_input(
            "Exam date",
            value=date.fromisoformat(settings["exam_date"])
            if settings["exam_date"]
            else date.today() + timedelta(days=60),
        )
        enabled = st.checkbox("Enable optional OpenAI feedback", value=settings["ai_enabled"])
        model = st.text_input("OpenAI model", value=settings["openai_model"], max_chars=100)
        st.caption(
            "Set OPENAI_API_KEY in your environment, local .env or Streamlit secrets. API keys are never stored in the learning database. Each Writing submission requires a separate AI choice."
        )
        save = st.form_submit_button("Save settings", type="primary")
    if save:
        try:
            repository.update_settings(
                {
                    "learner_name": name,
                    "daily_minutes": int(minutes),
                    "exam_date": exam_date.isoformat() if has_exam else "",
                    "ai_enabled": enabled,
                    "openai_model": model,
                }
            )
        except ValueError as error:
            st.error(str(error))
        else:
            st.success("Settings saved.")
    st.caption(
        "OpenAI key configured: " + ("yes" if api_key() else "no — offline feedback is available")
    )
    st.subheader("Export your learning data")
    st.write(
        "Download your profile, answers, mistakes, vocabulary schedules and writing drafts as JSON."
    )
    st.download_button(
        "Download learning data",
        json.dumps(repository.export_data(), ensure_ascii=False, indent=2),
        file_name="b1-learning-data.json",
        mime="application/json",
    )
    st.caption(
        "This app has one local learner profile. Use separate database files for different learners. Hosted SQLite needs a persistent volume; ephemeral hosting can lose local files."
    )
