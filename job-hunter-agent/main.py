from firecrawl import FirecrawlApp
import os

app = FirecrawlApp(api_key=os.getenv("PIRECRAWL_API_KEY"))
### GS 웹 스크랩 테스트 (페이지네이션)
data = app.scrape_url(
    "https://m.gsshop.com/index.gs",
    formats=["markdown"],
    only_main_content=True,
    max_age=172800000,
    # actions 형식을 Firecrawl 규격에 맞게 전면 수정했습니다.
    actions=[
        { "type": "scroll", "direction": "down" },
        { "type": "wait", "milliseconds": 2000 }, # 만약 wait에서 또 에러가 나면 이 줄을 지우고 scroll만 남겨보세요
        { "type": "scroll", "direction": "down" },
        { "type": "wait", "milliseconds": 2000 }
    ]
)

print(data)