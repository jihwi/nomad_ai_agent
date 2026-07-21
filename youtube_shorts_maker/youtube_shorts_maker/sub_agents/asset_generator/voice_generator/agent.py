from google.adk.agents import Agent 
from google.adk.models.lite_llm import LiteLlm 
from .prompt import VOICE_GENERATOR_DESCRIPTION, VOICE_GENERATOR_PROMPT
from .tools import generate_narrations

MODEL = LiteLlm(model="openai/gpt-4o")

voice_generator_agent = Agent(
    name="VoiceGeneratorAgent",
    model=MODEL, 
    instruction = VOICE_GENERATOR_PROMPT,
    description= VOICE_GENERATOR_DESCRIPTION,
    output_key = "voice_generator_output",
    tools=[
        generate_narrations
    ]
)