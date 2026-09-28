import os
from dotenv import load_dotenv

# Load environment variables from .env file if available
load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

def _get_gemini_model():
    """Initializes Google Gemini model with the available API key."""
    if not API_KEY or API_KEY == "your_gemini_api_key_here":
        return None
    try:
        import google.generativeai as genai
        genai.configure(api_key=API_KEY)
        # Try gemini-1.5-pro as specified in the PDF, with fallback to gemini-1.5-flash or gemini-2.0-flash
        for model_name in ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-2.0-flash", "gemini-2.5-flash"]:
            try:
                return genai.GenerativeModel(model_name)
            except Exception:
                continue
    except Exception:
        return None
    return None

def _generate_fallback_plan(goal: str, intensity: str) -> str:
    """Provides a structured, realistic 7-day fitness plan when API key is not yet set."""
    g = (goal or "general wellness").lower()
    intens = (intensity or "medium").title()

    return f"""** 7-Day Personalized Workout Plan for {goal.title()} ({intens} Intensity) **

Day 1: Upper Body Push & Core
- Warm-up (5-10 mins): Arm circles, chest openers, shoulder rotations, jumping jacks (2 mins).
- Main Workout:
  * Incline Dumbbell Bench Press: 3 sets of 10-12 reps
  * Overhead Dumbbell Shoulder Press: 3 sets of 10 reps
  * Push-ups (standard or knee-supported): 3 sets to failure
  * Tricep Cable/Band Pushdowns: 3 sets of 12-15 reps
  * Plank hold: 3 sets of 45-60 seconds
- Cooldown or recovery tip: 5 mins static chest and shoulder stretches. Hydrate with electrolyte water.

Day 2: Lower Body & Glutes
- Warm-up (5-10 mins): Bodyweight squats, dynamic leg swings, hip circles, light jog in place.
- Main Workout:
  * Barbell or Goblet Squats: 4 sets of 8-10 reps
  * Romanian Deadlifts (RDLs): 3 sets of 10-12 reps
  * Walking Lunges: 3 sets of 12 reps per leg
  * Glute Bridges / Hip Thrusts: 3 sets of 15 reps
  * Standing Calf Raises: 3 sets of 20 reps
- Cooldown or recovery tip: Foam roll hamstrings and quads. 5 mins deep diaphragmatic breathing.

Day 3: Cardiovascular Conditioning & HIIT
- Warm-up (5-10 mins): Brisk walking/jogging, high knees, dynamic torso twists.
- Main Workout:
  * Interval Sprints (Treadmill, Bike, or Track): 30s max effort, 60s recovery (8-10 rounds)
  * Kettlebell Swings: 4 sets of 15 reps
  * Mountain Climbers: 3 sets of 30 seconds
  * Jump Squats or Step-ups: 3 sets of 12 reps
- Cooldown or recovery tip: Light walking cooldown followed by full-body mobility stretching.

Day 4: Active Recovery & Mobility
- Warm-up: Gentle neck and spinal rolls.
- Main Workout:
  * 30-45 minutes brisk outdoor walk or gentle swimming
  * Cat-Cow poses and child's pose (10 reps each)
  * Pigeon stretch for hip openers (1 min per side)
  * Thoracic spine rotations
- Cooldown or recovery tip: Sip chamomile tea, prioritize 8 hours of sleep for cellular repair.

Day 5: Upper Body Pull & Posterior Chain
- Warm-up (5-10 mins): Lat activations, band pull-aparts, light rowing.
- Main Workout:
  * Lat Pulldowns or Assisted Pull-ups: 4 sets of 8-10 reps
  * Bent-over Dumbbell / Barbell Rows: 3 sets of 10-12 reps
  * Face Pulls for rear delts: 3 sets of 15 reps
  * Bicep Dumbbell Curls: 3 sets of 12 reps
  * Hanging Knee Raises: 3 sets of 12 reps
- Cooldown or recovery tip: Upper back and bicep stretch. Eat a protein-rich post-workout snack.

Day 6: Full Body Functional Circuit
- Warm-up (5-10 mins): Full body dynamic warm-up, inchworms, arm hugs.
- Main Workout:
  * Dumbbell Thrusters (Squat to Overhead Press): 3 sets of 10 reps
  * Renegade Rows with Push-up: 3 sets of 8 reps per side
  * Bulgarian Split Squats: 3 sets of 10 reps per leg
  * Cable / Resistance Band Woodchops: 3 sets of 15 reps each side
  * Farmer's Carry: 3 sets of 40 meters
- Cooldown or recovery tip: 10 minutes static stretching targeting hips, lower back, and hamstrings.

Day 7: Rest & Wellness Recovery
- Warm-up: None required - allow nervous system to recharge.
- Main Workout:
  * Total rest or optional 15-minute gentle mindful yoga/stretching.
- Cooldown or recovery tip: Hydrate well, prep nutritious meals for the upcoming week.
"""

def generate_workout_gemini(user_input: dict) -> str:
    """
    Implements core logic to generate a personalized 7-day workout plan
    using Gemini 1.5 Pro based on user inputs (goal, intensity).
    """
    goal = user_input.get("goal", "general wellness")
    intensity = user_input.get("intensity", "medium")

    prompt = f"""
You are a professional fitness trainer.

Create a personalized, structured 7-day workout plan for someone with the goal of "{goal}", and prefers "{intensity}" intensity workouts.

Each day must include:
- A warm-up (5-10 mins)
- Main workout (targeted exercises, sets & reps)
- Cooldown or recovery tip

Format:
Day 1:
Warm-up: ...
Main Workout: ...
Cooldown: ...
(Repeat for Day 2-7)
"""
    model = _get_gemini_model()
    if model:
        try:
            response = model.generate_content(prompt)
            if response and response.text:
                return response.text
        except Exception as e:
            # If API error, fallback gracefully to structured output
            return _generate_fallback_plan(goal, intensity)

    return _generate_fallback_plan(goal, intensity)
