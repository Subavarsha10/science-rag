
import hashlib
import streamlit as st

from src.rag import answer_question
from src.practice import generate_practice_questions
from src.youtube_search import search_youtube_videos
from src.pdf_qa import (
    answer_pdf_question,
    answer_all_pdf_questions
)


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Science RAG Tutor",
    page_icon="📘",
    layout="wide"
)

st.title("📘 Science RAG Tutor")
st.write(
    "Learn Class 10 Science with NCERT answers, PYQs, practice "
    "questions, YouTube videos, and uploaded-PDF question answering."
)
st.divider()


# ==================================================
# SOURCE DISPLAY
# ==================================================

def display_sources(sources, title="📚 View sources"):
    if not sources:
        return

    with st.expander(title):
        seen = set()

        for source in sources:
            name = source.get("source", "Unknown source")
            source_type = source.get("type") or (
                "PDF" if name == "Uploaded PDF" else "NCERT"
            )
            page = source.get("page")

            key = (source_type, name, page)

            if key in seen:
                continue

            seen.add(key)

            label = f"- **{source_type}** — `{name}`"

            if page is not None:
                label += f", page {page}"

            st.markdown(label)


# ==================================================
# FOUR TABS
# ==================================================

chat_tab, practice_tab, youtube_tab, pdf_tab = st.tabs([
    "💬 Ask Science",
    "📝 Practice Questions",
    "▶️ YouTube Learning",
    "📄 Upload PDF"
])


# ==================================================
# TAB 1: ASK SCIENCE
# ==================================================

with chat_tab:
    st.header("💬 Ask Science")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            if message["role"] == "assistant":
                display_sources(message.get("sources", []))

    question = st.chat_input(
        "Ask a Class 10 Science question...",
        key="science_chat_input"
    )

    if question:
        st.session_state.messages.append({
            "role": "user",
            "content": question
        })

        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Searching Science sources..."):
                try:
                    response = answer_question(question)

                    if isinstance(response, dict):
                        answer = response.get("answer", "No answer returned.")
                        sources = response.get("sources", [])
                    else:
                        answer = str(response)
                        sources = []

                except Exception as error:
                    answer = f"Error while answering: {error}"
                    sources = []

            st.markdown(answer)
            display_sources(sources)

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "sources": sources
        })

    if st.button("🗑️ Clear Science Chat"):
        st.session_state.messages = []
        st.rerun()


# ==================================================
# TAB 2: PRACTICE QUESTIONS
# ==================================================

with practice_tab:
    st.header("📝 Practice Questions")

    with st.form("practice_form"):
        topic = st.text_input(
            "Science topic",
            placeholder="e.g., Electricity, Heredity"
        )

        difficulty = st.selectbox(
            "Difficulty",
            ["mixed", "easy", "medium", "hard"]
        )

        count = st.slider("Number of questions", 1, 10, 5)

        generate = st.form_submit_button("✨ Generate Questions")

    if generate:
        if not topic.strip():
            st.warning("Please enter a topic.")
        else:
            with st.spinner("Generating questions..."):
                try:
                    result = generate_practice_questions(
                        topic=topic,
                        difficulty=difficulty,
                        count=count
                    )
                except Exception as error:
                    result = {"questions": [], "error": str(error)}

            if result.get("error"):
                st.error(result["error"])
            else:
                questions = result.get("questions", [])

                if not questions:
                    st.warning("No questions were generated.")
                else:
                    st.success(f"Generated {len(questions)} questions.")

                    for index, item in enumerate(questions, start=1):
                        with st.expander(
                            f"Question {index}: {item.get('question', '')}",
                            expanded=(index == 1)
                        ):
                            st.caption(
                                f"{item.get('type', 'Practice')} · "
                                f"{item.get('difficulty', difficulty).title()}"
                            )

                            for option in item.get("options", []):
                                st.markdown(f"- {option}")

                            with st.expander("Show answer and explanation"):
                                st.markdown(
                                    f"**Answer:** {item.get('answer', 'Not provided')}"
                                )
                                st.markdown(
                                    f"**Explanation:** "
                                    f"{item.get('explanation', 'Not provided')}"
                                )

                    display_sources(result.get("sources", []))


# ==================================================
# TAB 3: YOUTUBE LEARNING
# ==================================================

