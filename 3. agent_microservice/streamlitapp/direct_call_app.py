import streamlit as st
import sys
import os

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.title("LangGraph Agent App")

# Create a text input for the query
query = st.text_area("Enter your blog topic:", height=100)

# Create a button to submit the query
if st.button("Generate Blog"):
    if query:
        # Show a spinner while waiting for the response
        with st.spinner("Generating blog..."):
            try:
                # Import the agent only when needed
                from service.agent import run_agent
                
                # Call the agent function
                blog_content = run_agent(query)
                
                # Display the result
                st.subheader("Generated Blog")
                st.write(blog_content)
            except Exception as e:
                st.error(f"Error generating blog: {str(e)}")
                st.error(f"Error details: {type(e).__name__}")
                import traceback
                st.code(traceback.format_exc())
    else:
        st.warning("Please enter a query first.")

# Add a small footer
st.markdown("---")
st.caption("Powered by LangGraph Agent")