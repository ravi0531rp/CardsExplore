from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
from loguru import logger
from typing import List, Dict
import os

load_dotenv()

def get_webpage_links(url: str, geolocation: Dict[str, float] = {"latitude": 12.971598, "longitude": 77.594666}) -> List[str]:
    """
    Extracts all links with class 'underline' from the given URL.

    Args:
        url (str): The URL of the webpage to extract data from.
        geolocation (Dict[str, float]): A dictionary containing latitude and longitude.

    Returns:
        List[str]: List of href links with class 'underline'.
    """
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-web-security",
                    "--disable-dev-shm-usage",
                    "--lang=en-US",
                ],
            )

            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080},
                locale="en-US",
                geolocation=geolocation,
                permissions=["geolocation"],
            )

            page = context.new_page()
            page.goto(url, wait_until="networkidle")

            # Extract all hrefs with class 'underline'
            links = page.eval_on_selector_all(
                "a.underline",
                "elements => elements.map(el => el.href)"
            )

            # Fallback to extracting from <p class="text-base"> if no links found
            if not links:
                links = page.eval_on_selector_all(
                    "p.text-base a",
                    "elements => elements.map(el => el.href)"
                )

            

            browser.close()
            logger.success(f"Extracted {len(links)} links successfully.")
            return links
        except Exception as e:
            logger.error(f"Error extracting links: {e}")
            return []

def main() -> None:
    """
    Main function to extract and print webpage links.
    """
    all_links = []
    banks = []
    with open("./banks.txt", 'r') as fr:
        banks = fr.read().split("\n")

    print(banks)

    for bnk in banks:
        url = os.getenv(f"{bnk}_BASE_URL")
        links = get_webpage_links(url)
        all_links.extend(links)
        print("Extracted Links:")
        for link in links:
            print(link)

        with open("./card_links.txt", "w") as fw:
            fw.write("\n".join(all_links))

if __name__ == "__main__":
    main()