with youtube_tab:
    st.header("▶️ YouTube Learning")

    with st.form("youtube_search_form"):
        youtube_topic = st.text_input(
            "Science topic",
            placeholder="e.g., Electricity, Heredity"
        )

        video_count = st.slider(
            "Number of videos",
            1,
            10,
            6,
            key="youtube_video_count"
        )

        search_videos = st.form_submit_button("🔍 Search YouTube")

    if search_videos:
        if not youtube_topic.strip():
            st.warning("Please enter a topic.")
        else:
            with st.spinner("Searching YouTube..."):
                try:
                    result = search_youtube_videos(
                        youtube_topic,
                        max_results=video_count
                    )
                except Exception as error:
                    result = {"videos": [], "error": str(error)}

            if result.get("error"):
                st.error(result["error"])
            else:
                videos = result.get("videos", [])

                if not videos:
                    st.info("No videos found.")
                else:
                    st.success(f"Found {len(videos)} videos.")
                    columns = st.columns(2)

                    for index, video in enumerate(videos):
                        with columns[index % 2]:
                            with st.container(border=True):
                                if video.get("thumbnail"):
                                    st.image(
                                        video["thumbnail"],
                                        use_container_width=True
                                    )

                                st.subheader(video.get("title", "Untitled"))
                                st.caption(
                                    "Channel: "
                                    + video.get("channel", "Unknown")
                                )

                                if video.get("description"):
                                    st.write(video["description"][:250])

                                if video.get("url"):
                                    st.link_button(
                                        "▶️ Watch on YouTube",
                                        video["url"],
                                        use_container_width=True
                                    )


# ==================================================
# TAB 4: PDF QUESTION ANSWERING
# ==================================================

with pdf_tab:
    st.header("📄 Upload a PDF and Ask Questions")

    st.write(
        "Answer a specific question or process the entire question paper."
    )

    uploaded_pdf = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"],
        key="document_pdf_upload"
    )

    if uploaded_pdf is not None:
        pdf_bytes = uploaded_pdf.getvalue()
        document_hash = hashlib.sha256(pdf_bytes).hexdigest()
        document_key = f"{uploaded_pdf.name}:{document_hash}"

        st.success(
            f"Uploaded: {uploaded_pdf.name} "
            f"({len(pdf_bytes) / 1024:.1f} KB)"
        )

        st.caption(
            "Uploaded documents are processed for question answering "
            "and are not added to your permanent ChromaDB collection."
        )

        # Whole-document processing
        st.subheader("📝 Answer All Questions")

        if st.button(
            "Answer All Questions in PDF",
            key="answer_all_pdf_questions"
        ):
            with st.spinner(
                "Processing all readable pages in batches. Please wait..."
            ):
                result = answer_all_pdf_questions(
                    pdf_bytes,
                    pages_per_batch=3
                )

            if result.get("error"):
                st.error(result["error"])

            if result.get("answer"):
                st.session_state[
                    f"all_pdf_answer_{document_hash}"
                ] = result

        whole_answer = st.session_state.get(
            f"all_pdf_answer_{document_hash}"
        )

        if whole_answer and whole_answer.get("answer"):
            st.subheader("Answers to the Question Paper")
            st.markdown(whole_answer["answer"])

            display_sources(
                whole_answer.get("sources", []),
                title="📚 Pages processed"
            )

        st.divider()

        # Single-question mode
        st.subheader("💬 Ask a Specific Question")

        if "pdf_qa_history" not in st.session_state:
            st.session_state.pdf_qa_history = {}

        if document_key not in st.session_state.pdf_qa_history:
            st.session_state.pdf_qa_history[document_key] = []

        for item in st.session_state.pdf_qa_history[document_key]:
            with st.chat_message("user"):
                st.markdown(item["question"])

            with st.chat_message("assistant"):
                st.markdown(item["answer"])
                display_sources(item["sources"], "📚 PDF page references")

        pdf_question = st.chat_input(
            "Ask about the uploaded PDF...",
            key="pdf_question_input"
        )

        if pdf_question:
            with st.chat_message("user"):
                st.markdown(pdf_question)

            with st.chat_message("assistant"):
                with st.spinner("Finding relevant passages..."):
                    try:
                        result = answer_pdf_question(
                            pdf_question,
                            pdf_bytes
                        )
                    except Exception as error:
                        result = {
                            "answer": "",
                            "sources": [],
                            "error": str(error)
                        }

                if result.get("error"):
                    st.error(result["error"])
                else:
                    answer = result.get("answer", "")
                    sources = result.get("sources", [])

                    st.markdown(answer)
                    display_sources(sources, "📚 PDF page references")

                    st.session_state.pdf_qa_history[document_key].append({
                        "question": pdf_question,
                        "answer": answer,
                        "sources": sources
                    })

    else:
        st.info("Upload a PDF to start.")


# ==================================================
# FOOTER
# ==================================================

st.divider()

st.caption(
    "Science RAG Tutor | NCERT • PYQs • Practice Questions • "
    "YouTube Learning • PDF Question Answering"
)
