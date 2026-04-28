import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import streamlit as st 
import requests
from backend.app.config import Config
from backend.utils.helper import Utitlity

# xxxxxxxxxxxxxxxxxxxxxxxx-Utils-xxxxxxxxxxxxxxxxxxxxxxxxx

def add_thread(thread_id):

    if thread_id not in st.session_state["chat_threads"]:
        st.session_state["chat_threads"].append(thread_id)

def chat_reset():

    CONFIG = Config.config_id()
    st.session_state["mssg_hist"] = []
    st.session_state["thread_id"] = CONFIG["configurable"]["thread_id"]
    add_thread(CONFIG["configurable"]["thread_id"])
    
# xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx


# xxxxxxxxxxxxxxxxxxxxxxxx-SESSION-SETUP-xxxxxxxxxxxxxxxxx

CONFIG = Config.config_id()

if "mssg_hist" not in st.session_state:
    st.session_state["mssg_hist"] = []

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = CONFIG["configurable"]["thread_id"]

if "chat_threads" not in st.session_state:
    threads = Utitlity.extract_threads()
    st.session_state["chat_threads"] = threads

add_thread(st.session_state["thread_id"])

# xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx


#xxxxxxxxxxxxxxxxxxxxxx-SIDEBAR-xxxxxxxxxxxxxxxxxxxxxxxxxxx

st.sidebar.markdown("# **misl**")
st.sidebar.write("")
if st.sidebar.button("new chat"):
    chat_reset()

st.sidebar.subheader("Old Conversations")
for thread_id in st.session_state["chat_threads"]:
    if st.sidebar.button(thread_id,key=thread_id):

        st.session_state["thread_id"] = thread_id
        response = requests.get(
            url="http://127.0.0.1:8000/chat-history" , 
            params={"thread":thread_id}
        )
        old_messages = response.json()
        st.session_state["mssg_hist"] = old_messages

#xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx


# xxxxxxxxxxxxxxxxxxxxxxxx-OLD-CONVOS-xxxxxxxxxxxxxxxxxxxx

# load all the old convo hist 
for mssg in st.session_state["mssg_hist"]:
    with st.chat_message(mssg["role"]):
        st.markdown(mssg["content"])

#xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx


usr_input = st.chat_input("type here ...")

#xxxxxxxxxxxxxxxxxxxxxxxx-CHAT-xxxxxxxxxxxxxxxxxxxxxxxxxxxx

if usr_input:
    st.session_state["mssg_hist"].append({
        "role":"user",
        "content":usr_input})  
      
    with st.chat_message("user"):
        st.text(usr_input)
        
    response = requests.post(
        url= "http://127.0.0.1:8000/chat" , 
        json= {"usr_message":usr_input , 
               "CONFIG":{
                   "configurable":{
                       "thread_id":st.session_state["thread_id"]}
               }} , 
        stream= True
    )

    # WHAT (stream = True) does 
    # send request
    # ↓
    # open connection
    # ↓
    # do NOT download response body yet
    # ↓
    # wait for chunks

    # WHAT (for line in response.iter_lines():) does 
    # server sends token
    # ↓
    # client receives token
    # ↓
    # loop executes
    # ↓
    # UI updates
    
    full_response = ""
    with st.chat_message("assistant"):

        placeholder = st.empty()
        for line in response.iter_lines():
            if line:
                decoded  = line.decode("utf-8")
                if decoded.startswith("data: "):
                    token = decoded.replace("data: ","")
                    if token == "END":
                        break

                    full_response += token
                    placeholder.markdown(full_response) # used markdown cause it updates 
                    # the data creating a streaming effect , unlike the text box which 
                    # will create a new box for every token 

    st.session_state["mssg_hist"].append({
        "role":"assistant",
        "content":full_response})
        
#xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx  