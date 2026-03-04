import streamlit as st 
import requests

usr_input = st.chat_input("type here ...")


if "mssg_hist" not in st.session_state:
    st.session_state["mssg_hist"] = []

# load all the old convo hist 
for mssg in st.session_state["mssg_hist"]:
    with st.chat_message(mssg["role"]):
        st.text(mssg["content"])


if usr_input:
    st.session_state["mssg_hist"].append({
        "role":"user",
        "content":usr_input})  
      
    with st.chat_message("user"):
        st.text(usr_input)
        
        response = requests.post(
            url= "http://127.0.0.1:8000/chat" , 
            json= {"usr_message":usr_input} , 
            stream= True
        )

        """
        WHAT (stream = True) does 
        send request
        ↓
        open connection
        ↓
        do NOT download response body yet
        ↓
        wait for chunks

        WHAT (for line in response.iter_lines():) does 
        server sends token
        ↓
        client receives token
        ↓
        loop executes
        ↓
        UI updates
        """

        full_response = ""
        with st.chat_message("llm"):

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
        "role":"llm",
        "content":full_response})    
    