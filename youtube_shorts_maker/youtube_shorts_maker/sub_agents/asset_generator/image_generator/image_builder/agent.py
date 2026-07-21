from .prompt import IMAGE_BUILDER_DESCRIPTION, IMAGE_BUILDER_PROMPT
from google.adk.agents import Agent 
from google.adk.models.lite_llm import LiteLlm 
from .tools import generate_images

MODEL = LiteLlm(model="openai/gpt-4o")

image_builder_agent = Agent(
    name="ImageBuilderAgent",
    instruction=IMAGE_BUILDER_PROMPT,
    description=IMAGE_BUILDER_DESCRIPTION,
    model=MODEL, 
    output_key="image_builder_output",
    tools=[
        generate_images
    ]
)