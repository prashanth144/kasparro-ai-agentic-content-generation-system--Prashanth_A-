from pydantic import BaseModel, Field
from typing import List, Optional

class Product(BaseModel):
    name: str
    concentration: Optional[str] = None
    skin_type: List[str]
    ingredients: List[str]
    benefits: List[str]
    usage_instructions: str
    side_effects: Optional[str] = None
    price: str

class FAQItem(BaseModel):
    question: str
    answer: str
    category: str

class ContentPage(BaseModel):
    page_type: str
    content: dict