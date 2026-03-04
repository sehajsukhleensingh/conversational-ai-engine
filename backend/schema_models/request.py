from pydantic import BaseModel , Field 
from typing import Annotated

class UsrRequest(BaseModel):

    usr_message : Annotated[
        str,
        Field(max_length=300 , 
            description="the query of the user which will be feeded to llm ")
        ]

    CONFIG : Annotated[
        dict,
        Field(...,description="the config parameter for our llm node ")
        ] 