from google.adk.agents import Agent 
from google.adk.tools.agent_tool import AgentTool 
from google.adk.models.lite_llm import LiteLlm
from .prompt import PROMPT
from .sub_agents.data_analyst import data_analyst
from .sub_agents.financial_analyst import financial_analyst
from .sub_agents.news_analyst import news_analyst
from google.adk.tools import ToolContext
from google.genai import types

MODEL = LiteLlm(model="openai/gpt-4o-mini")

async def save_advice_report(tool_context:ToolContext, summary:str, ticker:str):
    state = tool_context.state
    data_analyst_result = state.get("data_analyst_result")
    financial_analyst_result = state.get("financial_analyst_result")
    news_analyst_analyst_result = state.get("news_analyst_analyst_result")
    
    
    report=f"""
        # Excetuve Summary and Advice:
        {summary}

        ## Data Analyst Report:
        {data_analyst_result}

        ## Financial Analyst Report:
        {financial_analyst_result}
        
        ## News Analyst Report:
        {news_analyst_analyst_result}
    """
    state["report"] = report

    file_name = f"{ticker}_investment_advice.md"
    artifact = types.Part(
        inline_data = types.Blob(
            mime_type="text/markdown",
            data=report.encode("utf-8")
        )
    ) # 파일 타입 정의 

    await tool_context.save_artifact(file_name, artifact)

    return {
        "success": True
    }


financial_advisor = Agent(
    name="FinancailAdvisor",
    instruction=PROMPT,
    model=MODEL, 
    tools=[
        AgentTool(agent=data_analyst),
        AgentTool(agent=financial_analyst),
        AgentTool(agent=news_analyst),
        save_advice_report
    ]
)

root_agent = financial_advisor