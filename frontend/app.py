import streamlit as st
import requests

st.title("📘 Bangla AI Teacher")

# Input
query = st.text_input("Enter your question:")

# Initialize conversation history state if not present
if "full_history" not in st.session_state:
    st.session_state.full_history = []

# Submit
if st.button("Ask") and query:
    try:
        response = requests.post("http://localhost:8000/process-pdf/rag-query", json={"req": query})
        if response.status_code == 200:
            data = response.json()
            answer = data.get("answer", "")
            history = data.get("history", [])

            # Update session state with history from backend
            st.session_state.full_history = history

            st.markdown(f"**Answer:** {answer}")
        else:
            st.error(f"Error: {response.text}")
    except Exception as e:
        st.error(f"Request failed: {e}")

# Show conversation history
if st.session_state.full_history:
    st.markdown("---")
    st.subheader("🗃️ Conversation History:")
    for idx, turn in enumerate(st.session_state.full_history):
        st.markdown(f"**Q{idx+1}:** {turn['question']}")
        st.markdown(f"**A{idx+1}:** {turn['answer']}")
