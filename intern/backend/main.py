import streamlit as st
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Title of the Streamlit app
st.title("NL2SQL Chatbot with Custom Model")

# Load your custom model and tokenizer
model_name = "charanhu/text_to_sql_5"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.container():
        st.markdown(f"{message['role']}: {message['content']}")

# Accept user input
if prompt := st.text_input("Ask a question"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Process user input with your custom model for SQL generation
    with st.spinner("Generating SQL query..."):
        inputs = tokenizer(prompt, return_tensors="pt")
        outputs = model.generate(**inputs)
        generated_sql = tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]

        # Display assistant response in chat message container
        st.session_state.messages.append({"role": "assistant", "content": generated_sql})
        st.markdown(f"Assistant: {generated_sql}")