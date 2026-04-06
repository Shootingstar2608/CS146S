import os
import sys
import argparse
import logging
import uvicorn
from dotenv import load_dotenv

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from mcp.server.fastmcp import FastMCP

# Ensure tools can be imported whether run as script or module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from tools import setup_tools

load_dotenv()
#fixed lan cuoi
# Setup logging
logging.basicConfig(
    stream=sys.stderr, # MUST be stderr for STDIO transport to work correctly
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("coingecko_server")

class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware to validate Bearer token for remote HTTP transports.
    Does not affect STDIO transport since STDIO doesn't use the Starlette app.
    """
    async def dispatch(self, request, call_next):
        auth_token = os.getenv("AUTH_TOKEN")
        if auth_token:
            header = request.headers.get("Authorization")
            if not header:
                return JSONResponse(
                    {"error": "Unauthorized. Please provide an Authorization header"}, 
                    status_code=401
                )
            token = header.split(" ")[1] if header.startswith("Bearer ") else header
            if token != auth_token:
                return JSONResponse(
                    {"error": "Forbidden. Invalid token credentials."}, 
                    status_code=403
                )
        return await call_next(request)

# Create FastMCP server and app globally so Serverless (Vercel/Cloudflare) can import it
mcp = FastMCP("CoinGecko Server")
setup_tools(mcp)

app = mcp.sse_app()
if os.getenv("AUTH_TOKEN"):
    logger.info("Authentication is enabled. Expecting Authorization token.")
    app.add_middleware(AuthMiddleware)
else:
    logger.warning("AUTH_TOKEN is not set. Running in insecure mode without authentication.")

def main():
    parser = argparse.ArgumentParser(description="CoinGecko MCP Server")
    parser.add_argument("--transport", default="stdio", choices=["stdio", "sse"], help="Transport mode (stdio or sse)")
    parser.add_argument("--port", type=int, default=8000, help="Port for SSE server")
    args = parser.parse_args()

    if args.transport == "stdio":
        logger.info("Starting CoinGecko MCP in STDIO mode")
        mcp.run(transport="stdio")
    elif args.transport == "sse":
        logger.info(f"Starting CoinGecko MCP in SSE (HTTP) mode on port {args.port}")
        uvicorn.run(app, host="0.0.0.0", port=args.port)

if __name__ == "__main__":
    main()
