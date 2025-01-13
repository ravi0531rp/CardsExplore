from typing import List, Dict, Any
from PIL import Image
from io import BytesIO
from loguru import logger
from json_repair import repair_json
import json
import os
import io
import google.generativeai as genai
from schemas import CardResult

def create_chunks(image: Image.Image, crop_height: int = 500, overlap: int = 200) -> List[Image.Image]:
    """
    Crops an image into overlapping vertical sections.

    Args:
        image (PIL.Image.Image): Input image.
        crop_height (int): Height of each crop.
        overlap (int): Overlap between crops.

    Returns:
        List[PIL.Image.Image]: List of cropped images.
    """
    width, height = image.size
    num_crops = (height + crop_height - 1) // crop_height
    png_crops = []

    for i in range(num_crops):
        upper = max(0, i * crop_height - (overlap if i > 0 else 0))
        lower = min(height, upper + crop_height + (overlap if i < num_crops - 1 else 0))
        cropped_image = image.crop((0, upper, width, lower))
        buffer = io.BytesIO()
        cropped_image.save(buffer, format="PNG")
        buffer.seek(0)
        png_image = Image.open(buffer)
        png_crops.append(png_image)
    logger.debug(f"{len(png_crops)} chunks created with overlap of {overlap}.")
    return png_crops

def save_raw_page(img: Image.Image, path: str) -> None:
    """
    Saves an image to the specified file path.

    Args:
        img (PIL.Image.Image): Image to save.
        path (str): Path to save the image.
    """
    img.save(path)
    logger.success(f"Image saved at {path}")

def load_raw_webpage_data(image_path: str) -> Image.Image:
    """
    Loads an image from the specified path.

    Args:
        image_path (str): Path to the image file.

    Returns:
        PIL.Image.Image: Loaded image.
    """
    return Image.open(image_path)

def str2json(json_str: str) -> Any:
    """
    Repairs and parses a JSON string.

    Args:
        json_str (str): JSON string to parse.

    Returns:
        Any: Parsed JSON data.
    """
    return json.loads(repair_json(json_str))

def gemini_parser(images: List[Image.Image]) -> Dict[str, Any]:
    """
    Uses Gemini AI to extract card information from images.

    Args:
        images (List[PIL.Image.Image]): List of cropped images.

    Returns:
        Dict[str, Any]: Extracted card information.
    """
    json_schema = CardResult.model_json_schema()
    prompt = "List out the Card details."
    model = genai.GenerativeModel(
        "models/gemini-1.5-flash",
        system_instruction=f"""You are a helpful assistant that scans for
        credit card details from webpage screenshots. Use this JSON schema:
        CardInfo = {json_schema}
        Return a `CardInfo`
        """,
        generation_config={"response_mime_type": "application/json"},
    )
    final_prompt = [prompt] + images
    response = model.generate_content(final_prompt)
    data = str2json(response.text)
    return data

def save_json(json_data: Dict[str, Any], file_path: str) -> None:
    """
    Saves JSON data to a file.

    Args:
        json_data (Dict[str, Any]): JSON data to save.
        file_path (str): Path to save the JSON file.
    """
    with open(file_path, "w") as f:
        json.dump(json_data, f, indent=4)
    logger.success(f"JSON data saved at {file_path}")
