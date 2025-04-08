import streamlit as st
import boto3
import json
import os

st.title("LangGraph Agent App")

# Create a text input for the query
query = st.text_area("Enter your blog topic:", height=100)

# Get Lambda function name from environment variable or use a default
#lambda_function_name='samapp-LangGraphFunction-ozFd6cPWEidZ'

lambda_function_name = os.environ.get("LAMBDA_FUNCTION")
aws_region = os.environ.get('AWS_REGION', 'us-west-2')

# Create a button to submit the query
if st.button("Generate Blog"):
    if query:
        # Show a spinner while waiting for the response
        with st.spinner("Generating blog..."):
            try:
                # Initialize Lambda client
                lambda_client = boto3.client('lambda', region_name=aws_region)
                
                # Prepare the payload for Lambda
                payload = {
                    "query": query
                }
                
                # Invoke the Lambda function
                response = lambda_client.invoke(
                    FunctionName=lambda_function_name,
                    InvocationType='RequestResponse',
                    Payload=json.dumps(payload)
                )
                
                # Parse the response
                response_payload = json.loads(response['Payload'].read().decode('utf-8'))
                
                if 'statusCode' in response_payload and response_payload['statusCode'] == 200:
                    blog_content = response_payload['body']
                    
                    # Display the result
                    st.subheader("Generated Blog")
                    st.write(blog_content)
                else:
                    st.error(f"Error from Lambda function: {response_payload}")
                    
            except Exception as e:
                st.error(f"Error generating blog: {str(e)}")
                st.error(f"Error details: {type(e).__name__}")
                import traceback
                st.code(traceback.format_exc())
    else:
        st.warning("Please enter a query first.")

# Add a small footer
st.markdown("---")
st.caption("Powered by LangGraph Agent on AWS Lambda")