import subprocess
import sys
import os
import time

if __name__ == "__main__":
    # Start FastAPI server in the background
    print("Starting FastAPI server at http://localhost:8000")
    fastapi_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "service.fastapi:app", "--host", "0.0.0.0", "--port", "8000"],
        # Use parent directory for service imports
        cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    
    # Give FastAPI a moment to start
    time.sleep(2)
    
    # Start Streamlit app
    print("Starting Streamlit app at http://localhost:8501")
    streamlit_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                 "direct_call_app.py")
    try:
        # This will block until the Streamlit app is closed
        subprocess.run([sys.executable, "-m", "streamlit", "run", streamlit_path, "--server.port=8501"])
    finally:
        # When Streamlit is closed, also terminate the FastAPI server
        print("Shutting down FastAPI server...")
        fastapi_process.terminate()
        fastapi_process.wait()
