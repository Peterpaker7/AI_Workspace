import streamlit as st
from crewai import LLM, Agent, Crew, Task

MODEL = "llama3.2:1b"
BASE_URL = "http://localhost:11434"

st.set_page_config(page_title="Ask the Agent", page_icon="pencil")
st.title("Ask the Agent")
st.caption("One CrewAI agent on a local model. Nothing leaves this machine.")

if st.sidebar.button("Clear chat"):
    st.session_state.messages = []

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    st.chat_message(message["role"]).markdown(message["content"])

question = st.chat_input("Ask anything")

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    st.chat_message("user").markdown(question)

    llm = LLM(
        model="ollama/" + MODEL,
        base_url=BASE_URL,
        temperature=0.7,
        max_tokens=600,   
    )

    agent = Agent(
        role="Helpful Assistant",
        goal="Answer the question clearly and get to the point.",
        backstory=(
            "You explain things in plain words, use concrete examples, and "
            "stop once the question is answered. You always reply in English, "
            "whatever language the question hints at."
        ),
        llm=llm,
        allow_delegation=False,
        max_iter=3,
        verbose=False,
    )

    history = "\n".join(
        "%s: %s" % (m["role"], m["content"]) for m in st.session_state.messages[-7:-1]
    )
    task = Task(
        description=(
            ("Earlier conversation:\n%s\n\n" % history if history else "")
            + "Answer this question: %s\n\n"
            "Answer in English. Answer directly, with no preamble." % question
        ),
        expected_output="A clear, direct answer.",
        agent=agent,
    )

    crew = Crew(agents=[agent], tasks=[task], verbose=False)

    with st.chat_message("assistant"):
        with st.spinner("Thinking"):
            try:
                answer = str(crew.kickoff())
            except Exception as exc:
                answer = (
                    "That failed: %s\n\nIs `ollama serve` running and is "
                    "`%s` pulled?" % (exc, MODEL)
                )
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})