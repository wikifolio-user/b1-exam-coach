from uuid import uuid4

import streamlit as st

from components.common import get_repository, heading
from data.content import load_vocabulary


def render():
    repository = get_repository()
    heading(
        "Vocabulary Trainer", "Recall the meaning first, then choose how easily you remembered it."
    )
    cards = load_vocabulary()
    due = repository.due_cards(cards)
    states = repository.get_vocab_states()
    cols = st.columns(3)
    cols[0].metric("Due / new", len(due))
    cols[1].metric("Words practised", len(states))
    cols[2].metric("Word bank", len(cards))
    if "vocab_last_review" in st.session_state:
        st.success(st.session_state["vocab_last_review"])
    if not due:
        st.success("All cards are scheduled for later. Come back on their due dates.")
        if states:
            st.dataframe(states, hide_index=True, use_container_width=True)
        return
    card = due[0]
    key = "vocab_" + card["id"]
    with st.container(border=True):
        st.caption(card["topic"])
        st.header(card["word"])
        st.write(card["example"])
        if st.button("Reveal meaning", key=key + "_reveal"):
            st.session_state[key + "_revealed"] = True
        if st.session_state.get(key + "_revealed"):
            st.subheader(card["meaning"])
            st.caption(
                "Again: forgot it · Hard: needed a hint · Good: recalled it · Easy: immediate recall"
            )
            if key + "_review_token" not in st.session_state:
                st.session_state[key + "_review_token"] = uuid4().hex
            for column, quality, label in zip(
                st.columns(4), range(4), ["Again", "Hard", "Good", "Easy"]
            ):
                if column.button(label, key=key + "_" + label, use_container_width=True):
                    state = repository.review_card(
                        card["id"], quality, review_id=st.session_state[key + "_review_token"]
                    )
                    st.session_state["vocab_last_review"] = (
                        f"{card['word']} saved. Next review: {state['due_date']}."
                    )
                    st.session_state.pop(key + "_revealed", None)
                    st.session_state.pop(key + "_review_token", None)
                    st.rerun()
