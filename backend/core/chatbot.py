from langgraph.graph import StateGraph , START , END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.prebuilt import ToolNode , tools_condition


from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage , HumanMessage , SystemMessage 

from backend.utils.tools import search_tool , exchange_rate , rag_tool
from backend.utils.mcp import client

from dotenv import load_dotenv
from typing import TypedDict , Annotated 
import aiosqlite
import os 
import asyncio

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
    thread_id: str  # passed for reference but thread_id comes from config



async def build_graph():

    conn = await aiosqlite.connect(database="backend/data/convos.db") 
    checkpointer = AsyncSqliteSaver(conn=conn)

    mcp_tools = await client.get_tools()
    tools = [*mcp_tools , search_tool , exchange_rate , rag_tool]

    llm_w_tools = llm.bind_tools(tools=tools)

    async def chatfunc(state : BotState):
    
        # user query 
        usr_query = state["messages"]
        #feed to llm
        system_message = SystemMessage(content="""
        You are an assistant that helps users analyze uploaded documents.
        
        TOOLS AVAILABLE:
        - rag_tool: Retrieves relevant information from uploaded PDF documents
        
        INSTRUCTIONS:
        - When user asks about uploaded files/documents, ALWAYS use rag_tool first
        - If user mentions 'file', 'document', 'resume', 'pdf', or similar, use rag_tool to retrieve content
        - NEVER show raw tool output - ALWAYS summarize it naturally
        - ONLY return final, clean answers summarizing the retrieved information
        - If rag_tool returns no results, explain that the document doesn't contain relevant information
        """) 
        llm_res = await llm_w_tools.ainvoke([system_message]+usr_query)

        return {"messages":[llm_res]}

    toolnode = ToolNode(tools=tools)

    graph = StateGraph(BotState)

    graph.add_node("chat_node",chatfunc)
    graph.add_node("tools",toolnode)

    graph.add_edge(START,"chat_node")
    graph.add_conditional_edges("chat_node",tools_condition)
    graph.add_edge("tools","chat_node")

    bot = graph.compile(checkpointer=checkpointer)

    return bot


