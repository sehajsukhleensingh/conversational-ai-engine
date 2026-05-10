from fastapi import APIRouter , HTTPException , Request
from fastapi.responses import StreamingResponse
from fastapi import UploadFile , File , Form

from backend.schema_models.request import UsrRequest
from backend.utils.tools import _USER_FILES_PATH

from langchain_core.messages import HumanMessage , BaseMessage , AIMessage

import os 

router = APIRouter()

@router.get("/health")
def health_check(request : Request):
    
    bot = request.app.state.bot

    try:      
        if bot is None:
            raise Exception(status_code=500,detail="chatbot error")
        
        return {"status":"healthy" , 
                "bot":"ready"}

    except Exception as e:
        raise HTTPException(status_code=503 , detail=str(e))


@router.post("/chat")
async def chat(usr : UsrRequest , request : Request ):

    bot = request.app.state.bot

    # fetch the query 
    query = usr.usr_message
    CONFIG = usr.CONFIG

    try:
        # feed to chatbot
        async def generator():
            async for msg_chnk , meta in  bot.astream(
                {
                    "messages": [HumanMessage(content=query)],
                    "thread_id": CONFIG["configurable"]["thread_id"]
                },
                stream_mode="messages",
                config=CONFIG):

                if await request.is_disconnected():
                    break 

                if isinstance(msg_chnk, AIMessage) and msg_chnk.content:
                    yield f"data: {msg_chnk.content} \n\n"
            
            yield "event: done\ndata: END\n\n"
 
        return StreamingResponse(generator(),media_type="text/event-stream")

    except Exception as e: 
        raise HTTPException(status_code=500 , detail= str(e))



@router.get("/chat-history")
def history(thread : str , request : Request) -> list[dict[str,str]]:

    bot = request.app.state.bot
    
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
        
@router.post("/upload_file")
async def upload_file(file: UploadFile = File(...), thread_id: str = Form(...)):
    
    try:
        path = os.path.join(_USER_FILES_PATH,thread_id)
        os.makedirs(path,exist_ok=True)

        save_path = os.path.join(path,file.filename)

        with open(save_path,"wb") as f:
            content = await file.read()
            f.write(content)

        return {"message":"file uploaded successfully"} 

    except Exception as e:
        raise RuntimeError("issue while uploading the file " + str(e))

