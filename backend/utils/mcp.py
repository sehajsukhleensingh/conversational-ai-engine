from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient(
    {
        "github":{
            "transport" : "streamable_http" , 
            "url" : "https://api.githubcopilot.com/mcp/"
        }
    }
)