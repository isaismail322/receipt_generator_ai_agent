import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
# app.py
from main import ask_agent_sync
# from pdf_generator import pdf_receipt_generator

st.set_page_config(page_title="Receipt Generator Agent", page_icon=":robot:")
st.title("Receipt Chatbot")
st.write("Chat with the Receipt agent about Receipts")

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
    # message_placeholder.markdown(response)
    # response

    tool_data = []
    for entry in response["history"]:
        if entry.__class__.__name__ == "ModelRequest":
            for parts in entry.parts:
                if parts.__class__.__name__ == "ToolReturnPart":
                    if parts.tool_name == "fetch_records":
                        tool_data.extend(parts.content)
                        # print(parts.content)



    # 
    # for entry in response.get("history", []):
    #     model_response = getattr(entry, "model_response", None)
    #     if model_response:
    #         for part in getattr(model_response, "parts", []):
    #             if part.__class__.__name__ == "ToolReturnPart":
    #                 tool_data.extend(part.content)  # This is your Airtable records

    if tool_data:  # Only if the tool returned data
        pdf_buffer = pdf_receipt_generator(tool_data)
        st.download_button(
            label="📄 Download Receipt",
            data=pdf_buffer,
            file_name="trip_receipt.pdf",
            mime="application/pdf"
        )


    # Test the pdf_generator separately
# if st.button("Test PDF Generation"):
#     test_data = {
#         "trip_id": "12345",
#         "passenger_name": "John Doe",
#         "pickup": "123 Main St",
#         "dropoff": "456 Oak Ave",
#         "fare": "$25.00",
#         "date": "2025-01-01"
#         }
    
#     try:
#         pdf_buffer = pdf_receipt_generator(test_data)
#         st.download_button(
#             label="📄 Download Test Receipt",
#             data=pdf_buffer,
#             file_name="test_receipt.pdf",
#             mime="application/pdf"
#         )
#     except Exception as e:
#         st.error(f"PDF generation error: {str(e)}")

#    st.experimental_rerun()


# -----------------------
# Footer / credits
# -----------------------
st.markdown("---")
st.markdown(
    "Created with :heart: using **Streamlit** and **Airbyte**."
)