"""
app.py
------
Streamlit dashboard for the AI-Powered Sports Engagement Content Agent.

Run with:
    streamlit run app.py
"""

import streamlit as st
from app.agent import ContentAgent
from app import schemas

st.set_page_config(page_title="Sports Engagement Content Agent", page_icon="🏆", layout="centered")

SPORTS = ["Cricket", "Football", "Tennis", "Badminton", "Basketball"]
DIFFICULTIES = ["Easy", "Medium", "Hard"]
TYPE_LABELS = {
    "mcq": "Multiple Choice Question",
    "true_false": "True / False",
    "this_or_that": "This-or-That Poll",
    "fill_blank": "Fill in the Blank",
    "guess_number": "Guess the Number",
}

if "agent" not in st.session_state:
    st.session_state.agent = ContentAgent()
if "batch" not in st.session_state:
    st.session_state.batch = []
if "batch_config" not in st.session_state:
    st.session_state.batch_config = None

st.title("🏆 AI Sports Engagement Content Agent")
st.caption("Generates Instagram-ready quizzes, polls & more — grounded in web search + ChromaDB, validated per schema.")

with st.sidebar:
    st.header("Configure batch")
    sport = st.selectbox("Sport", SPORTS)
    difficulty = st.selectbox("Difficulty", DIFFICULTIES)
    selected_types = st.multiselect(
        "Content type(s) — pick multiple to mix in one batch",
        options=list(TYPE_LABELS.keys()),
        default=["mcq", "true_false"],
        format_func=lambda k: TYPE_LABELS[k],
    )
    batch_size = st.slider("Batch size", min_value=4, max_value=5, value=5)
    generate_clicked = st.button("✨ Generate batch", type="primary", use_container_width=True)

if generate_clicked:
    if not selected_types:
        st.warning("Pick at least one content type.")
    else:
        with st.spinner("Retrieving context and generating content..."):
            st.session_state.batch = st.session_state.agent.generate_batch(
                sport, difficulty, selected_types, batch_size
            )
            st.session_state.batch_config = (sport, difficulty, selected_types, batch_size)

if st.session_state.batch_config and st.button("🔄 Regenerate full batch"):
    sport, difficulty, selected_types, batch_size = st.session_state.batch_config
    with st.spinner("Regenerating..."):
        st.session_state.batch = st.session_state.agent.generate_batch(
            sport, difficulty, selected_types, batch_size
        )

st.divider()

for idx, item in enumerate(st.session_state.batch):
    if isinstance(item, dict) and "error" in item:
        st.error(f"Item {idx+1} ({item['type']}) failed validation: {item['error']}")
        continue

    with st.container(border=True):
        col1, col2 = st.columns([5, 1])
        with col1:
            st.markdown(f"**{TYPE_LABELS.get(item.type, item.type)}** · {item.sport}"
                        + (f" · {item.difficulty}" if hasattr(item, "difficulty") else ""))
        with col2:
            if st.button("🔁", key=f"regen_{idx}", help="Regenerate this item"):
                sport_c, difficulty_c, _, _ = st.session_state.batch_config
                with st.spinner("Regenerating item..."):
                    new_item = st.session_state.agent.generate_item(item.type, item.sport,
                                                                      getattr(item, "difficulty", difficulty_c))
                    st.session_state.batch[idx] = new_item
                st.rerun()

        if isinstance(item, schemas.MCQItem):
            st.write(item.question)
            for opt in item.options:
                marker = "✅" if opt == item.correct_answer else "▫️"
                st.write(f"{marker} {opt}")
            st.caption(f"💡 {item.explanation}")

        elif isinstance(item, schemas.TrueFalseItem):
            st.write(item.statement)
            st.write(f"**Answer:** {item.correct_answer}")
            st.caption(f"💡 {item.explanation}")

        elif isinstance(item, schemas.PollItem):
            st.write(item.prompt)
            c1, c2 = st.columns(2)
            c1.button(item.options[0], key=f"pollA_{idx}", use_container_width=True, disabled=True)
            c2.button(item.options[1], key=f"pollB_{idx}", use_container_width=True, disabled=True)
            st.caption("🗳️ Opinion-based — not fact-checked")

        elif isinstance(item, schemas.FillBlankItem):
            st.write(item.sentence)
            for opt in item.options:
                marker = "✅" if opt == item.correct_answer else "▫️"
                st.write(f"{marker} {opt}")
            st.caption(f"💡 {item.explanation}")

        elif isinstance(item, schemas.GuessNumberItem):
            st.write(item.question)
            st.write(f"**Target:** {item.target_number} (±{item.tolerance})")
            st.caption(f"💡 {item.explanation}")

        st.caption(f"📚 Source: {item.source}")

if not st.session_state.batch:
    st.info("Configure your batch in the sidebar and hit **Generate batch** to get started.")
