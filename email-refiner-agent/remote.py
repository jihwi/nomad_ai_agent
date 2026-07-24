import vertexai 
from vertexai import agent_engines

## 타 서비스에서 호출한다는 가정하. 

PROJECT_ID="TEST"
LOCATION="europe-southwest1"

vertexai.init(
    project=PROJECT_ID,
    location=LOCATION
)


deployments = agent_engines.list()

for deployment in deployments:
    print(deployment)

DEPLOYMENT_ID = "projects/23382131925/locations/europe-southwest1/reasoningEngines/2153529862441140224"

remote_app = agent_engines.get(DEPLOYMENT_ID)

remote_session = remote_app.create_session(user_id="u_123")

print(remote_session["id"])

SESSION_ID = "5724511082748313600"

for event in remote_app.stream_query(
    user_id="u_123",
    session_id=SESSION_ID,
    message="I'm going to Laos, any tips?",
):
    print(event, "\n", "=" * 50)


#remote_app.delete(force=True) #비용이슈로 배포했던 agent 삭제