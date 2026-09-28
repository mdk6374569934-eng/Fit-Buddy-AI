"""
nutrition.py - Handles nutrition-specific logic and metabolic calculations
Complements Gemini AI tips with personalized nutritional target estimates.
"""

def calculate_nutrition_guidelines(age: int, weight_kg: float, goal: str, intensity: str) -> dict:
    """
    Calculates estimated daily caloric requirements, macro breakdown, and hydration targets.
    """
    goal_lower = (goal or "").lower()
    intensity_lower = (intensity or "").lower()

    # Estimate BMR (Mifflin-St Jeor simplified for average height ~170cm)
    base_bmr = 10 * weight_kg + 6.25 * 170 - 5 * age + 5

    # Activity multiplier based on intensity
    if "high" in intensity_lower:
        activity_multiplier = 1.65
        workout_burn = 450
    elif "medium" in intensity_lower:
        activity_multiplier = 1.45
        workout_burn = 300
    else:  # low
        activity_multiplier = 1.25
        workout_burn = 180

    tdee = round(base_bmr * activity_multiplier)

    # Adjust calories for fitness goal
    if "loss" in goal_lower or "fat" in goal_lower or "cut" in goal_lower:
        target_calories = round(tdee - 450)
        protein_per_kg = 2.0  # high protein to spare muscle in deficit
        fat_pct = 0.25
    elif "gain" in goal_lower or "bulk" in goal_lower or "muscle" in goal_lower:
        target_calories = round(tdee + 350)
        protein_per_kg = 2.2
        fat_pct = 0.25
    elif "endurance" in goal_lower or "stamina" in goal_lower:
        target_calories = round(tdee + 150)
        protein_per_kg = 1.6
        fat_pct = 0.20
    else:  # wellness / general fitness
        target_calories = tdee
        protein_per_kg = 1.6
        fat_pct = 0.25

    # Macros
    protein_grams = round(weight_kg * protein_per_kg)
    protein_cals = protein_grams * 4
    fat_cals = round(target_calories * fat_pct)
    fat_grams = round(fat_cals / 9)
    remaining_cals = max(300, target_calories - protein_cals - fat_cals)
    carb_grams = round(remaining_cals / 4)

    # Hydration
    water_liters = round((weight_kg * 0.035) + (0.5 if "high" in intensity_lower else 0.25), 1)

    return {
        "calories": target_calories,
        "protein_grams": protein_grams,
        "carbs_grams": carb_grams,
        "fats_grams": fat_grams,
        "water_liters": water_liters,
        "water_glasses": round(water_liters * 4)  # ~250ml glass
    }
