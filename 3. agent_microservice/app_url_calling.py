import streamlit as st
import requests
import json

# Set page title
st.title("LangGraph Agent App")

# Create a text input for the query
query = st.text_area("Enter your blog topic:", height=100)

# Create a button to submit the query
if st.button("Generate Blog"):
    if query:
        # Show a spinner while waiting for the response
        with st.spinner("Generating blog..."):
            try:
                # Make a POST request to the FastAPI server
                response = requests.post(
                    "http://localhost:8000/agent/run",
                    json={"query": query},
                    headers={"Content-Type": "application/json"}
                )
                
                # Check if the request was successful
                if response.status_code == 200:
                    data = response.json()
                    if data["status"] == "success":
                        st.subheader("Generated Blog")
                        st.write(data["blog_content"])
                    else:
                        st.error(f"Error: {data['message']}")
                else:
                    st.error(f"Error: HTTP {response.status_code} - {response.text}")
            except Exception as e:
                st.error(f"Error connecting to the server: {str(e)}")
    else:
        st.warning("Please enter a query first.")

# Add a small footer
st.markdown("---")
st.caption("LangGraph Agent Microservice")
