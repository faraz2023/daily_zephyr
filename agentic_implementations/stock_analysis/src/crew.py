from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
import tools
from langchain_openai import ChatOpenAI
from crewai_tools import ScrapeWebsiteTool, SerperDevTool



@CrewBase
class StockanalysisCrew():
    """stock_analysis crew"""


    @agent
    def financial_researcher(self) -> Agent:
        search_tool = SerperDevTool()
        scrape_tool = ScrapeWebsiteTool()
        return Agent(
            config=self.agents_config['financial_researcher'],
            tools=[tools.query_perplexity,search_tool, scrape_tool],  # add tools here or use `agentstack tools add <tool_name>
            verbose=True,
            allow_delegation=True
        )
    
    @agent
    def main_writer(self) -> Agent:
        print("-----")
        print("self.agents_config")
        print(self.agents_config)
        return Agent(
            config=self.agents_config['main_writer'],
            tools=[tools.query_perplexity],
            verbose=True, 
            allow_delegation=True
        )
    
    @agent
    def editor(self) -> Agent:
        return Agent(
            config=self.agents_config['editor'],
            tools=[tools.query_perplexity],
            verbose=True, 
            allow_delegation=True
        )
    
    @agent
    def final_writer(self) -> Agent:
        return Agent(
            config=self.agents_config['final_writer'],
            tools=[],
            verbose=True, 
            allow_delegation=True
        )

    def manager(self) -> Agent:
        return Agent(
            config=self.agents_config['manager'],
            tools=[],
            verbose=True, 
            allow_delegation=True
        )

    # Task definitions

    @task
    def market_data_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['market_data_analysis_task'],
        )

    @task
    def draft_report(self) -> Task:
        return Task(
            config=self.tasks_config['draft_report'],
        )

    @task
    def data_distilation_and_critique_task(self) -> Task:
        return Task(
            config=self.tasks_config['data_distilation_and_critique_task'],
        )
    
    @task
    def finalize_report(self) -> Task:
        return Task(
            config=self.tasks_config['finalize_report'],
        )
    
    

    @crew
    def crew(self) -> Crew:
        """Creates the Test crew"""
        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            verbose=True,
            # memory=True,
            planning=True,
            manager_agent=self.manager(),
            process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
