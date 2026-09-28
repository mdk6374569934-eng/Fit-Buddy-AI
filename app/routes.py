import os
from fastapi import APIRouter, Request, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from .schemas import UserInput, FeedbackRequest, WorkoutRequest
from .database import (
    SessionLocal,
    User,
    WorkoutPlan,
    save_user,
    save_plan,
    update_plan,
    get_original_plan,
    get_user,
    get_all_users,
    get_all_plans,
    delete_user
)
from .gemini_generator import generate_workout_gemini
from .gemini_flash_generator import generate_nutrition_tip_with_flash
from .updated_plan import update_workout_plan
from .nutrition import calculate_nutrition_guidelines

router = APIRouter()

# Locate templates directory flexibly across various execution directories
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__)) # .../app
APP_PARENT = os.path.dirname(CURRENT_DIR)                 # .../backend or workspace root
WORKSPACE_ROOT = os.path.dirname(APP_PARENT) if os.path.basename(APP_PARENT) == "backend" else APP_PARENT

candidate_template_dirs = [
    os.path.join(WORKSPACE_ROOT, "frontend", "templates"),
    os.path.join(WORKSPACE_ROOT, "templates"),
    os.path.join(APP_PARENT, "templates"),
    os.path.join(CURRENT_DIR, "templates"),
]

TEMPLATE_DIR = None
for candidate in candidate_template_dirs:
    if os.path.isdir(candidate):
        TEMPLATE_DIR = candidate
        break

if not TEMPLATE_DIR:
    TEMPLATE_DIR = candidate_template_dirs[0]

templates = Jinja2Templates(directory=TEMPLATE_DIR)


# ==========================================
# 1. Web Page Routes (HTML + Jinja2)
# ==========================================

@router.get("/", response_class=HTMLResponse)
async def home_route(request: Request):
    """Returns the user input form page (index.html)."""
    return templates.TemplateResponse(request=request, name="index.html", context={"request": request})


@router.post("/generate-workout", response_class=HTMLResponse)
async def generate_workout_form(
    request: Request,
    username: str = Form(...),
    user_id: int = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...)
):
    """
    Receives user form input, generates 7-day plan via Gemini Pro,
    generates nutrition tip via Gemini Flash, saves to SQLite DB,
    and returns result.html.
    """
    user_input = {
        "username": username,
        "user_id": user_id,
        "age": age,
        "weight": weight,
        "goal": goal,
        "intensity": intensity
    }

    # Generate workout plan using Gemini Pro
    workout_plan = generate_workout_gemini(user_input)

    # Generate nutrition tip using Gemini Flash
    nutrition_tip = generate_nutrition_tip_with_flash(goal)

    # Calculate nutritional estimates
    nutrition_stats = calculate_nutrition_guidelines(age, weight, goal, intensity)

    # Store user and original workout plan into SQLite
    save_user(
        user_id=user_id,
        name=username,
        age=age,
        weight=weight,
        goal=goal,
        intensity=intensity
    )
    save_plan(user_id=user_id, plan=workout_plan)

    return templates.TemplateResponse(request=request, name="result.html", context={
        "request": request,
        "username": username,
        "user_id": user_id,
        "age": age,
        "weight": weight,
        "goal": goal,
        "intensity": intensity,
        "workout_plan": workout_plan,
        "nutrition_tip": nutrition_tip,
        "nutrition_stats": nutrition_stats,
        "is_updated": False,
        "confirmation_message": None
    })


