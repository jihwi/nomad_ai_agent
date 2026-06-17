from crewai.tools import tool
from crewai_tools import SerperDevTool
import time 
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

@tool
def count_letters(sentence: str):
    """
    This function is to count the amount of letters in a sentence.
    The input is a `sentence` string.
    The output is a number.
    """
    print("tool called with input :", sentence)
    return len(sentence)

search_tool = SerperDevTool(n_results=10,)

@tool
def scrape_tool(url:str):
    """
    Use this when you need to read the content of a website.
    Returns the content of a website, in case the website is not available, it returns 'No content'.
    Input should be a `url` string. for example (https://www.reuters.com/world/asia-pacific/cambodia-thailand-begin-talks-malaysia-amid-fragile-ceasefire-2025-08-04/)
    """

    print(f"Scrapping URL: {url}")

    with sync_playwright() as p: 
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)

        time.sleep(5)

        content = page.content()
        browser.close()

        soup = BeautifulSoup(content, 'html.parser')
        unwanted_tags = [
            "header",
            "footer",
            "nav",
            "aside",
            "script",
            "style",
            "noscript",
            "iframe",
            "form",
            "button",
            "input",
            "select",
            "textarea",
            "img",
            "svg",
            "canvas",
            "audio",
            "video",
            "embed",
            "object",
        ]

        for tag in unwanted_tags:
            for element in soup.find_all(tag):
                element.decompose()

        content = soup.get_text(separator=" ")
        return content if content != "" else "No content"