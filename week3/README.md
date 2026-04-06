# CoinGecko MCP Server

A custom Model Context Protocol (MCP) server that provides real-time cryptocurrency data using the public CoinGecko API. This server supports both standard **STDIO** transport for local use and **SSE (HTTP)** transport for remote network deployments, along with optional token-based authentication.

## Features & Tools

This server exposes the following MCP Tools:

1. **`get_coin_price`**
   - **Description**: Fetches the current price of one or more cryptocurrency IDs in specified fiat currencies.
   - **Parameters**: 
     - `coin_ids` (string, required): Comma-separated list of CoinGecko coin IDs (e.g. `bitcoin,ethereum`).
     - `vs_currencies` (string, optional, defaults to `usd`): Comma-separated fiat currencies (e.g. `usd,eur`).
   - **Expected Behavior**: Returns formatted text block with prices of requested tokens. Gracefully handles errors if IDs are incorrect or API rate-limited.

2. **`get_trending_coins`**
   - **Description**: Fetches the top-7 trending cryptos searched by users in the last 24 hours.
   - **Parameters**: None
   - **Expected Behavior**: Returns a formatted list of trending coins with their names, symbols, and market cap rank.

## Prerequisites

- Python >= 3.10
- Node.js (Only required if you want to test via the `mcp-inspector`)
- CoinGecko API Key (Optional, free public API limits apply)

## Setup & Environment

1. **Clone and Install dependencies**:
   Ensure you're inside this `week3` directory, then create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r server/requirements.txt
   ```

2. **Configure Environment Variables**:
   Copy the example config and adjust if needed:
   ```bash
   cp server/.env.example server/.env
   ```
   Add a secret key to `AUTH_TOKEN` in `.env` if you plan to deploy remotely.

## Running the Server

### Option A: Local Transport (STDIO)
This runs locally and communicates over stdin/stdout. Logging is strictly routed to `stderr` to avoid breaking the MCP protocol.
```bash
python server/main.py --transport stdio
```

### Option B: Remote Transport (SSE / HTTP)
This starts an HTTP server (Uvicorn / FastAPI wrapper) listening on port 8000 by default. It utilizes Server-Sent Events (SSE).
```bash
python server/main.py --transport sse --port 8000
```
> **Security Note:** If `AUTH_TOKEN` is found in `.env`, the SSE server will mandate an `Authorization: Bearer <token>` header for requests.

## Client Integration Examples

### Testing with Claude Desktop (Local STDIO)
To use this with the local Claude Desktop app, edit your Claude config file (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS or `%APPDATA%\Claude\claude_desktop_config.json` on Windows):

```json
{
  "mcpServers": {
    "coingecko": {
      "command": "/absolute/path/to/week3/.venv/bin/python",
      "args": [
        "/absolute/path/to/week3/server/main.py",
        "--transport",
        "stdio"
      ],
      "env": {}
    }
  }
}
```

### Testing with MCP Inspector
You can debug your server via the official inspector CLI:

**Local STDIO:**
```bash
npx @modelcontextprotocol/inspector python server/main.py --transport stdio
```

**Remote SSE:**
When hosting the server on `http://localhost:8000`, connect the inspector over HTTP.

## Error Handling & Rate Limiting

- **Graceful Error Responses**: Missing coins, HTTP timeouts, and unexpected data schema errors are caught and returned as clean strings to the Model instead of crashing the server.
- **Rate Limit Caution**: The free CoinGecko API is strictly rate-limited. If you exceed the quota, the server returns an explicit message urging the agent/user to *try again later*.
