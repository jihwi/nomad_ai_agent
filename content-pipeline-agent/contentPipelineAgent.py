from crewai.flow.flow import Flow, listen, start, router, and_, or_
from pydantic import BaseModel
from tools import web_search_tool
from crewai.agent import Agent
from crewai import LLM
from typing import List
from seo_crew import SEOCrew
from virality_crew import ViralityCrew

class BlogPost(BaseModel):
    title: str
    subtitle: str
    sections: List[str]


class Tweet(BaseModel):
    content: str
    hashtags: str


class LinkedInPost(BaseModel):
    hook: str
    content: str
    call_to_action: str

class Score(BaseModel):
    score: int = 0
    reason: str = "" 

class ContentPipelineFlowState(BaseModel):
    #input
    content_type: str = "" 
    topic : str = "" 

    #internal
    max_length: int = 0
    score: Score | None = None
    research: str = "" 

    blog_post: BlogPost | None = None
    tweet: Tweet | None = None
    linkedin_post: LinkedInPost | None = None

class ContentPipelineFlow(Flow[ContentPipelineFlowState]):
    @start() 
    def init_content_pipeline(self): 

        if (self.state.content_type not in ["tweet", "blog", "linkedin"]): 
            raise ValueError("The content type is wrong.")

        if (self.state.topic == ""):
            raise ValueError("The topic can't be blank.")

        if (self.state.content_type == "tweet"):
            self.state.max_length = 150
        elif (self.state.content_type == "blog"):
            self.state.max_length = 800
        elif (self.state.content_type == "linkedin"):
            self.state.max_length = 5000

    @listen(init_content_pipeline)
    def conduct_research(self):
        researcher = Agent(
            role="Head Researcher",
            backstory="You're like a digital detective who loves digging up fascinating facts and insights. You have a knack for finding the good stuff that others miss.",
            goal=f"Find the most interesting and useful info about {self.state.topic} and return it in a structured format.",
            tools=[web_search_tool],
        )

        self.state.research = researcher.kickoff(f"Find the most interesting and useful info about {self.state.topic} and return it in a structured format.")

    @router(conduct_research)
    def route(self):
        content_type = self.state.content_type

        if (content_type == "tweet"):
            return "make_tweet"
        elif (content_type == "blog"):
            return "make_blog"
        elif (content_type == "linkedin"):
            return "make_linkedin_post"

    @listen(or_("make_tweet", "remake_tweet"))
    def handle_make_tweet(self):
        tweet = self.state.tweet

        llm = LLM(
            model="openai/o4-mini",
            response_format=Tweet,
        )

        if (tweet is None):
            self.state.tweet = llm.call(
                f"""
                Make a tweet that can go viral on the topic {self.state.topic} using the following research:

                <research>
                ================
                {self.state.research}
                ================
                </research>
                """
            )
        else : 
            self.state.tweet = llm.call(
                f"""
                You wrote this tweet on {self.state.topic}, but it does not have a good virality score because of {self.state.score.reason} 
            
                Improve it.

                <tweet>
                {self.state.tweet.model_dump_json()}
                </tweet>

                Use the following research.

                <research>
                ================
                {self.state.research}
                ================
                </research>
                """
            )

    @listen(or_("make_blog", "remake_blog"))
    def handle_make_blog(self):
        blog_post = self.state.blog_post

        llm = LLM(
            model="openai/o4-mini",
            response_format=BlogPost,
        )

        if (blog_post is None):
            self.state.blog_post = llm.call(
                f"""
                Make a blog post on the topic {self.state.topic} using the following research:

                <research>
                ================
                {self.state.research}
                ================
                </research>
                """
            )
        else : 
            self.state.blog_post = llm.call(
                f"""
                You wrote this blog post on {self.state.topic}, but it does not have a good SEO score because of {self.state.score.reason} 
            
                Improve it.

                <blog post>
                {self.state.blog_post.model_dump_json()}
                </blog post>

                Use the following research.

                <research>
                ================
                {self.state.research}
                ================
                </research>
                """
            )


    @listen(or_("make_linkedin_post", "remake_linkedin_post"))
    def handle_make_linkedin_post(self):
        linkedin_post = self.state.linkedin_post

        llm = LLM(
            model="openai/o4-mini",
            response_format=LinkedInPost,
        )

        if (linkedin_post is None):
            self.state.linkedin_post = llm.call(
                f"""
                Make a linkedin post that can go viral on the topic {self.state.topic} using the following research:

                <research>
                ================
                {self.state.research}
                ================
                </research>
                """
            )
        else : 
            self.state.linkedin_post = llm.call(
                f"""
                You wrote this linkedin post on {self.state.topic}, but it does not have a good virality score because of {self.state.score.reason} 
            
                Improve it.

                <linkedin_post>
                {self.state.linkedin_post.model_dump_json()}
                </linkedin_post>

                Use the following research.

                <research>
                ================
                {self.state.research}
                ================
                </research>
                """
            )

    @listen(handle_make_blog)
    def check_seo(self):
        seo_result = SEOCrew().crew().kickoff(
            inputs={
                "blog_post": self.state.blog_post.model_dump_json(),
                "topic": self.state.topic,
            }
        )
        self.state.score = seo_result.pydantic
    
    @listen(or_(handle_make_tweet, handle_make_linkedin_post))
    def check_virality(self):
        virality_result = ViralityCrew().crew().kickoff(
            inputs={
                "content_type": self.state.content_type,
                "topic": self.state.topic,
                "content": self.state.tweet.model_dump_json() if self.state.content_type == "tweet" 
                                else self.state.linkedin_post.model_dump_json()
            }
        )
        self.state.score = virality_result.pydantic 
    
    
    @router(or_(check_seo, check_virality))
    def score_router(self):

        content_type = self.state.content_type
        score = self.state.score 

        if (score.score >= 8):
            return "check_passed"
        else:
            if (content_type == "tweet"):
                return "remake_tweet"
            elif (content_type == "blog"):
                return "remake_blog"
            elif (content_type == "linkedin"):
                return "remake_linkedin_post"


    @listen("check_passed")
    def finalize_content(self):
        print("Finalizing content...")
        

flow = ContentPipelineFlow()
flow.kickoff(inputs={
    'content_type': 'blog',
    'topic': 'The Future of AI',
})