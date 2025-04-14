import streamlit as st
import boto3
import json
import uuid
import os
from dotenv import load_dotenv

# Set up the page configuration
st.set_page_config(
    page_title="Bedrock Agent Interface",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_dotenv()
agentid = os.environ.get("AGENT_ID")
agentalias = os.environ.get("AGENT_ALIAS")

# Initialize session state variables if they don't exist
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "trace_data" not in st.session_state:
    st.session_state.trace_data = None

# Sidebar for configuration
st.sidebar.title("Configuration")
region = st.sidebar.text_input("AWS Region", "us-west-2")
agent_id = st.sidebar.text_input("Agent ID", agentid)
agent_alias_id = st.sidebar.text_input("Agent Alias ID", agentalias)

# Initialize Bedrock Agent Runtime client
@st.cache_resource
def get_bedrock_agent_client(region_name):
    return boto3.client('bedrock-agent-runtime', region_name=region_name)

# Main app layout
st.title("Bedrock Agent Interface")

# Create two columns for chat and trace
col1, col2 = st.columns([3, 2])

with col1:
    st.header("Conversation")
    # Display chat messages
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

# Chat input
if prompt := st.chat_input("Ask the agent something..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with col1:
        with st.chat_message("user"):
            st.write(prompt)
        
        # Display assistant response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            # Invoke the agent
            if agent_id and agent_alias_id:
                try:
                    client = get_bedrock_agent_client(region)
                    
                    # Make sure to properly set enableTrace parameter
                    response = client.invoke_agent(
                        agentId=agent_id,
                        agentAliasId=agent_alias_id,
                        sessionId=st.session_state.session_id,
                        inputText=prompt,
                        enableTrace=False
                    )
                    
                    # Debug: Show response keys
                    response_keys = list(response.keys())
                    st.sidebar.write(f"Response keys: {response_keys}")
                    
                    # Process the streaming response
                    for event in response.get('completion'):
                        # Handle text chunks
                        if 'chunk' in event:
                            chunk_data = event['chunk'].get('bytes', b'').decode('utf-8')
                            full_response += chunk_data
                            message_placeholder.markdown(full_response + "▌")
                    
                    # Final update without the cursor
                    message_placeholder.markdown(full_response)
                    
                    # Add assistant message to chat history
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                
                except Exception as e:
                    st.error(f"Error invoking agent: {str(e)}")
                    message_placeholder.markdown(f"Error: {str(e)}")
            else:
                message_placeholder.markdown("Please provide Agent ID and Agent Alias ID in the sidebar.")

# Add a button to start a new conversation
with col1:
    if st.button("Start New Conversation"):
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.trace_data = None
        st.rerun()