import os
import json
from src.services import LLMService
from src.agents import DataIngestionAgent, QuestionGenerationAgent, ContentWriterAgent, ComparisonAgent
from src.engine import TemplateEngine
from src.logic_blocks import format_currency_block, extract_safety_warning_block

API_KEY = os.getenv("OPENAI_API_KEY") 

def main():
    print("--- Starting Agentic Content System ---")
    llm = LLMService(api_key=API_KEY)
    engine = TemplateEngine()
    
    
    engine.register_template("product_page", {
        "title": "{{ name }}",
        "price_display": "{{ BLOCK:format_price }}",
        "safety_info": "{{ BLOCK:safety_logic }}",
        "details": "{{ usage_instructions }}"
    })
    
    engine.register_template("comparison_page", {
        "title": "Comparison: {{ name }} vs {{ comp_name }}",
        "our_price": "{{ price }}",
        "their_price": "{{ comp_price }}",
        "verdict": "{{ BLOCK:verdict_logic }}"
    })

    
    ingestor = DataIngestionAgent("Ingestor", llm)
    
    if not os.path.exists("input_data.json"):
        print("Error: input_data.json not found!")
        return

    with open("input_data.json", "r") as f: raw = json.load(f)
    product = ingestor.parse(raw)
    
    print("Generating Content...")
    q_agent = QuestionGenerationAgent("Q-Gen", llm)
    
    qs = q_agent.generate_questions(product) 
    
    writer = ContentWriterAgent("Writer", llm)
    faqs = writer.answer_faq(product, qs)
    
    comp_agent = ComparisonAgent("Comparator", llm)
    comp_data = comp_agent.create_competitor_and_compare(product)
    
    
    logic = {
        "format_price": lambda ctx: format_currency_block(ctx['price']),
        "safety_logic": lambda ctx: extract_safety_warning_block(ctx['side_effects']),
        "verdict_logic": lambda ctx: "Better Value" # Simple logic block
    }
    
    print("Writing Files...")
    
    
    prod_json = engine.render("product_page", product.dict(), logic)
    
    
    comp_context = {
        "name": product.name,
        "price": product.price,
        "comp_name": comp_data.get("Name", "Generic Brand"),
        "comp_price": comp_data.get("Price", "999"),
        "side_effects": product.side_effects
    }
    comp_json = engine.render("comparison_page", comp_context, logic)

    
    with open("product_page.json", "w") as f: json.dump(prod_json, f, indent=2)
    with open("faq.json", "w") as f: json.dump({"faqs": faqs}, f, indent=2)
    with open("comparison_page.json", "w") as f: json.dump(comp_json, f, indent=2)
    
    print("Done! generated: product_page.json, faq.json, comparison_page.json")

if __name__ == "__main__":
    main()