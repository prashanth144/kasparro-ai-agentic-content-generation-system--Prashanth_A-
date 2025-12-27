import json
from .models import Product
from .services import LLMService

class BaseAgent:
    def __init__(self, name: str, llm: LLMService):
        self.name = name
        self.llm = llm

class DataIngestionAgent(BaseAgent):
    """Parses raw input into structured Pydantic models."""
    def parse(self, raw_data: dict) -> Product:

        return Product(
            name=raw_data.get("Product Name"),
            concentration=raw_data.get("Concentration"),
            skin_type=[s.strip() for s in raw_data.get("Skin Type", "").split(",")],
            ingredients=[i.strip() for i in raw_data.get("Key Ingredients", "").split(",")],
            benefits=[b.strip() for b in raw_data.get("Benefits", "").split(",")],
            usage_instructions=raw_data.get("How to Use"),
            side_effects=raw_data.get("Side Effects"),
            price=raw_data.get("Price")
        )

class QuestionGenerationAgent(BaseAgent):
    """Generates user questions based on product data."""
    def generate_questions(self, product: Product, count: int = 15) -> list:
        prompt = (
            f"Generate exactly {count} user questions about {product.name}."
            f"Categories: Usage, Safety, Ingredients, Comparison."
            f"Context: {product.model_dump_json()}"
            f"Output JSON format: {{ 'questions': [ {{ 'category': '...', 'text': '...' }} ] }}"
        )
        response = self.llm.generate_json(prompt, "You are a customer support simulation agent.")
        return response.get("questions", [])

class ContentWriterAgent(BaseAgent):
    """Answers questions and writes descriptions."""
    def answer_faq(self, product: Product, questions: list) -> list:

        selected_qs = questions[:5]
        faqs = []
        for q in selected_qs:
            prompt = f"Answer this question for {product.name} based ONLY on this data: {product.model_dump_json()}. Question: {q['text']}"
            ans = self.llm.generate_completion(prompt)
            faqs.append({"question": q['text'], "answer": ans, "category": q['category']})
        return faqs

class ComparisonAgent(BaseAgent):
    """Generates competitor data and compares."""
    def create_competitor_and_compare(self, product: Product):
        
        prompt = "Create a fictional competitor serum (Product B) with Name, Price (higher), Ingredients (different), and Benefits. Output JSON."
        prod_b = self.llm.generate_json(prompt, "You are a creative product designer.")
        
        return prod_b