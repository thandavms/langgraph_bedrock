import os
from typing import TypedDict
import boto3
from langchain_aws import ChatBedrock
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv

load_dotenv()

# Load environment variables with defaults
model_id = os.environ.get('MODEL_ID')
if not model_id:
    raise ValueError("MODEL_ID environment variable is not set")

aws_region = os.environ.get('AWS_REGION')
bedrock_kb_id = os.environ.get('BEDROCK_KB_ID')
if not bedrock_kb_id:
    print("Warning: BEDROCK_KB_ID environment variable is not set. Knowledge base queries will fail.")

# Initialize the LLM only if model_id is available
llm = ChatBedrock(model=model_id) if model_id else None

# Define the state schema
class State(TypedDict):
    query: str
    web_search: str
    kb_search: str
    final_blog: str

# Initialize the LLM
llm = ChatBedrock(model=model_id)

def search_web(state: State):
    """Search the web for information related to the query."""
    search_tool = TavilySearchResults(max_results=2)
    web_results = search_tool.invoke(state["query"])
    return {"web_search": web_results}

def query_knowledge_base(state: State):
    """Query the knowledge base for information related to the query."""
    bedrock_agent = boto3.client('bedrock-agent-runtime', region_name=aws_region)

    query_text = f"""
    {state["query"]}
    
    If you don't have relevant information from the knowledge base to answer this query,
    please respond with exactly: "Sorry I do not have information on this topic."
    """

    response = bedrock_agent.retrieve_and_generate(
        input={
            "text": query_text
        },
        retrieveAndGenerateConfiguration={
            "type": "KNOWLEDGE_BASE",
            "knowledgeBaseConfiguration": {
                "knowledgeBaseId": bedrock_kb_id,
                "modelArn": model_id,
                "retrievalConfiguration": {
                    "vectorSearchConfiguration": {
                        "numberOfResults": 5
                    }
                }
            }
        }
    )

    kb_results = response['output']['text']
    print(kb_results)
    return {"kb_search": kb_results}

def blogger(state: State):
    """Create a blog post based on the search results."""
    if 'web_search' in state and state['web_search']:
        prompt = f"""Your job is to create a blog title and a one paragraph blog from this content: {state['web_search']}"""
    else:
        prompt = f"""Your job is to create a blog title and a one paragraph blog from this content: {state['kb_search']}"""

    final_answer = llm.invoke(prompt)           
    return {"final_blog": final_answer.content}

def conditional_node(state: State):
    """Determine whether to use KB results or search the web."""
    condition = "Sorry" 
    if condition in state['kb_search']:
        return "fail"
    else:
        return "pass"

def create_agent():
    """Create and compile the agent graph."""
    # Build workflow
    chainer = StateGraph(State)

    # Add nodes
    chainer.add_node("search_kb", query_knowledge_base)
    chainer.add_node("search_web", search_web)
    chainer.add_node("blog_writer", blogger)

    # Add edges to connect nodes
    chainer.add_edge(START, "search_kb")
    chainer.add_conditional_edges("search_kb", conditional_node, {"pass": "blog_writer", "fail": "search_web"})
    chainer.add_edge("search_web", "blog_writer")
    chainer.add_edge("blog_writer", END)

    # Compile the graph
    return chainer.compile()

def run_agent(query: str):
    """Run the agent with the given query."""
    agent = create_agent()
    state = agent.invoke({"query": query})
    return state['final_blog']
