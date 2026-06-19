from crewai.flow.flow import Flow, listen, start, router, and_, or_
from pydantic import BaseModel

class MyFirstFlowState(BaseModel):
    user_id : int = 1
    is_admin: bool = False

class MyFirstFlow(Flow[MyFirstFlowState]):
    @start()
    def first(self):
        # self.state["whatever"] = 2
        self.state.user_id = 2
        print("hello")

    @listen(first)
    def second(self):
        print("world")

    @listen(first)
    def third(self): 
        # print(self.state["whatever"])
        print(self.state.user_id)
        print("!")

    @listen(and_(second, third))
    def final(self):
        # self.state["whatever"] = 1
        self.state.user_id = 1
        print(":)")

    @router(final)
    def route(self):
        if self.state.is_admin:
            return "even"
        else:
            return "odd"

    @listen("even")
    def handle_even(self):
        print(self.state.user_id)
        print("even")

    @listen("odd")
    def handle_add(self):
        print(self.state.user_id)
        print("odd")

flow = MyFirstFlow()
flow.plot() 

flow.kickoff()