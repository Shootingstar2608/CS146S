import os
import sys

# Add project root so we can import internal modules inside Serverless logic
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the pre-configured Starlette app from our codebase
from server.main import app

# This app instance is grabbed by Vercel for mapping to HTTPS endpoints
