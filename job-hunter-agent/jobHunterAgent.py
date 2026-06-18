import dotenv

dotenv.load_dotenv()

from crewai import Crew, Agent, Task 
from crewai.project import CrewBase, agent, task, crew
from models import JobList, RankedJobList, ChosenJob
from tools import web_search_tool
from crewai.knowledge.source.text_file_knowledge_source import TextFileKnowledgeSource

resume_knowledge_source = TextFileKnowledgeSource(
    file_path=["resume.txt",]
)

@CrewBase 
class JobHunterCrew: 
    @agent 
    def job_search_agent(self): 
        return Agent(
            config=self.agents_config["job_search_agent"],
            tools=[web_search_tool],
        )
    @agent 
    def job_matching_agent(self): 
        return Agent(
            config=self.agents_config["job_matching_agent"],
            knowledge_sources=[resume_knowledge_source],
        )
    @agent 
    def resume_optimization_agent(self): 
        return Agent(
            config=self.agents_config["resume_optimization_agent"]
        )
    @agent 
    def company_search_agent(self): 
        return Agent(
            config=self.agents_config["company_search_agent"],
            knowledge_sources=[resume_knowledge_source],
            tools=[web_search_tool],
        )
    @agent 
    def iterview_prep_agent(self): 
        return Agent(
            config=self.agents_config["iterview_prep_agent"],
            knowledge_sources=[resume_knowledge_source],
        )
    @agent
    def translator_agent(self):
        return Agent(
            config=self.agents_config["translator_agent"],
        )
    @task 
    def job_extraction_task(self): 
        return Task(
            config=self.tasks_config["job_extraction_task"],
            output_pydantic=JobList,
        )
    @task 
    def job_matching_task(self): 
        return Task(
            config=self.tasks_config["job_matching_task"],
            output_pydantic=RankedJobList,
        )
    @task 
    def job_selection_task(self): 
        return Task(
            config=self.tasks_config["job_selection_task"],
            output_pydantic=ChosenJob,
        )
    @task 
    def resume_rewriting_task(self): 
        return Task(
            config=self.tasks_config["resume_rewriting_task"],
        )
    @task 
    def company_research_task(self): 
        return Task(
            config=self.tasks_config["company_research_task"],
            context=[
                self.job_selection_task(),
            ]
        )
    @task 
    def iterview_prep_task(self): 
        return Task(
            config=self.tasks_config["iterview_prep_task"],
            context=[
                self.job_selection_task(),
                self.resume_rewriting_task(),
                self.company_research_task(),
            ]
        )
    @task
    def translate_task(self):
        return Task(
            config=self.tasks_config["translate_task"],
        )
    @crew 
    def crew(self): 
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            verbose=True,
        )

JobHunterCrew().crew().kickoff(inputs={
    'level': 'Senior',
    'position': 'React Native Developer',
    'location': 'Seoul, Korea',
})