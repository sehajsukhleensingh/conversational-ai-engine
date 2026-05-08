import os 
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.tools import tool
import httpx
from dotenv import load_dotenv
load_dotenv()

apikey = os.getenv("EXCHANGE_RATE_API")
if not apikey:
    raise ValueError("key not found")


search_tool = DuckDuckGoSearchRun(region="us-en") #prebuilt in langchain

@tool
async def exchange_rate(currency: str):
    """
    Fetch the latest exchange rates for a given currency.
    
    This function retrieves exchange rate data from the exchangerate-api.com API
    for the specified currency against multiple other currencies.
    
    Args:
        currency (str): The ISO 4217 currency code (e.g., 'USD', 'EUR', 'GBP')
                    for which to fetch exchange rates.
    
    Returns:
        dict: A dictionary containing exchange rate data from the API, including
            base currency, timestamp, and conversion rates for all supported
            currencies. The exact structure depends on the API response.
    
    Raises:
        requests.exceptions.RequestException: If the HTTP request fails.
        ValueError: If the API returns an error response.
    
    Example:
        >>> rates = exchange_rate('USD')
        >>> print(rates)  # Returns exchange rates for USD
    """
    
    currency = currency.upper()
    url = f'https://v6.exchangerate-api.com/v6/{apikey}/latest/{currency}'
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url=url)
        data = response.json()

        return {
        "base": data["base_code"],
        "rates": data["conversion_rates"]
    }
