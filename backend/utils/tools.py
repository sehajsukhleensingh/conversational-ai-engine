import os 

from langchain_community.tools import DuckDuckGoSearchRun
from langchain.tools import tool
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings
from langchain_core.runnables import RunnableConfig

from backend.schema_models.request import UsrRequest

import httpx
from dotenv import load_dotenv
load_dotenv()

_USER_FILES_PATH = "backend/data/uploads/threads"
_VECTOR_STORE_PATH = "backend/data/vector_store/threads"

exchange_apikey = os.getenv("EXCHANGE_RATE_API")
if not exchange_apikey:
    raise ValueError("key not found")

embeddings_model = OpenAIEmbeddings(
        model="text-embedding-3-small" , 
        base_url="https://api.aicredits.in/v1"
    )

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
    url = f'https://v6.exchangerate-api.com/v6/{exchange_apikey}/latest/{currency}'
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url=url)
        data = response.json()

        return {
        "base": data["base_code"],
        "rates": data["conversion_rates"]
    }


async def rag_ingestion(thread_id : str) -> FAISS:
    """
    Ingest PDF files from a thread directory and create a FAISS vector store.
    
    This function loads all PDF files in a thread-specific directory, splits them into chunks,
    generates embeddings using OpenAI's text-embedding-3-small model, and stores them in a
    FAISS vector database for semantic search and retrieval.
    
    Args:
        thread_id (str): The conversation thread ID used to locate the PDF files in
                        _USER_FILES_PATH/thread_id. Documents are organized per thread.
    
    Returns:
        FAISS: A FAISS vector store object containing embedded document chunks from all
               PDFs in the thread directory. The vector store is saved locally in
               _VECTOR_STORE_PATH/thread_id for persistence and future retrieval.
    
    Raises:
        ValueError: If the thread directory doesn't exist, PDF loading fails, chunk creation
                   errors occur, or vector store serialization to disk fails.
    
    Note:
        - Chunk size: 1200 characters with 420 character overlap
        - Uses OpenAI embeddings model: text-embedding-3-small
        - Vector store is persisted to disk automatically
    
    Example:
        >>> vectorstore = await rag_ingestion('thread-uuid-12345')
        >>> # vectorstore is now ready for similarity searches
    """
    path = os.path.join(_USER_FILES_PATH , thread_id)
    file_name = os.listdir(path=path)[0]
    full_path = os.path.join(path,file_name)
    if os.path.exists(path=full_path):
        loader = PyPDFLoader(full_path)
        doc = loader.load()
    else: 
        raise ValueError("The file path doesnt exists")
    
    try:
        splitter = RecursiveCharacterTextSplitter(chunk_size = 1200 , chunk_overlap = 420)
        chunks = splitter.split_documents(doc)

    except Exception as e:
        raise ValueError("Got issue in creating chunks "+str(e))


    vectorstore = FAISS.from_documents(documents=chunks , embedding=embeddings_model)

    try:
        vec_store_path = os.path.join(_VECTOR_STORE_PATH,thread_id)
        vectorstore.save_local(vec_store_path)
    except Exception as e:
        raise ValueError("got some issue in saving vector store "+str(e))        

    return vectorstore

@tool
async def rag_tool(config: RunnableConfig, query: str):
    """
    Retrieve relevant documents from a thread-specific vector store using semantic search.
    
    This tool retrieves the most similar documents to a user query from a FAISS vector store.
    It automatically loads the vector store for the current thread or creates one by ingesting
    PDFs if it doesn't exist yet. Thread ID is extracted from LangGraph's RunnableConfig.
    
    Args:
        config (RunnableConfig): LangGraph runtime config containing thread_id in
                               config['configurable']['thread_id']. This identifies which
                               conversation thread to retrieve documents for.
        query (str): The natural language search query to find relevant documents.
                    Will retrieve documents most similar to this query based on embeddings.
    
    Returns:
        dict: A dictionary containing:
            - 'query' (str): The original query string
            - 'retrieved_documents' (list): List of up to 4 most similar document chunks
                                           (sorted by semantic similarity)
            - 'metadata' (list): Metadata for each document (e.g., page numbers, source)
    
    Raises:
        RuntimeError: If document retrieval or similarity search fails.
        ValueError: If the vector store cannot be created or loaded.
    
    Note:
        - Retrieves top 4 most similar documents using cosine similarity
        - Thread-specific vector stores are stored in _VECTOR_STORE_PATH/thread_id
        - Automatically ingests PDFs if vector store doesn't exist for the thread
        - Thread ID is injected by the LangGraph framework, not by the LLM
    
    Example:
        >>> result = await rag_tool('What are the key findings?', config)
        >>> print(result['retrieved_documents'])  # Returns relevant document sections
    """

    thread_id = config["configurable"]["thread_id"]
    path = os.path.join(_VECTOR_STORE_PATH , thread_id)
    if os.path.exists(path):
        vectorstore = FAISS.load_local(
                        path ,
                        embeddings_model ,
                        allow_dangerous_deserialization=True)
    else:
        vectorstore = await rag_ingestion(thread_id=thread_id)
    
    try:
        retriever = vectorstore.as_retriever(search_type = "similarity" , search_kwargs = {"k":4})
        retrieved_data = retriever.invoke(query)

    except Exception as e:
        raise RuntimeError("some issue occured in retriever"+str(e))
    

    content = [doc.page_content for doc in retrieved_data]
    metadata = [doc.metadata for doc in retrieved_data]

    return {
        "query":query , 
        "retrieved_documents":content ,
        "metadata":metadata
    }
