from fastapi import APIRouter , HTTPException , Request
from fastapi.responses import StreamingResponse

from backend.schema_models.request import UsrRequest

from langchain_core.messages import HumanMessage , BaseMessage , AIMessage

from backend.core.chatbot import bot

router = APIRouter()

@router.get("/health")
def health_check():
    try:      
        if bot is None:
            raise Exception(status_code=500,detail="chatbot error")
        
        return {"status":"healthy" , 
                "bot":"ready"}

    except Exception as e:
        raise HTTPException(status_code=503 , detail=str(e))


@router.post("/chat")
async def chat(usr : UsrRequest , request : Request ):

    # fetch the query 
    query = usr.usr_message
    CONFIG = usr.CONFIG

    try:
        # feed to chatbot
        async def generator():
            async for msg_chnk , meta in  bot.astream(
                {"messages":[HumanMessage(content = query)]},
                stream_mode="messages",
                config=CONFIG):

                if await request.is_disconnected():
                    break 

                if hasattr(msg_chnk,"content") and msg_chnk.content:
                    yield f"data: {msg_chnk.content} \n\n"
            
            yield "event: done\ndata: END\n\n"
 
        return StreamingResponse(generator(),media_type="text/event-stream")

    except Exception as e: 
        raise HTTPException(status_code=500 , detail= str(e))



@router.get("/chat-history")
def history(thread : str) -> list[dict[str,str]]:

    try:
        state = bot.get_state(config = {"configurable":
                                    {"thread_id":thread}})
        data = state.values.get("messages",[])
        
    except Exception as e:
        raise HTTPException(status_code=500 , detail= str(e))
    
    records = []

    for item in data: 
        temp = {}
        if isinstance(item,HumanMessage):
            temp["role"] = "user"
            temp["content"] = item.content

        elif isinstance(item,AIMessage):
            temp["role"] = "assistant"
            temp["content"] = item.content

        records.append(temp)
    
    return records
        