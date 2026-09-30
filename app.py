import streamlit as st
from dotenv import load_dotenv

# Load local environment variables before importing modules that read DATABASE_URL.
load_dotenv()

from database.seed import seed_database
from pages import dashboard, grammar, mistakes, progress, reading, settings, study_plan, vocabulary, writing
from utils.constants import APP_TITLE

st.set_page_config(page_title=APP_TITLE, page_icon="🎯", layout="wide")
seed_database()

PAGES = {
    "🏠 Dashboard": dashboard.render,
    "🎯 Study Plan": study_plan.render,
    "📖 Reading": reading.render,
    "✍️ Writing": writing.render,
    "🧠 Grammar": grammar.render,
    "📚 Vocabulary": vocabulary.render,
    "❌ My Mistakes": mistakes.render,
    "📊 Progress": progress.render,
    "⚙️ Settings": settings.render,
}

if "nav" not in st.session_state:
    st.session_state["nav"] = "🏠 Dashboard"

with st.sidebar:
    st.title("B1 Exam Coach")
    st.caption("Cambridge B1 Preliminary training")
    labels = list(PAGES.keys())
    current = st.session_state.get("nav", labels[0])
    if current not in labels:
        current = labels[0]
    selected = st.radio(
        "Navigation",
        labels,
        index=labels.index(current),
        label_visibility="collapsed",
    )
    st.session_state["nav"] = selected
    st.divider()
    st.caption("Phase 2 · adaptive study + writing")

PAGES[selected]()
