import streamlit as st
import openai
from openai import OpenAI

# Initialize the OpenAI client
client = OpenAI()

# Streamlit UI for user to upload file and ask questions
st.title("Legal Document Q&A")

# File upload section
uploaded_files = st.file_uploader("Upload PDF files", type="pdf", accept_multiple_files=True)
count=0
if uploaded_files:
    # Ready the files for upload to OpenAI
    file_streams = uploaded_files

    # Create a vector store
    vector_store = client.beta.vector_stores.create(name="User Uploaded Documents")

    # Upload files and poll status
    file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
        vector_store_id=vector_store.id, files=file_streams
    )

    # Check the status
    if file_batch.status == 'completed':
        st.write("Files uploaded successfully and added to the vector store." ,count )
        count+=1

        # Create an assistant to answer questions
        assistant = client.beta.assistants.create(
            name="Legal Analyst",
            instructions="You are a world class legal analyst.",
            tools=[{"type": "file_search"}],
            model="gpt-4o",
        )

        # Update the assistant to use the vector store
        assistant = client.beta.assistants.update(
            assistant_id=assistant.id,
            tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
        )

        # Save vector store and assistant ID for future use
        st.session_state.vector_store_id = vector_store.id
        st.session_state.assistant_id = assistant.id
        st.write("Vector store and assistant created successfully. You can now ask questions.")
    else:
        st.write("Error uploading the files. Please try again.")

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
            st.write(message_content.value)
        else:
            st.write("No response available from the assistant.")
