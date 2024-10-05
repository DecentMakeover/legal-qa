import streamlit as st
import openai
from openai import OpenAI

# Initialize the OpenAI client
client = OpenAI()

# Streamlit UI for user to ask questions
st.title("Legal Document Q&A")

# Question asking section
if "assistant_id" in st.session_state and "vector_store_id" in st.session_state:
    question = st.text_input("Ask a question about the documents")
    if question:
        # Create a thread and ask the question
        thread = client.beta.threads.create(
            messages=[
                {
                    "role": "user",
                    "content": question,
                    "attachments": []
                }
            ]
        )

        # Run the assistant and get the response
        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id, assistant_id=st.session_state.assistant_id
        )

        # Retrieve the messages from the thread
        messages = list(client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))

        # Display the response to the user
        if messages:
            message_content = messages[0].content[0].text if isinstance(messages[0].content, list) else messages[0].content
            st.write("Answer:")
            st.json(message_content)
        else:
            st.write("No response available from the assistant.")
else:
    st.write("Please upload and index the files first using the upload_and_index.py script.")
