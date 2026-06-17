import dotenv

dotenv.load_dotenv()

from crewai import Crew, Agent, Task 
from crewai.project import CrewBase, agent, crew, task 
from tools import scrape_tool, search_tool

@CrewBase
class NewsReaderAgent: 
    @agent
    def news_hunter_agent(self):
        return Agent(
            config=self.agents_config["news_hunter_agent"],
            tools=[search_tool, scrape_tool],
        )
    @agent
    def summarizer_agent(self):
        return Agent(
            config=self.agents_config["summarizer_agent"],
            tools=[scrape_tool],
        )
    @agent
    def curator_agent(self):
        return Agent(
            config=self.agents_config["curator_agent"],
        )
    @agent 
    def translator_agent(self):
        return Agent(
            config=self.agents_config["translator_agent"],
        )
        
    @task
    def content_harvesting_task(self): 
        return Task(
            config=self.tasks_config["content_harvesting_task"],
        )
    @task
    def summarization_task(self): 
        return Task(
            config=self.tasks_config["summarization_task"],
        )
    @task
    def final_report_assembly_task(self): 
        return Task(
            config=self.tasks_config["final_report_assembly_task"],
        )

    @task
    def translate_task(self):
        return Task(
            config=self.tasks_config["translate_task"],
        )
    @crew
    def crew(self):
        return Crew(
            agents= self.agents,
            tasks= self.tasks,
            verbose= True,
        )

result = NewsReaderAgent().crew().kickoff(inputs={"topic": "선관위"})

for task_output in result.tasks_output:
    print(task_output)
