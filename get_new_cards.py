from get_card_info import get_info_from_raw_page
from langchain_community.tools import TavilySearchResults
from dotenv import load_dotenv
from loguru import logger
import google.generativeai as genai
import json
from typing import Optional, List, Dict, Any

load_dotenv()

def tavily_card_search(topic: str) -> List[Dict[str, Any]]:
    """
    Performs a web search using TavilySearchResults to find BankBazaar pages related to the specified credit card topic.
    
    Args:
        topic (str): The credit card topic to search for.
        
    Returns:
        List[Dict[str, Any]]: A list of search result dictionaries containing URLs and content.
    """
    tool = TavilySearchResults(
        max_results=5,
        search_depth="advanced",
        include_answer=True,
        include_raw_content=True
    )
    responses = tool.invoke({"query": f"Bankbazaar page for {topic}"})
    logger.info(f"Search results for topic '{topic}': {responses}")
    return responses

def clean_url(url: str) -> str:
    """
    Cleans a URL by stripping whitespace and removing newline characters.
    
    Args:
        url (str): The URL to clean.
        
    Returns:
        str: The cleaned URL.
    """
    return url.strip().replace("\n", "")

def fetch_url(model: genai.GenerativeModel, topic: str) -> Optional[str]:
    """
    Uses a generative model to extract the most relevant URL for a given credit card topic from search results.
    
    Args:
        model (genai.GenerativeModel): The generative model to process search results.
        topic (str): The credit card topic to search for.
        
    Returns:
        Optional[str]: The most relevant URL or None if extraction fails.
    """
    responses = tavily_card_search(topic)
    logger.info(f"Generating URL from search responses for topic '{topic}'")
    try:
        url = model.generate_content(json.dumps(responses)).text
        cleaned_url = clean_url(url)
        logger.info(f"Generated URL: {cleaned_url}")
        return cleaned_url
    except Exception as e:
        logger.error(f"Error generating URL for topic '{topic}': {e}")
        return None

def save_new_card_info(model: genai.GenerativeModel, topic: str, image_dir: str, json_dir : str) -> None:
    """
    Fetches the most relevant URL for a credit card topic and retrieves detailed card information from the page.
    
    Args:
        model (genai.GenerativeModel): The generative model to extract the URL.
        topic (str): The credit card topic to process.
    """
    url = fetch_url(model, topic)
    if url:
        get_info_from_raw_page(url, image_dir, json_dir)
        logger.info(f"Card information retrieved and saved for topic '{topic}'.")
    else:
        logger.warning(f"Failed to retrieve URL for topic '{topic}'.")

def main() -> None:
    """
    Main function to initiate the credit card information retrieval process.
    """
    topic = "Sbi Pulse Credit Card"
    image_dir = "./cards_data/images"
    json_dir = "./cards_data/jsons"
    model = genai.GenerativeModel(
        "models/gemini-1.5-flash",
        system_instruction=f"""
        You are a helpful assistant that takes in a web search result and returns the most relevant URL for the Credit Card information page.
        The user has queried to get a page from BankBazaar for {topic}. Return only the URL you think is most relevant.
        """
    )
    save_new_card_info(model, topic, image_dir, json_dir)

if __name__ == "__main__":
    main()
