

def format_currency_block(price_str: str) -> str:
    """Standardizes currency formatting."""
    return price_str.replace("₹", "INR ").strip()

def extract_safety_warning_block(side_effects: str) -> str:
    """Generates a standard safety disclaimer based on side effects."""
    if "tingling" in side_effects.lower() or "irritation" in side_effects.lower():
        return f"⚠ Patch Test Recommended: {side_effects}"
    return "Dermatologically tested."

def generate_comparison_matrix(product_a, product_b_dict) -> dict:
    """Compares two products logic block."""
    return {
        "price_diff": f"{product_a.name} is {product_a.price} vs {product_b_dict['name']} at {product_b_dict['price']}",
        "ingredient_overlap": list(set(product_a.ingredients) & set(product_b_dict['ingredients']))
    }