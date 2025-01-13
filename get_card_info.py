from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
from loguru import logger
from typing import List, Dict, Optional
from PIL import Image
from io import BytesIO
import google.generativeai as genai
import time
import os
from utils import (
    create_chunks,
    save_raw_page,
    load_raw_webpage_data,
    str2json,
    gemini_parser,
    save_json
)

load_dotenv()

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

def get_raw_data(url: str, geolocation: Dict[str, float] = {"latitude": 12.971598, "longitude": 77.594666}) -> Optional[Image.Image]:
    """
    Captures a full-page screenshot of the given URL.

    Args:
        url (str): The webpage URL to capture.
        geolocation (Dict[str, float], optional): Geolocation for the browser context.

    Returns:
        Optional[Image.Image]: Screenshot as a PIL Image or None if an error occurs.
    """
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0",
                viewport={"width": 1920, "height": 1080},
                geolocation=geolocation,
                permissions=["geolocation"],
            )
            page = context.new_page()
            page.goto(url, wait_until="networkidle")
            screenshot_bytes = page.screenshot(full_page=True)
            browser.close()
            return Image.open(BytesIO(screenshot_bytes))
        except Exception as e:
            logger.error(f"Error capturing screenshot: {e}")
            return None

def get_info_from_raw_page(url: str, image_dir: str, json_dir: str) -> None:
    """
    Extracts and saves card data from a webpage.

    Args:
        url (str): Webpage URL.
        image_dir (str): Directory to save images.
        json_dir (str): Directory to save JSON data.
    """
    card_name = url.split('/')[-1].replace('.html', '')
    fp_image = get_raw_data(url)
    if not fp_image:
        logger.error(f"Failed to fetch data for {url}")
        return

    save_path = os.path.join(image_dir, f"{card_name}.png")
    save_raw_page(fp_image, save_path)
    logger.success(f"Saved {card_name}.png")

    img = load_raw_webpage_data(save_path)
    crops = create_chunks(img)
    resp = gemini_parser(crops)
    save_json(resp, os.path.join(json_dir, f"{card_name}.json"))
    logger.success(f"Saved JSON data for {card_name}")

if __name__ == "__main__":
    image_dir = "./cards_data/images"
    json_dir = "./cards_data/jsons"
    urls_file = "./card_links.txt"
    
    os.makedirs(image_dir, exist_ok=True)
    os.makedirs(json_dir, exist_ok=True)
    
    with open(urls_file, 'r') as fr:
        urls = [url.strip() for url in fr.read().split("\n") if url.strip()]
    
    for url in urls:
        try:
            get_info_from_raw_page(url, image_dir, json_dir)
        except Exception as e:
            logger.error(f"Error {e} for {url}")
        time.sleep(30)
