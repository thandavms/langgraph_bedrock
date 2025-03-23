# Langgraph with Amazon Bedrock

Notebooks for learning langgraph agents patterns and using it with Amazon Bedrock - Models, Knowledge bases and Agents 

## Prerequisites

- AWS Account with appropriate permissions
- Python 3.x
- Git

## Setup Instructions

### 1. Create Bedrock Knowledge Base
- Navigate to the `bedrock_resources` folder
- Follow the setup instructions for Amazon Bedrock knowledge base configuration

### 2. Clone the Repository
```console
git clone <repository-url>
cd <project-directory>
```

### 3.  Install Dependencies

- go to the dependencies directory and install the dependencies

```python
pip install -r requirements.txt
```

### 4.  Configuration
1.  Rename env.tmp to .env
2.  Update the .env file with your credentials:

```python
AWS_REGION=your_region
TAVILY_API_KEY="Create an Tavily API key by logging in to tavily"
MODEL_ID = "bedrock model id to use"
AWS_REGION="AWS region to use"
BEDROCK_KB_ID="Bedrock knowledge base ID createed in set up instructions
BEDROCK_AGENT_ID = 
BEDROCK_AGENT_ALIAS_ID =
```

### Project Structure

```python
project/
├── bedrock_resources/    # Bedrock configuration files
├── dependencies/         # Project dependencies
└── langgraph_agents     # Notebooks
└── data                 # sample database and document 
```

