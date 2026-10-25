
import streamlit as st

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama

st.set_page_config(
    page_title="AI Study Assistant",
    page_icon="📚",
    layout="centered"
)

st.image(
    "D:\AI_Projects\AI_Study_Assistant\assets\chatbot.jpg",
    width=250)

st.title("📚 AI Study Assistant")
st.write("Learn concepts, practise interview questions, and solve puzzles.")


@st.cache_resource
def load_model():
    return ChatOllama(
        model="qwen2.5:1.5b",
        temperature=0.3
    )


model = load_model()
output_parser = StrOutputParser()


study_modes = {
    "Simple Explanation": (
        "Explain the topic in simple English for a beginner. "
        "Use a short definition and an easy example."
    ),

    "Summary": (
        "Summarize the provided topic or text. "
        "Include only the main points and use clear bullet points."
    ),

    "Step-by-Step Explanation": (
        "Explain the topic step by step in a logical order. "
        "Use simple English and a small example."
    ),

    "Practical Examples": (
        "Explain the topic using at least three practical, "
        "real-world examples. Briefly explain each example."
    ),

    "Interview Questions": (
        "Generate five relevant interview questions about the topic "
        "and provide a clear answer to each question."
    )
}


st.header("Study Mode")

selected_mode = st.selectbox(
    "Choose a learning mode",
    list(study_modes.keys())
)

user_input = st.text_area(
    "Enter a topic or paste your text",
    placeholder="Example: Machine Learning",
    height=120
)

if st.button("Generate Study Content", type="primary"):

    if not user_input.strip():
        st.warning("Please enter a topic or some text.")

    else:
        study_prompt = PromptTemplate.from_template(
            """You are a helpful AI Study Assistant.

Follow these instructions:
{mode_instruction}

Topic or text:
{user_input}

Give an accurate, well-organized answer.
"""
        )

        study_chain = study_prompt | model | output_parser

        try:
            with st.spinner("Preparing your study content..."):
                result = study_chain.invoke({
                    "mode_instruction": study_modes[selected_mode],
                    "user_input": user_input.strip()
                })

            st.session_state.study_result = result
            st.session_state.study_mode = selected_mode

        except Exception as e:
            st.error(
                "Could not connect to Ollama. "
                "Check that Ollama is running and the model is installed."
            )
            st.caption(str(e))


if "study_result" in st.session_state:
    st.subheader(st.session_state.study_mode)
    st.markdown(st.session_state.study_result)


st.divider()
st.header("🧩 Puzzle Mode")
st.write("Generate a puzzle, submit your answer, and get feedback.")

puzzle_type = st.selectbox(
    "Choose a puzzle type",
    [
        "Logic Puzzle",
        "Riddle",
        "Math Puzzle",
        "General Knowledge Puzzle"
    ]
)

puzzle_difficulty = st.select_slider(
    "Choose difficulty",
    options=["Easy", "Medium", "Hard"],
    value="Easy"
)


if st.button("Generate Puzzle"):

    puzzle_prompt = PromptTemplate.from_template(
        """You are a puzzle creator.

Create one original {difficulty} {puzzle_type}.
Make sure it has a clear, correct, and unambiguous answer.
Do not reveal the answer or solution.
Give only the puzzle and the information needed to solve it.
"""
    )

    puzzle_chain = puzzle_prompt | model | output_parser

    try:
        with st.spinner("Creating your puzzle..."):
            puzzle = puzzle_chain.invoke({
                "difficulty": puzzle_difficulty,
                "puzzle_type": puzzle_type
            })

        st.session_state.puzzle = puzzle
        st.session_state.puzzle_type = puzzle_type
        st.session_state.puzzle_difficulty = puzzle_difficulty
        st.session_state.puzzle_feedback = None
        st.session_state.user_puzzle_answer = ""

    except Exception as e:
        st.error("Could not generate a puzzle. Check your Ollama setup.")
        st.caption(str(e))



if "puzzle" in st.session_state:

    st.subheader("Your Puzzle")
    st.markdown(st.session_state.puzzle)

    user_puzzle_answer = st.text_input(
        "Enter your answer",
        key="user_puzzle_answer"
    )

    if st.button("Check My Answer"):

        if not user_puzzle_answer.strip():
            st.warning("Please enter your answer first.")

        else:
            checking_prompt = PromptTemplate.from_template(
                """You are a fair and helpful puzzle evaluator.

Puzzle:
{puzzle}

User's answer:
{user_answer}

Solve the puzzle yourself carefully before evaluating the user's answer.
Accept answers that are correct in meaning, even if the wording differs.
If the puzzle is ambiguous or has no clear answer, explain that honestly.

Give:
1. Result: Correct, Partially correct, or Incorrect.
2. Explanation: Explain the reasoning in simple English.
3. Correct answer: State the answer clearly.

Do not mark an answer correct unless it matches a valid solution.
"""
            )

            checking_chain = checking_prompt | model | output_parser

            try:
                with st.spinner("Checking your answer..."):
                    feedback = checking_chain.invoke({
                        "puzzle": st.session_state.puzzle,
                        "user_answer": user_puzzle_answer.strip()
                    })

                st.session_state.puzzle_feedback = feedback

            except Exception as e:
                st.error("Could not check your answer. Check your Ollama setup.")
                st.caption(str(e))


if st.session_state.get("puzzle_feedback"):
    st.subheader("Puzzle Feedback")
    st.markdown(st.session_state.puzzle_feedback)
