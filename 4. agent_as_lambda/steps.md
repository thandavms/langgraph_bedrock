

### Set Up Your Project Directory

```python
mkdir langgraph-sam
cd langgraph-sam
```

### Create the Lambda Function Code

Create a requirements.txt file in the same directory with the dependencies:
```python
langchain
langchain_community
langchain_aws
langgraph
python-dotenv
pydantic
```

### Create a file named template.yaml with the following content:

Handler: Points to lambda_function.lambda_handler.
Runtime: Python 3.11 (adjust if you need a different version).
Architectures: x86_64 (default; use arm64 if preferred).
CodeUri: . means the current directory contains the code and requirements.txt.
Policies: Adds execution permissions (e.g., Bedrock, CloudWatch Logs).

### Build and Deploy Lambda

Run the SAM build command to package your function and dependencies:
Deploy the built application to AWS:

```python
sam build

sam deploy --guided
```

### Run the application

Review the .env file to ensure the new lambda function is entered
Run the streamlit app under app/app.py

```python
streamlit run app.py
```
