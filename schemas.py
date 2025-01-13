from pydantic import BaseModel, Field
from typing import Dict
from dotenv import load_dotenv

load_dotenv()

class CardResult(BaseModel):
    """
    Information about the card. For currency, use Rs. instead of ₹
    """
    card_name: str = Field(..., description="Name of the credit card")
    card_issuer: str = Field(..., description="Name of the credit card issuing bank")
    fee_details: str = Field(..., description="Entire fee structure Details in bullet points")
    joining_perks: str = Field(..., description="Entire fee structure Details in bullet points")
    reward_structure: str = Field(..., description="Entire Reward Structure in bullet points")
    key_highlights: str = Field(..., description="key Highlights of the Card in bullet points")
    benefits_features: Dict[str, str] = Field(..., description="Benefits and features of the cards in a key value pair, with benefit heading being the key, & description being the value. Example of keys : Travel benefits, Fuel benefits, Dining benefits, Renewal benefits, Lounge benefits. And in the values, include in detail what they are and how those benefits are availed.")
    how_tos: Dict[str, str] = Field(..., description="All the how tos mentioned in the page for all queries and their descriptions in a key value pair")
    reward_point_benefits: str = Field(..., description="Reward Point Structure in detailed bullet points")
    fees_and_charges: Dict[str, str] = Field(..., description="A key value pair with types of fees and Amount")
    miscellaneous: str = Field(..., description = "Any feature which we have not explicitly mentioned and is specific to the card.")
    faqs: Dict[str, str] = Field(..., description="A key value pair of Faqs and Answers in detail")

