import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

def _get_gemini_model():
    """Initializes Google Gemini model for plan updates."""
    if not API_KEY or API_KEY == "your_gemini_api_key_here":
        return None
    try:
        import google.generativeai as genai
        genai.configure(api_key=API_KEY)
        for model_name in ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-2.0-flash", "gemini-2.5-flash"]:
            try:
                return genai.GenerativeModel(model_name)
            except Exception:
                continue
    except Exception:
        return None
    return None

def _apply_fallback_revision(original_plan: str, user_feedback: str) -> str:
    """Applies contextual feedback adjustments when running offline or without API key."""
    feedback_note = f"** [UPDATED BASED ON FEEDBACK: \"{user_feedback.strip()}\"] **\n\n"

    lines = original_plan.splitlines()
    revised_lines = [feedback_note]

    fb_lower = user_feedback.lower()
    for line in lines:
        if "cardio" in fb_lower and ("Day 3" in line or "Day 6" in line):
            revised_lines.append(line)
            revised_lines.append("  * Added Extra Cardio Burst: 20 mins Zone-2 treadmill incline walk or rowing")
        elif "yoga" in fb_lower and ("Day 4" in line or "Day 7" in line):
            revised_lines.append(line)
            revised_lines.append("  * Added Vinyasa Flow Yoga (30 mins) for deep mobility and mindfulness")
        elif ("rest" in fb_lower or "easy" in fb_lower) and "Day 5" in line:
            revised_lines.append(line.replace("Upper Body Pull", "Active Recovery & Light Stretching"))
            revised_lines.append("  * Adjusted to lower intensity: Light bodyweight mobility and foam rolling")
        else:
            revised_lines.append(line)

    return "\n".join(revised_lines)

def update_workout_plan(original_plan: str, user_feedback: str) -> str:
    """
    Use Gemini 1.5 Pro to update the workout plan based on user feedback.

    Args:
        original_plan (str): The existing 7-day workout plan text.
        user_feedback (str): Feedback submitted by the user.

    Returns:
        str: The revised workout plan.
    """
    prompt = f"""
You are a professional fitness trainer assistant.

Here's the original 7-day workout plan:
{original_plan}

User Feedback:
"{user_feedback}"

Based on the feedback, revise the relevant parts of the workout plan. Keep the format and rest of the plan unchanged if not needed.
"""
    model = _get_gemini_model()
    if model:
        try:
            response = model.generate_content(prompt)
            if response and response.text:
                return response.text.strip()
        except Exception:
            return _apply_fallback_revision(original_plan, user_feedback)

    return _apply_fallback_revision(original_plan, user_feedback)
