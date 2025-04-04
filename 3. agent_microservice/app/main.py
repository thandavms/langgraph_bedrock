from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import traceback
import logging

from app.agent import run_agent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="LangGraph Agent API",
    description="API for running a LangGraph agent for Prompt Chaining",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class QueryRequest(BaseModel):
    """Request model for agent queries."""
    query: str

def format_response(blog_content):
    """Format the blog content for API response."""
    return {
        "status": "success",
        "blog_content": blog_content
    }

def format_error(message):
    """Format error messages for API response."""
    return {
        "status": "error",
        "message": message
    }

@app.post("/agent/run")
async def run_agent_endpoint(request: QueryRequest):
    """Run the agent with the provided query."""
    try:
        logger.info(f"Received query: {request.query}")
        
        if not request.query or len(request.query.strip()) == 0:
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Run the agent
        blog_content = run_agent(request.query)
        
        # Return the response
        response = format_response(blog_content)
        logger.info("Agent execution completed successfully")
        return response
        
    except Exception as e:
        logger.error(f"Error running agent: {str(e)}")
        logger.error(traceback.format_exc())
        return format_error(f"Error running agent: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware to log all requests."""
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
