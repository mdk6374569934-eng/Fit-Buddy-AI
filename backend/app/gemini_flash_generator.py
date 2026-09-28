import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

def _get_flash_model():
    """Initializes Google Gemini Flash model for lightweight, fast responses."""
    if not API_KEY or API_KEY == "your_gemini_api_key_here":
        return None
    try:
        import google.generativeai as genai
        genai.configure(api_key=API_KEY)
        for model_name in ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-2.5-flash", "gemini-1.5-pro"]:
            try:
                return genai.GenerativeModel(model_name)
            except Exception:
                continue
    except Exception:
        return None
    return None

def _get_fallback_nutrition_tip(goal: str) -> str:
    """Returns an actionable, evidence-based nutrition/recovery tip based on the goal."""
    g = (goal or "").lower()
    if "loss" in g or "weight" in g or "fat" in g:
        return "Prioritize protein and fiber in every meal! Aim for at least 25-30g of lean protein (like grilled chicken, eggs, lentils, or Greek yogurt) paired with green vegetables to keep you full, preserve lean muscle, and stabilize energy throughout the day."
    elif "muscle" in g or "gain" in g or "bulk" in g:
        return "Fuel muscle synthesis with a balanced post-workout window: consume 25-35g of complete protein along with fast-digesting carbohydrates (like a banana with whey protein or oatmeal with almond butter) within 45 minutes after training."
    elif "endurance" in g or "stamina" in g or "run" in g:
        return "Maintain optimal glycogen stores and electrolyte balance! Drink 500ml of water with a pinch of pink Himalayan salt and lemon 30 minutes before hard cardio, and refuel with complex carbs like sweet potatoes or quinoa."
    else:
        return "Stay hydrated and focus on whole foods: aim for 2.5 to 3 liters of fresh water daily, and make half of every plate colorful vegetables and healthy fats like avocado and olive oil for optimal recovery and joint health."

def generate_nutrition_tip_with_flash(goal: str) -> str:
    """
    Generate a nutrition or recovery tip using Gemini Flash based on the user's fitness goal.

    Args:
        goal (str): User's fitness goal - "weight loss", "muscle gain", or "general fitness".

    Returns:
        str: Generated tip.
    """
    prompt = (
        f"Give one clear, helpful nutrition or recovery tip for someone focused on '{goal}'. "
        "The tip should be practical, friendly, and easy to understand."
    )

    model = _get_flash_model()
    if model:
        try:
            response = model.generate_content(prompt)
            if response and response.text:
                return response.text.strip()
        except Exception:
            return _get_fallback_nutrition_tip(goal)

    return _get_fallback_nutrition_tip(goal)
