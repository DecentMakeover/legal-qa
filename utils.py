import streamlit as st
import openai
from openai import OpenAI
count = 0
# Initialize the OpenAI client
client = OpenAI()

# Streamlit UI for user to upload file and ask questions
st.title("Legal Document Q&A")

uploaded_files = st.file_uploader("Upload PDF files", type="pdf", accept_multiple_files=True)
question = st.text_input("Ask a question about the documents")

if uploaded_files and question:
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
        st.write("Files uploaded successfully and added to the vector store.")

        # Create an assistant to answer the question
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

        # Upload the user provided files to OpenAI for further analysis
        message_files = [
            client.files.create(file=file, purpose="assistants") for file in uploaded_files
        ]

        # Create a thread and attach the files to the message
        thread = client.beta.threads.create(
            messages=[
                {
                    "role": "user",
                    "content": question,
                    "attachments": [
                        {"file_id": message_file.id, "tools": [{"type": "file_search"}]} for message_file in message_files
                    ],
                }
            ]
        )

        # Run the assistant and get the response
        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id, assistant_id=assistant.id
        )

        # Retrieve the messages from the thread
        messages = list(client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))

        # Display the response to the user
        if messages:
            message_content = messages[0].content[0].text if isinstance(messages[0].content, list) else messages[0].content
            st.write(message_content)
            print(count)
            count+=1
        else:
            st.write("No response available from the assistant.")
    else:
        st.write("Error uploading the files. Please try again.")
