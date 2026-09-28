# ⚡ FitBuddy – AI Fitness Plan Generator using Gemini Models

FitBuddy is an intelligent, full-stack AI fitness web application built with **FastAPI**, **Google Gemini AI**, and **SQLite (SQLAlchemy ORM)**. It generates custom 7-day personalized workout routines, computes metabolic and nutrition guidelines, dynamically refines workout plans based on user feedback, and provides a coach/admin dashboard to track users.

---

## 📂 Project Structure (Frontend & Backend for GitHub)

The repository is cleanly organized into **Frontend** and **Backend** modules for effortless GitHub uploading and management:

```text
fitbuddy/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI application entry point & CORS
│   │   ├── routes.py                  # HTML template routes & REST API endpoints
│   │   ├── database.py                # SQLAlchemy ORM models (User, WorkoutPlan) & SQLite logic
│   │   ├── schemas.py                 # Pydantic data validation schemas
│   │   ├── gemini_generator.py        # Gemini 1.5 Pro 7-day workout plan generator
│   │   ├── gemini_flash_generator.py  # Gemini Flash rapid nutrition & recovery tips
│   │   ├── updated_plan.py            # Gemini 1.5 Pro feedback-based plan revision engine
│   │   └── nutrition.py               # Macro targets, BMR/TDEE & hydration calculations
│   ├── requirements.txt               # Backend dependencies
│   ├── .env.example                   # Environment configuration template
│   └── .env                           # Local environment keys (contains GOOGLE_API_KEY)
├── frontend/
│   ├── templates/
│   │   ├── index.html                 # Modern user input form with gym styling
│   │   ├── result.html                # Workout plan display, nutrition tip & feedback loop
│   │   └── all_users.html             # Admin / trainer dashboard for all users & plans
│   └── static/
│       ├── css/
│       │   └── style.css              # Custom styling, dark mode glassmorphism & responsive grid
│       └── images/
│           └── gym-bg.jpg             # High-resolution gym background visual
├── app/                               # Root alias for direct "uvicorn app.main:app" execution
├── templates/                         # Root alias for templates
├── static/                            # Root alias for static assets
├── fitbuddy.db                        # SQLite database (auto-generated)
├── requirements.txt                   # Root dependency manifest
├── run.py                             # One-command server launcher
└── README.md                          # Documentation & project manual
```

---

## 🚀 Key Features & Scenarios

- **Scenario 1: Personalized 7-Day Workout Generation**: User inputs name, user ID, age, weight, fitness goal (e.g. *weight loss*, *muscle gain*), and intensity level (*low*, *medium*, *high*). Powered by **Gemini 1.5 Pro**, it generates an organized day-by-day plan with warm-up, main exercises, sets, reps, and cooldown.
- **Scenario 2: Dynamic Feedback & Plan Updating**: Users can enter their feedback (e.g., *"add yoga on weekends"*, *"include more cardio"*, *"more rest days"*). **Gemini 1.5 Pro** updates the workout routine and persists the revised plan separately in the database.
- **Scenario 3: Targeted Nutrition & Recovery Tips**: Powered by **Gemini Flash**, users receive targeted dietary and recovery advice (protein intake, hydration, sleep) along with estimated daily calorie and macro breakdowns.
- **Scenario 4: Coach & Admin Dashboard (`/view-all-users`)**: Comprehensive admin view displaying all registered users, fitness goals, intensities, and comparing original plans against updated revisions. Includes ability to delete records.

---

## 🛠️ Prerequisites & Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/fitbuddy-ai.git
   cd fitbuddy-ai
   ```

2. **Create and activate a virtual environment (Python 3.10+):**
   - On Windows:
     ```powershell
     python -m venv fitbuddy-env
     fitbuddy-env\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     python3 -m venv fitbuddy-env
     source fitbuddy-env/bin/activate
     ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure your Google Gemini API Key:**
   Open `.env` (or copy `.env.example` to `.env`) and add your Gemini API Key:
   ```env
   GOOGLE_API_KEY=your_actual_gemini_api_key_here
   GEMINI_API_KEY=your_actual_gemini_api_key_here
   ```
   > *Note: If no API key is provided, FitBuddy seamlessly operates in demonstration fallback mode with pre-calibrated fitness routines so all features can be tested offline without crashes.*

---

## 🖥️ Running the Application Locally

Start the local server using either of the following commands:

### Option 1 (Recommended Launcher):
```bash
python run.py
```

### Option 2 (Uvicorn CLI per PDF specification):
```bash
uvicorn app.main:app --reload
```

Once running, access the application in your browser:
- 🌐 **Web Application (Homepage):** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- 👥 **Admin Dashboard:** [http://127.0.0.1:8000/view-all-users](http://127.0.0.1:8000/view-all-users)
- 📖 **Interactive Swagger API Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- 📑 **ReDoc Documentation:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 📡 REST API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Renders user input form (`index.html`) |
| `POST` | `/generate-workout` | Form submission endpoint for generating workout & nutrition plan |
| `POST` | `/submit-feedback` | Form submission endpoint for updating plan based on user feedback |
| `GET` | `/view-all-users` | Admin view of all registered users and plans (`all_users.html`) |
| `POST` | `/delete-user/{id}` | Admin endpoint to delete a user record |
| `POST` | `/generate-workout/gemini` | JSON API endpoint to generate workout using Gemini Pro |
| `GET` | `/nutrition-tip?goal={goal}` | JSON API endpoint to generate nutrition tip using Gemini Flash |
| `POST` | `/generate-plan` | JSON API endpoint accepting `UserInput` model and saving to SQLite |
| `POST` | `/update-plan/{id}` | JSON API endpoint accepting `FeedbackRequest` to revise plan |
| `GET` | `/api/users` | JSON API endpoint returning all registered users and plans |
