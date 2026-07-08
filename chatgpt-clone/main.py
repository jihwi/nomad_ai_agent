import streamlit as st
from agents import Agent, Runner, SQLiteSession, WebSearchTool, FileSearchTool, ImageGenerationTool, CodeInterpreterTool,HostedMCPTool
from dotenv import load_dotenv
import asyncio
from openai import OpenAI
import base64
from agents.mcp.server import MCPServerStdio

load_dotenv()

client = OpenAI()
VECTOR_STORE_ID = "vs_6a38f8c3691881918fe18f6ff64f50d9"


if "session" not in st.session_state: 
    st.session_state["session"] = SQLiteSession("chat-history", "chat-gpt-clone-memory.db")

session = st.session_state["session"]

async def paint_history():
    messages = await session.get_items()
    for message in messages: 
        if "role" in message:
            with st.chat_message(message["role"]):
                if message["role"] == "user":
                    content = message["content"]
                    if isinstance(content, str):
                        st.write(content)
                    elif isinstance(content, list):
                        for part in content:
                            if "image_url" in part:
                                st.image(part["image_url"])
                else:
                    if message["type"] == "message":
                        st.write(message["content"][0]["text"].replace("$", "\$"))
        
        if "type" in message:
            message_type = message["type"]
            if message_type == "web_search_call":
                with st.chat_message("ai"):    
                    st.write("🔎 Searched the web...")
            elif message_type == "file_search_call":
                with st.chat_message("ai"):    
                    st.write("🗂️ Searched the files...")
            elif message_type == "image_generation_call":
                with st.chat_message("ai"):    
                    image = base64.b64decode(message["result"])
                    st.image(image)
            elif message_type == "code_interpreter_call":
                with st.chat_message("ai"):    
                    st.code(message["code"])
            elif message_type == "mcp_list_tools":
                with st.chat_message("ai"):
                    st.write(f"Listed {message["server_label"]}'s tools")
            elif message_type == "mcp_call":
                with st.chat_message("ai"):
                    st.write(f"Called {message["server_label"]}'s {message["name"]} with args {message["arguments"]}")

asyncio.run(paint_history())


def update_status(status_container, event):
    status_messages = {
        "response.web_search_call.completed": ("✅ Web search completed.", "complete"),
        "response.web_search_call.in_progress": (
            "🔍 Starting web search...",
            "running",
        ),
        "response.web_search_call.searching": (
            "🔍 Web search in progress...",
            "running",
        ),
        "response.file_search_call.completed": ("✅ File search completed.", "complete"),
        "response.file_search_call.in_progress": (
            "🗂️ Starting file search...",
            "running",
        ),
        "response.file_search_call.searching": (
            "🗂️ File search in progress...",
            "running",
        ),
        "response.image_generation_call.generating": (
            "🎨 Drawing image...",
            "running",
        ),
        "response.image_generation_call.in_progress": (
            "🎨 Drawing image...",
            "running",
        ),
        "response.code_interpreter_call_code.done": ("🤖 Run code.", "complete"),
        "response.code_interpreter_call.completed": ("🤖 Run code.", "complete"),
        "response.code_interpreter_call.in_progress": (
            "🤖 Running code...",
            "running",
        ),
        "response.code_interpreter_call.interpreting": (
            "🤖 Running code...",
            "running",
        ),
        "response.mcp_call.completed": (
            "⚒️ Called MCP tool",
            "complete",
        ),
        "response.mcp_call.failed": (
            "⚒️ Error calling MCP tool",
            "complete",
        ),
        "response.mcp_call.in_progress": (
            "⚒️ Calling MCP tool...",
            "running",
        ),
        "response.mcp_list_tools.completed": (
            "⚒️ Listed MCP tools",
            "complete",
        ),
        "response.mcp_list_tools.failed": (
            "⚒️ Error listing MCP tools",
            "complete",
        ),
        "response.mcp_list_tools.in_progress": (
            "⚒️ Listing MCP tools",
            "running",
        ),
        "response.completed": (" ", "complete"),
    }

    if event in status_messages: 
        label, state = status_messages[event]
        status_container.update(label = label, state = state)


async def run_agent(message):
    yfinance_server = MCPServerStdio(
        params = {
            "command": "uvx",
            "args": ["mcp-yahoo-finance"],
        },
        client_session_timeout_seconds=60,  
        cache_tools_list =True
    ) #매번 실헹마다 mcp 서버를 넘겨줘야해서 session cache agent 사용 제거 

    timezone_server = MCPServerStdio(
        params = {
            "command": "uvx",
            "args": ["mcp-server-time", "--local-timezone=Asia/Seoul"]
        },
        client_session_timeout_seconds=60,  
        cache_tools_list =True
    )

    async with yfinance_server, timezone_server:
        agent = Agent(
            mcp_servers=[yfinance_server, timezone_server],
            name="ChatGPT Clone",
            instructions= """
            You are a helpful assistant.

            You have access to the following tools:
                - Web Search Tool: Use this when the user asks a questions that isn't in your training data. Use this tool when the users asks about current or future events, when you think you don't know the answer, try searching for it in the web first.
                - File Search Tool: Use this tool when the user asks a question about facts related to themselves. Or when they ask questions about specific files.
                - Image Generation Tool: Use this tool when the user asks a question about images.
                - Code Interpreter Tool: CRITICAL: You MUST use this tool whenever the user requests any mathematical calculations, data analysis, portfolio simulations, or code execution. Do not attempt to calculate complex math or simulate financial portfolios in text; always write and run code to get the exact numbers.
            """,
            tools=[WebSearchTool(
                user_location={
                    "type": "approximate",
                    "city": "Seoul",
                    "country": "KR",
                    "timezone": "Asia/Seoul"
                }
            ),
            FileSearchTool(vector_store_ids=[VECTOR_STORE_ID], max_num_results=3),
            ImageGenerationTool(
                tool_config= {
                    "type": "image_generation",
                    "quality": "high",
                    "output_format": "jpeg",
                    "partial_images": 1 
                }
            ),
            CodeInterpreterTool(
                tool_config = {
                    "type": "code_interpreter",
                    "container": {
                        "type": "auto"
                    }
                }
            ),
            HostedMCPTool(
                tool_config = {
                    "server_url": "https://mcp.context7.com/mcp",
                    "type": "mcp",
                    "server_label": "Context7",
                    "server_description": "Use this to get the docs from software projects.",
                    "require_approval": "never"
                }
            )
            ],
        )

        with st.chat_message("ai"):
            status_container = st.status("⏳", expanded=False)

            code_placeholder = st.empty()
            image_placeholder = st.empty()
            text_placeholder = st.empty()
            code_response = ""
            response = "" 
            stream = Runner.run_streamed(agent, message, session=session)
        
            async for event in stream.stream_events():
                if event.type == "raw_response_event":
                    update_status(status_container, event.data.type)

                    if event.data.type == "response.output_text.delta":
                        response += event.data.delta 
                        text_placeholder.write(response.replace("$", "\$"))

                    elif event.data.type == "response.image_generation_call.partial_image":
                        image= base64.b64decode(event.data.partial_image_b64)
                        image_placeholder.image(image)

                    elif event.data.type == "response.code_interpreter_call_code.delta":
                        code_response += event.data.delta
                        code_placeholder.code(code_response)


prompt = st.chat_input("Write a message for your assistant.", accept_file=True, file_type=["txt", "jpg", "jpeg", "png"])
if prompt: 
    for file in prompt.files:
        if file.type.startswith("text/"):
            with st.chat_message("ai"):
                with st.status("⏳ Uploading file...") as status:
                    uploaded_file = client.files.create(
                        file=(file.name, file.getvalue()),
                        purpose="user_data"
                    )

                    status.update(label="⏳ Attaching file...")

                    client.vector_stores.files.create(
                        file_id = uploaded_file.id,
                        vector_store_id = VECTOR_STORE_ID,
                    )
                    status.update(label = "✅ File uploaded.", state = "complete")
        elif file.type.startswith("image/"):
            with st.status("⏳ Uploading image...") as status:
                image_bytes = file.getvalue()
                image_base64 = base64.b64encode(image_bytes).decode("utf-8")
                image_url = f"data:{file.type};base64,{image_base64}"

                asyncio.run(session.add_items(
                    [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "input_image",
                                    "detail": "auto",
                                    "image_url": image_url
                                }
                            ]
                        }
                    ]
                ))
                status.update(label = "✅ Image uploaded.", state = "complete")
            with st.chat_message("human"):
                st.image(image_url)

    if prompt.text: 
        with st.chat_message("human"):
            st.write(prompt.text)
        asyncio.run(run_agent(prompt.text))


with st.sidebar: 
    reset = st.button("Reset memory")
    if reset: 
        asyncio.run(session.clear_session())

    st.write(asyncio.run(session.get_items()))