@router.post("/submit-feedback", response_class=HTMLResponse)
async def submit_feedback_form(
    request: Request,
    user_id: int = Form(...),
    feedback: str = Form(...)
):
    """
    Captures feedback and user_id, retrieves original plan,
    updates plan using Gemini Pro, updates SQLite DB,
    and re-renders result.html with confirmation.
    """
    original_plan = get_original_plan(user_id)
    user = get_user(user_id)

    if not original_plan or not user:
        return templates.TemplateResponse(request=request, name="result.html", context={
            "request": request,
            "username": "User",
            "user_id": user_id,
            "age": 0,
            "weight": 0.0,
            "goal": "Unknown",
            "intensity": "Unknown",
            "workout_plan": f"Error: No existing workout plan found for User ID {user_id}. Please generate a plan first.",
            "nutrition_tip": "Make sure to register and generate a plan before requesting revisions.",
            "is_updated": False,
            "error_message": f"User ID {user_id} not found in database."
        })

    # Update workout plan via Gemini Pro based on user feedback
    updated_plan_text = update_workout_plan(original_plan, feedback)
    update_plan(user_id, updated_plan_text)

    # Re-fetch nutrition tip and stats
    nutrition_tip = generate_nutrition_tip_with_flash(user.goal)
    nutrition_stats = calculate_nutrition_guidelines(user.age, user.weight, user.goal, user.intensity)

    return templates.TemplateResponse(request=request, name="result.html", context={
        "request": request,
        "username": user.name,
        "user_id": user.id,
        "age": user.age,
        "weight": user.weight,
        "goal": user.goal,
        "intensity": user.intensity,
        "workout_plan": updated_plan_text,
        "original_plan": original_plan,
        "nutrition_tip": nutrition_tip,
        "nutrition_stats": nutrition_stats,
        "is_updated": True,
        "confirmation_message": "Your plan has been updated based on your feedback!"
    })


@router.get("/view-all-users", response_class=HTMLResponse)
async def view_all_users(request: Request):
    """
    Admin View of all registered users and their workout plans.
    Rendered with Jinja2 using a {% for user in users %} loop.
    """
    db = SessionLocal()
    try:
        users = db.query(User).all()
        user_data = []
        for u in users:
            plan = db.query(WorkoutPlan).filter(WorkoutPlan.user_id == u.id).first()
            user_data.append({
                "id": u.id,
                "name": u.name,
                "age": u.age,
                "weight": u.weight,
                "goal": u.goal,
                "intensity": u.intensity,
                "original_plan": plan.original_plan if plan else "N/A",
                "updated_plan": plan.updated_plan if (plan and plan.updated_plan) else "Not updated"
            })
    finally:
        db.close()

    return templates.TemplateResponse(request=request, name="all_users.html", context={
        "request": request,
        "users": user_data
    })


@router.post("/delete-user/{user_id}")
async def admin_delete_user(user_id: int):
    """Allows admin to delete a user and their plans from database."""
    delete_user(user_id)
    return RedirectResponse(url="/view-all-users", status_code=status.HTTP_303_SEE_OTHER)


# ==========================================
# 2. JSON REST API Endpoints (as per PDF)
# ==========================================

# 1. API: Generate workout using Gemini Pro
@router.post("/generate-workout/gemini")
async def generate_gemini_workout(request: WorkoutRequest):
    try:
        result = generate_workout_gemini({
            "goal": request.goal,
            "intensity": request.intensity
        })
        return {"model": "gemini-pro", "workout_plan": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 2. API: Generate nutrition tip using Gemini Flash
@router.get("/nutrition-tip")
def get_flash_tip(goal: str):
    tip = generate_nutrition_tip_with_flash(goal)
    return {"goal": goal, "nutrition_tip": tip}


# 3. API: Save user info & generate plan
@router.post("/generate-plan")
def generate_plan(user_data: UserInput):
    try:
        save_user(
            user_id=user_data.user_id,
            name=user_data.username,
            age=user_data.age,
            weight=user_data.weight,
            goal=user_data.goal,
            intensity=user_data.intensity
        )
        plan = generate_workout_gemini({
            "goal": user_data.goal,
            "intensity": user_data.intensity
        })
        save_plan(user_data.user_id, plan)
        return {
            "message": "Workout plan generated and saved successfully!",
            "workout_plan": plan
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Something went wrong: {str(e)}")


# 4. API: Update workout plan based on user feedback
@router.post("/update-plan/{user_id}")
def update_user_plan(user_id: int, data: FeedbackRequest):
    original = get_original_plan(user_id)
    if not original:
        return {"error": "Original plan not found for this user."}
    updated = update_workout_plan(original, data.feedback)
    update_plan(user_id, updated)
    return {"updated_plan": updated}


# 5. API: Fetch all users JSON
@router.get("/api/users")
def get_users_api():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        res = []
        for u in users:
            plan = db.query(WorkoutPlan).filter(WorkoutPlan.user_id == u.id).first()
            res.append({
                "id": u.id,
                "name": u.name,
                "age": u.age,
                "weight": u.weight,
                "goal": u.goal,
                "intensity": u.intensity,
                "original_plan": plan.original_plan if plan else None,
                "updated_plan": plan.updated_plan if plan else None
            })
        return {"users": res}
    finally:
        db.close()
