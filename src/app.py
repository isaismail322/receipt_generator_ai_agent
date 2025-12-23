# app.py
import streamlit as st
from main import ask_agent_sync

st.set_page_config(page_title="GitHub Agent Chatbot", page_icon=":robot:")
st.title("GitHub Agent Chatbot")
st.write("Chat with the GitHub agent about GitHub repositories!")

# Initialize chat session
if "messages" not in st.session_state:
    st.session_state.messages = []

if "history" not in st.session_state:
    st.session_state.history = None

# Display chat history
for msg in st.session_state.messages:
    role = msg["role"]
    content = msg["content"]
    with st.chat_message(role):
        st.markdown(content)

# User input
if prompt := st.chat_input("Type your message..."):
    # Append user message
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Typing...")

    # Call agent
    response = ask_agent_sync(prompt, st.session_state.history)
    st.session_state.history = response["history"]

    # Append agent response
    st.session_state.messages.append({"role": "assistant", "content": response["output"]})
        
    # Replace placeholder with actual response
    message_placeholder.markdown(response["output"])

#    st.experimental_rerun()


# -----------------------
# Footer / credits
# -----------------------
st.markdown("---")
st.markdown(
    "Created with :heart: using **Streamlit** and **Airbyte GitHub Agent**."
)