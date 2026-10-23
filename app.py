
import streamlit as st
from src.rag import answer_question

st.set_page_config(
    page_title="NCERT Science Tutor",
    page_icon="📘",
    layout="centered"
)

st.title("📘 NCERT Science Tutor")
st.write(
    "Ask questions from your Class 10 Science textbook. "
    "Answers are generated using retrieved textbook content."
)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

question = st.chat_input("Ask a Science question...")

if question:
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Searching the NCERT textbook..."):
            try:
                answer = answer_question(question)
            except Exception as error:
                answer = f"Something went wrong: {error}"

        st.markdown(answer)

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })
