from google.adk.agents import Agent 
from google.adk.models.lite_llm import LiteLlm 
from .prompt import VIDEO_ASSEMBLER_DESCRIPTION, VIDEO_ASSEMBLER_PROMPT
from .tools import assemble_video

MODEL = LiteLlm(model="openai/gpt-4o")

video_assembler_agent = Agent(
    name="VideoAssemblerAgent",
    instruction=VIDEO_ASSEMBLER_PROMPT,
    description=VIDEO_ASSEMBLER_DESCRIPTION,
    model=MODEL,
    tools=[
        assemble_video
    ]
)