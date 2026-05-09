from langchain_mcp_adapters.client import MultiServerMCPClient
import os 

from dotenv import load_dotenv
load_dotenv()

git_api_key = os.getenv("GITHUB_TOKEN") 
if not git_api_key:
    raise ValueError("github api key not found")

client = MultiServerMCPClient(
    {
        "github":{
            "transport" : "streamable_http" , 
            "url" : "https://api.githubcopilot.com/mcp/" , 
            "headers" :{
                "Authorization":f"Bearer {os.getenv('GITHUB_TOKEN')}"
            }
        }
    }
)