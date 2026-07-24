from google.adk.agents import LoopAgent, Agent
from google.adk.models.lite_llm import LiteLlm
from .prompt import (
    EMAIL_OPTIMIZER_DESCRIPTION,
    TONE_STYLIST_DESCRIPTION,
    CLARITY_EDITOR_DESCRIPTION,
    LITERARY_CRITIC_DESCRIPTION,
    EMAIL_SYNTHESIZER_DESCRIPTION,
    PERSUASION_STRATEGIST_DESCRIPTION,
    TONE_STYLIST_INSTRUCTION,
    CLARITY_EDITOR_INSTRUCTION,
    LITERARY_CRITIC_INSTRUCTION,
    EMAIL_SYNTHESIZER_INSTRUCTION,
    PERSUASION_STRATEGIST_INSTRUCTION,
)
from google.adk.tools.tool_context import ToolContext

MODEL = LiteLlm(model="openai/gpt-4o")

clarity_agent = Agent(
    name="ClarityEditorAgent",
    description=CLARITY_EDITOR_DESCRIPTION,
    instruction=CLARITY_EDITOR_INSTRUCTION,
    output_key="clarity_output",
    model=MODEL,
)

tone_stylist_agent = Agent(
    name="ToneStylistAgent",
    description=TONE_STYLIST_DESCRIPTION,
    instruction=TONE_STYLIST_INSTRUCTION,
    output_key="tone_output",
    model=MODEL,
)

persuation_agent = Agent(
    name="PersuationAgent",
    description=PERSUASION_STRATEGIST_DESCRIPTION,
    instruction=PERSUASION_STRATEGIST_INSTRUCTION,
    output_key="persuasion_output",
    model=MODEL,
)

email_synthesizer_agent = Agent(
    name="EmailSynthesizerAgent",
    description=EMAIL_SYNTHESIZER_DESCRIPTION,
    instruction=EMAIL_SYNTHESIZER_INSTRUCTION,
    output_key="synthesized_output",
    model=MODEL,
)

def escalate_email_complete(tool_context:ToolContext):
    """Use this tool only when the email is good to go."""
    tool_context.actions.escalate = True #loop를 끊는다 or subAgent 호출이 끝나고 상위 부모 agent로 돌아감. (openai sdk와 달리 sub_agent에서 상위 부모로 올라가는 기능이 존재.)
    return "Email optimization complete. "

literary_critic_agent = Agent(
    name="LiteraryCriticAgent",
    description=LITERARY_CRITIC_DESCRIPTION,
    instruction=LITERARY_CRITIC_INSTRUCTION,
    tools=[
        escalate_email_complete,
    ],
    model=MODEL,
)

#model 머리가 없기때문에 대화를 하지않음. 바로 user의 text를 가지고 sub_agents 실행됨. 
email_refiner_agent = LoopAgent(
    name="EmailRefinerAgent",
    max_iterations=50, #최대 루프 횟수  
    description=EMAIL_OPTIMIZER_DESCRIPTION,
    sub_agents=[
        clarity_agent,
        tone_stylist_agent,
        persuation_agent,
        email_synthesizer_agent,
        literary_critic_agent
    ]
)

root_agent = email_refiner_agent