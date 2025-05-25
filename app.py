import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

try:
    openai_api_key = os.getenv("OPENAI_API_KEY")
except:
    openai_api_key = None


# Title and header
st.title("NITK ECE Advisor Bot")

## Sidebar
with st.sidebar:
    st.markdown("""
                Ask me about NITK ECE department. I can answer questions related to
                
                * Curriculum 
                * Events   
                * News
                
                """)
    st_openai_api_key = st.text_input("OpenAI API Key", type="password", help="Enter your OpenAI API key")

    if st.button("Clear chat"):
        st.session_state.messages = []
        st.success("Chat History cleared")

system_prompt = """
You are a helpful assistant who is an expert on everything related to NITK Electronics and Communication (ECE) department. You answer questions related to NITKs ECE program, curriculum, events and latest news

Guidelines:
1. You are **not** allowed to answer questions that are not directly related to NITK. This is very important. If the user query is **not relaated to NITK**, respond by saying its out of scope and that you're here to help with NITK-related questions
2. **If a user query is vague or underspecified**, do not assume. Instead, ask follow-up questions.


Be concise when appropriate, but offer long, elaborate answers when more detail would be helpful.
"""

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = [{"role":"system", "content":system_prompt}]

if openai_api_key or st_openai_api_key:
    st.session_state.api_key = openai_api_key or st_openai_api_key
    st.session_state.client = OpenAI(api_key=st.session_state.api_key)

else:
    st.warning("Please enter your OpenAI API key here or add it to the .env file to continue.")


# Display chat history (excluding system message)
for msg in st.session_state.messages:
    if msg["role"] == "system":
        continue  # Don't show system message
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Handle user input
if st.session_state.client:
    if user_input := st.chat_input("Enter your message here"):
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.chat_message("user"):
            st.markdown(user_input)


        with st.chat_message("assistant"):
            status_container = st.empty()
            response_container = st.empty()
            status_container.info("Initializing....")    

            response = st.session_state.client.chat.completions.create(
                temperature=0.1,
                messages=st.session_state.messages,
                model="gpt-3.5-turbo"
            )

            if response:
                status_container.empty()
                with response_container.container():
                    st.markdown(response.choices[0].message.content)
                
                st.session_state.messages.append({
                    "role":"assistant",
                    "content": response.choices[0].message.content
                })
                print(st.session_state.messages)
            
            

            
        