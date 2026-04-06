import httpx
import logging
from typing import Any, Dict, List, Optional
from mcp.server.fastmcp import FastMCP

# Quan & Huy fixed
# We setup logging here, but configure handlers in main
logger = logging.getLogger(__name__)

# Base URL for CoinGecko Public API
COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"

def setup_tools(mcp: FastMCP):
    """
    Register CoinGecko tools to the FastMCP server instance.
    We pass the mcp server instance so we can use its decorator.
    """

    @mcp.tool()
    async def get_coin_price(coin_ids: str, vs_currencies: str = "usd") -> str:
        """
        Get the current price of one or more cryptocurrencies.
        
        Args:
            coin_ids: A comma-separated string of cryptocurrency IDs (e.g., "bitcoin,ethereum", "dogecoin").
            vs_currencies: A comma-separated string of fiat currencies to compare against (default: "usd").
        """
        logger.debug(f"Fetching price for {coin_ids} in {vs_currencies}")
        url = f"{COINGECKO_BASE_URL}/simple/price"
        params = {
            "ids": coin_ids.lower(),
            "vs_currencies": vs_currencies.lower()
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params, timeout=10.0)
                response.raise_for_status()
                data = response.json()
                
                if not data:
                    return f"Error: No data found for coin_ids '{coin_ids}'. Check if the IDs are correct."
                
                # Format output nicely
                lines = []
                for coin, prices in data.items():
                    price_strs = ", ".join([f"{k.upper()}: {v}" for k, v in prices.items()])
                    lines.append(f"{coin.capitalize()}: {price_strs}")
                
                return "\n".join(lines)
            except httpx.HTTPStatusError as e:
                # Handle specific HTTP error cases (Rate limits, etc.)
                if e.response.status_code == 429:
                    return "Error: CoinGecko API rate limit exceeded. Please try again later."
                return f"Error: HTTP {e.response.status_code} - {e.response.text}"
            except Exception as e:
                return f"Error: Failed to fetch coin price - {str(e)}"
        
        return "Unknown error occurred"

    @mcp.tool()
    async def get_trending_coins() -> str:
        """
        Get the top-7 trending cryptocurrencies on CoinGecko as searched by users in the last 24 hours.
        """
        logger.debug("Fetching trending coins")
        url = f"{COINGECKO_BASE_URL}/search/trending"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, timeout=10.0)
                response.raise_for_status()
                data = response.json()
                
                coins = data.get("coins", [])
                if not coins:
                    return "No trending coins found."
                    
                lines = ["Trending Coins in the last 24 hours:"]
                for item in coins:
                    coin = item["item"]
                    lines.append(f"{coin['score'] + 1}. {coin['name']} ({coin['symbol']}) - Market Cap Rank: {coin.get('market_cap_rank', 'N/A')}")
                    
                return "\n".join(lines)
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    return "Error: CoinGecko API rate limit exceeded. Please try again later."
                return f"Error: HTTP {e.response.status_code} - {e.response.text}"
            except Exception as e:
                return f"Error: Failed to fetch trending coins - {str(e)}"

        return "Unknown error occurred"
