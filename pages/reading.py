import streamlit as st

from components.common import get_repository, heading, quiz
from data.content import load_reading

PART_NAMES = {
    1: "Short messages",
    2: "Matching people to texts",
    3: "Long text comprehension",
    4: "Gapped text",
    5: "Multiple choice cloze",
    6: "Open cloze",
}


def render():
    heading(
        "Reading Trainer",
        "Six exam formats, original practice texts and explanations for every answer.",
    )
    part = st.selectbox(
        "Reading part", list(PART_NAMES), format_func=lambda p: f"Part {p} · {PART_NAMES[p]}"
    )
    sets = [item for item in load_reading() if item["part"] == part]
    chosen = st.selectbox("Practice set", sets, format_func=lambda item: item["title"])
    st.subheader(chosen["title"])
    st.write(chosen["instructions"])
    with st.container(border=True):
        st.markdown(chosen["passage"])
    quiz(chosen["questions"], f"reading_{chosen['id']}", get_repository())
