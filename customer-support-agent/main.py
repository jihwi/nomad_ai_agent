import streamlit as st
from agents import Agent, Runner, SQLiteSession, function_tool, RunContextWrapper, InputGuardrailTripwireTriggered, OutputGuardrailTripwireTriggered
from dotenv import load_dotenv
import asyncio
from openai import OpenAI
from model import UserAccountContext
from my_agents.triage_agents import triage_agent

load_dotenv()

client = OpenAI()

@function_tool 
def get_user_tier(wrapper: RunContextWrapper[UserAccountContext]):
    return (
        f"the user {wrapper.customer_id} has a {wrapper.tier} account."
    )

user_account_ctx = UserAccountContext(
    customer_id = 1,
    name= "nico",
    tier = "basic"
)

if "session" not in st.session_state: 
    st.session_state["session"] = SQLiteSession("chat-history", "chat-gpt-clone-memory.db")

session = st.session_state["session"]

if "agent" not in st.session_state: 
    st.session_state["agent"] = triage_agent


async def paint_history():
    messages = await session.get_items()
    for message in messages: 
        if "role" in message:
            with st.chat_message(message["role"]):
                if message["role"] == "user":
                    content = message["content"]
                    if isinstance(content, str):
                        st.write(content)
                else:
                    if message["type"] == "message":
                        st.write(message["content"][0]["text"].replace("$", "\$"))

asyncio.run(paint_history())


async def run_agent(message):
   with st.chat_message("ai"):
            text_placeholder = st.empty()
            response = ""

            st.session_state["text_placeholder"] = text_placeholder
            
            try: 
                stream = Runner.run_streamed(st.session_state["agent"], message, session=session, context=user_account_ctx)  #여기에 context를 넘겨주면 그 내부 모든 tool에 의존성주입된다. 
            
                async for event in stream.stream_events():
                    if event.type == "raw_response_event":
                        if event.data.type == "response.output_text.delta":
                            response += event.data.delta 
                            text_placeholder.write(response.replace("$", "\$"))
                    elif event.type == "agent_updated_stream_event": 
                        if (st.session_state["agent"] != event.new_agent): 
                            st.write(f"🤖 transfer from {st.session_state["agent"].name} to {event.new_agent.name}")
                            st.session_state["agent"] = event.new_agent; 
                            text_placeholder = st.empty()
                            st.session_state["text_placeholder"] = text_placeholder
                            response = ""

            except InputGuardrailTripwireTriggered : 
                st.write("I can't help you with that.")
            except OutputGuardrailTripwireTriggered: 
                st.write("Cant show you that answer.")
                st.session_state["text_placeholder"].empty()



prompt = st.chat_input("Write a message for your assistant.")
if prompt: 
    if prompt: 
        with st.chat_message("human"):
            st.write(prompt)
        asyncio.run(run_agent(prompt))


with st.sidebar: 
    reset = st.button("Reset memory")
    if reset: 
        asyncio.run(session.clear_session())

    st.write(asyncio.run(session.get_items()))