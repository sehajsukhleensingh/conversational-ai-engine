from langgraph.graph import StateGraph , START , END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.prebuilt import ToolNode , tools_condition

from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool 
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage , HumanMessage , SystemMessage 

from dotenv import load_dotenv
from typing import TypedDict , Annotated 
import aiosqlite
import os 
import requests

load_dotenv()

llm = ChatOpenAI(
                model="gpt-4o-mini",  # or gemini, claude etc
                temperature=0.2,
                max_tokens=512,
                base_url="https://api.aicredits.in/v1",
            )

class BotState(TypedDict):
    # this will store all the chat logs , the convos of human and llm 
    messages : Annotated[list[BaseMessage],add_messages]

# tools 
search_tool = DuckDuckGoSearchRun(region="us-en") #prebuilt in langchain
 
apikey = os.getenv("EXCHANGE_RATE_API")
if not apikey:
    raise ValueError("key not found")

@tool
def exchange_rate(currency: str):
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
    req = requests.get(url=url)
    data = req.json()

    return {
    "base": data["base_code"],
    "rates": data["conversion_rates"]
}

tools = [exchange_rate , search_tool] #added tools to a list 

llm_w_tools = llm.bind_tools(tools=tools)

toolnode = ToolNode(tools=tools)


def chatfunc(state : BotState):
    
    # user query 
    usr_query = state["messages"]
    #feed to llm
    system_message = SystemMessage(content="""
    You are an assistant.
    - NEVER show raw tool output to the user
    - ALWAYS summarize tool results
    - ONLY return final, clean answers
    """) 
    llm_res = llm_w_tools.invoke([system_message] + usr_query)

    return {"messages":[llm_res]}


conn = aiosqlite.connect(database="backend/data/convos.db") 
checkpointer = AsyncSqliteSaver(conn=conn)
graph = StateGraph(BotState)

graph.add_node("chat_node",chatfunc)
graph.add_node("tools",toolnode)

graph.add_edge(START,"chat_node")
graph.add_conditional_edges("chat_node",tools_condition)
graph.add_edge("tools","chat_node")

bot = graph.compile(checkpointer=checkpointer)
