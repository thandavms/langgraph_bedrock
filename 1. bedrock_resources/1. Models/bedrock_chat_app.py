import streamlit as st
import boto3
import json

# Initialize Streamlit app
st.title("Bedrock Chat App")

# Initialize session state for conversation history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar for model selection and parameters
with st.sidebar:
    st.header("Model Settings")
    model_option = st.selectbox(
        "Select Model",
        ["us.amazon.nova-pro-v1:0", "us.anthropic.claude-3-5-sonnet-20240620-v1:0"],
        format_func=lambda x: "Amazon Nova Pro" if "nova" in x else "Claude 3.5 Sonnet"
    )
    
    max_tokens = st.slider("Max Tokens", 100, 4000, 2000)
    temperature = st.slider("Temperature", 0.0, 1.0, 0.0, 0.1)
    top_p = st.slider("Top P", 0.0, 1.0, 0.9, 0.1)
    
    # Region selection
    region = st.text_input("AWS Region", "us-west-2")
    
    st.markdown("---")
    st.caption("A simple chat interface for Amazon Bedrock models")

# Initialize Bedrock client
@st.cache_resource
def get_bedrock_client(region_name):
    return boto3.client(service_name='bedrock-runtime', region_name=region_name)

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Get user input
user_input = st.chat_input("Type your message here...")

if user_input:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Display user message
    with st.chat_message("user"):
        st.write(user_input)
    
    # Prepare messages for Bedrock API
    bedrock_messages = []
    for msg in st.session_state.messages:
        role = "user" if msg["role"] == "user" else "assistant"
        bedrock_messages.append({
            "role": role,
            "content": [{"text": msg["content"]}]
        })
    
    # Display assistant thinking indicator
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking...")
        
        try:
            # Get Bedrock client
            bedrock_runtime = get_bedrock_client(region)
            
            # Call Bedrock API
            response = bedrock_runtime.converse(
                modelId=model_option,
                messages=bedrock_messages,
                inferenceConfig={
                    "temperature": temperature,
                    "maxTokens": max_tokens,
                    "topP": top_p
                }
            )
            
            # Extract response
            result = response['output']['message']['content'][0]['text']
            
            # Update placeholder with response
            message_placeholder.markdown(result)
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": result})
            
        except Exception as e:
            message_placeholder.markdown(f"Error: {str(e)}")
