import os
import json
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from tools.curriculum_tool import get_courses

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
3. For any questions related to ECE courses or curriculum, use the curriculum_tool in your planning

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


tools = [
    {
        "type":"function",
        "function": {
            "name":"get_courses",
            "description": "Get courses relevant to the user query",
            "parameters":{
                "type": "object",
                "properties": {
                    "user_prompt":{
                        "type": "string",
                        "description": "User query"
                    }
                },
                "required":["user_prompt"]
            }

        }
    }
]

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
                model="gpt-3.5-turbo",
                tools=tools
            )

            response = response.choices[0].message

            if response.content:
                status_container.empty()
                with response_container.container():
                    st.markdown(response.content)
                
                st.session_state.messages.append({
                    "role":"assistant",
                    "content": response.content
                })
                print(st.session_state.messages)
            
            if response.tool_calls:
                tool_call = response.tool_calls[0]
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                print(function_name, function_args)
                if function_name == 'get_courses':
                    function_response = get_courses(**function_args)
                    print(function_response)

                st.session_state.messages.append({
                    "role":"assistant",
                    "content": None,
                    "tool_calls": [{
                        "id": tool_call.id,
                        "type": "function",
                        "function": {
                            "name": function_name,
                            "arguments": tool_call.function.arguments
                        }
                     }]
                })

                st.session_state.messages.append({
                    "role":"tool",
                    "tool_call_id": tool_call.id,
                    "content":str(function_response)
                }                
                )
                print(st.session_state.messages)
                response = st.session_state.client.chat.completions.create(
                temperature=0.1,
                messages=st.session_state.messages,
                model="gpt-3.5-turbo",
                )

                response = response.choices[0].message
                status_container.empty()
                with response_container.container():
                    st.markdown(response.content)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": response.content
                    }
                )
            
            

            
        