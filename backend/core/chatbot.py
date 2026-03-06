from langgraph.graph import StateGraph , START , END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage , HumanMessage 

from dotenv import load_dotenv
from typing import TypedDict , Annotated 
import aiosqlite

load_dotenv()

llm = ChatGoogleGenerativeAI(model = "gemini-2.5-flash-lite" , 
                             temperature = 0.2)

class BotState(TypedDict):
    # this will store all the chat logs , the convos of human and llm 
    messages : Annotated[list[BaseMessage],add_messages]

def chatfunc(state : BotState):
    
    # user query 
    usr_query = state["messages"]
    #feed to llm 
    llm_res = llm.invoke(usr_query)

    return {"messages":[llm_res]}

conn = aiosqlite.connect(database="backend/data/convos.db")
checkpointer = AsyncSqliteSaver(conn=conn)
graph = StateGraph(BotState)

graph.add_node("chat_llm",chatfunc)
graph.add_edge(START,"chat_llm")
graph.add_edge("chat_llm",END)

bot = graph.compile(checkpointer=checkpointer)
