import streamlit as st
import boto3
import uuid
import json
from dotenv import load_dotenv
import os

# Set page title
st.set_page_config(page_title="Bedrock Knowledge Base Q&A")

# Initialize session state for conversation history
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

load_dotenv()
kb_id = os.environ.get("KNOWLEDGE_BASE")
modelarn = os.environ.get("MODEL_ARN")

# Initialize Bedrock client
@st.cache_resource
def get_bedrock_client():
    return boto3.client('bedrock-agent-runtime', region_name = 'us-west-2')

# Function to query the knowledge base
def query_knowledge_base(query, session_id):
    client = get_bedrock_client()
    
    try:

        response = client.retrieve_and_generate(
            input={
                "text": query
            },
            retrieveAndGenerateConfiguration={
                "type": "KNOWLEDGE_BASE",
                "knowledgeBaseConfiguration": {
                    'knowledgeBaseId': st.session_state.kb_id,
                    "modelArn": st.session_state.model_arn,
                    "retrievalConfiguration": {
                        "vectorSearchConfiguration": {
                            "numberOfResults":5
                        } 
                    }
                }
            }
        )
        
        # Extract the response text
        response_text = response['output']['text']
        citations = []
        
        # Extract citations if available
        if 'citations' in response:
            for citation in response['citations']:
                citations.append({
                    'retrievedReferences': citation.get('retrievedReferences', [])
                })
        
        return response_text, citations
    except Exception as e:
        return f"Error: {str(e)}", []

# Sidebar for configuration
with st.sidebar:
    st.title("Configuration")
    st.session_state.kb_id = st.text_input("Knowledge Base ID", key="kb_id_input", value=kb_id)
    st.session_state.model_arn = st.text_input("Model ARN", key="model_arn_input", 
                                              value=modelarn)
    
    if st.button("New Conversation"):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.conversation_history = []
        st.success(f"Started new conversation with session ID: {st.session_state.session_id}")
    
    st.divider()
    st.write(f"Current Session ID: {st.session_state.session_id}")

# Main app
st.title("Bedrock Knowledge Base Q&A")

# Display conversation history
for i, (q, a) in enumerate(st.session_state.conversation_history):
    st.text_area(f"Question {i+1}", q, height=68, disabled=True)
    st.text_area(f"Answer {i+1}", a, height=150, disabled=True)
    st.divider()

# Input for new question
query = st.text_area("Ask a question:", height=100)

if st.button("Submit"):
    if not st.session_state.kb_id:
        st.error("Please enter a Knowledge Base ID in the sidebar.")
    elif not st.session_state.model_arn:
        st.error("Please enter a Model ARN in the sidebar.")
    elif not query:
        st.error("Please enter a question.")
    else:
        with st.spinner("Getting answer..."):
            answer, citations = query_knowledge_base(query, st.session_state.session_id)
            
            # Add to conversation history
            st.session_state.conversation_history.append((query, answer))
            
            # Display the new answer
            st.text_area("Question", query, height=68, disabled=True)
            st.text_area("Answer", answer, height=150, disabled=False)
            
            # Display citations if available
            if citations:
                st.write("Citations:")
                st.json(citations)
