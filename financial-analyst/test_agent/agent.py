from dis import Instruction
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm 
from google.adk.tools.agent_tool import AgentTool

MODEL = LiteLlm("openai/gpt-4o")

def get_weather(city:str):
    return f"the weather in {city} is 30 degrees."

def convert_units(degrees: int):
    return f"That is 40 fareheit"

geo_agent = Agent(
    name="GeoAgent",
    instruction="Your help with geo questions",
    model=MODEL,
    description="Transfer to this agent when you have a geo related question."
)

weather_agent = Agent(
    name="WeatherAgent",
    instruction="You help the user with weather related questions",
    model=MODEL,
    tools=[
        get_weather, 
        convert_units, 
        # AgentTool(agent=geo_agent) # tool 방식으로 agent 사용 
    ],
    sub_agents=[ #handsoff와 동일 기능
        geo_agent
    ]
)

root_agent = weather_agent