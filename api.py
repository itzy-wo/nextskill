# Import os module for directory path operations
import os  # Standard operating system interface
# Import typing module for type annotations
from typing import List, Union  # Type hint for list of strings and union types
# Import FastAPI and HTTP exception handling classes
from fastapi import FastAPI, HTTPException  # FastAPI web framework classes
# Import response classes for redirection
from fastapi.responses import RedirectResponse  # HTTP redirect response class
# Import StaticFiles handler for mounting static directories
from fastapi.staticfiles import StaticFiles  # Static asset server handler
# Import Pydantic base model and Field for data validation
from pydantic import BaseModel, Field  # Request validation schema tools
# Import get_suggestions function and custom GeminiError from core
from core import get_suggestions, GeminiError  # Core logic and error classes
# Import tutor engine functions for curriculum management and query assessment
from tutor_engine import (  # Tutor engine interface
    load_skill,  # Loads skill curriculum
    get_roadmap,  # Gets stage and lesson titles
    get_lesson,  # Gets lesson fields excluding expected_query
    check_lesson,  # Checks student query for a lesson
    get_project,  # Gets project tasks excluding expected_query
    check_project_task,  # Checks student query for a project task
)

# Initialize the FastAPI web application instance
app = FastAPI(title="NEXT-SKILL API")  # FastAPI application instance


# Define Pydantic schema for the career suggestions request payload
class SuggestRequest(BaseModel):  # Request validation model
    # Current degree or study field capped at 100 characters
    field: str = Field(..., max_length=100)  # Study field with max length 100
    # Area of tech interest capped at 100 characters
    interest: str = Field(..., max_length=100)  # Tech interest with max length 100
    # Favorite activity capped at 100 characters
    enjoy: str = Field(..., max_length=100)  # Enjoyment activity with max length 100
    # List of current skill strings
    skills: List[str]  # List of acquired student skills
    # Skill comfort level capped at 100 characters
    level: str = Field(..., max_length=100)  # Skill level with max length 100
    # Career goal for the next year capped at 100 characters
    goal: str = Field(..., max_length=100)  # Next year goal with max length 100


# Define Pydantic schema for the lesson check request payload
class LessonCheckRequest(BaseModel):  # Request validation model for checking lessons
    lesson_id: Union[str, int]  # Lesson identifier string or integer
    query: str = Field(..., max_length=500)  # Student SQL query capped at 500 characters
    attempt: int = Field(..., ge=1, le=3)  # Attempt number strictly between 1 and 3


# Define Pydantic schema for the project task check request payload
class ProjectCheckRequest(BaseModel):  # Request validation model for checking project tasks
    stage_id: Union[int, str]  # Stage identifier integer or string
    task_index: Union[int, str]  # Task index or question number
    query: str = Field(..., max_length=500)  # Student SQL query capped at 500 characters
    attempt: int = Field(..., ge=1, le=3)  # Attempt number strictly between 1 and 3


# Helper function to load skill curriculum or raise 404
def _load_skill_or_404(skill: str):  # Skill loader with 404 handling
    try:  # Guard curriculum loading
        return load_skill(skill)  # Load curriculum from skills directory
    except FileNotFoundError:  # Handle missing skill JSON file
        raise HTTPException(status_code=404, detail=f"Skill '{skill}' not found")  # Return 404 error


# Helper function to find a specific stage in skill or raise 404
def _find_stage_or_404(skill_data: dict, stage_id: Union[int, str]):  # Stage lookup with 404 handling
    for stage in skill_data.get("stages", []):  # Iterate stages in curriculum
        if str(stage.get("id")) == str(stage_id):  # Compare stage id as string
            return stage  # Return matching stage dict
    raise HTTPException(status_code=404, detail=f"Stage '{stage_id}' not found")  # Return 404 error


# Define root endpoint route redirecting to the welcome page
@app.get("/", include_in_schema=False)  # Route handler for root URL
def redirect_to_index():  # Root redirection function
    # Return HTTP redirect response pointing to /static/index.html
    return RedirectResponse(url="/static/index.html")  # Redirect to welcome page


# Define POST endpoint for generating career suggestions
@app.post("/api/suggest")  # POST route for suggestions API
def suggest_careers(request: SuggestRequest):  # Suggestion generation endpoint
    # Build dictionary of answers from validated request fields
    answers = {  # Dictionary mapping validated fields
        # Study field string
        "field": request.field,  # Map field answer
        # Tech interest string
        "interest": request.interest,  # Map interest answer
        # Favorite activity string
        "enjoy": request.enjoy,  # Map enjoy answer
        # Skills list
        "skills": request.skills,  # Map skills list
        # Skill comfort level string
        "level": request.level,  # Map level answer
        # Next year goal string
        "goal": request.goal,  # Map goal answer
    }  # End of answers dictionary
    # Wrap core API call in try-except block to handle Gemini errors
    try:  # Error handling wrapper for AI generation
        # Call get_suggestions to build prompt, query Gemini, and parse results
        results = get_suggestions(answers)  # Fetch career suggestions list
        # Return successful response containing suggestions list
        return {"suggestions": results}  # Return suggestions dictionary
    # Catch custom GeminiError raised by core logic
    except GeminiError as err:  # Exception handler for Gemini failures
        # Raise HTTP 502 Bad Gateway with the error message
        raise HTTPException(status_code=502, detail=str(err))  # Return 502 error


# Define GET endpoint for retrieving curriculum roadmap
@app.get("/api/tutor/{skill}/roadmap")  # GET route for skill roadmap
def get_tutor_roadmap(skill: str):  # Roadmap endpoint handler
    skill_data = _load_skill_or_404(skill)  # Load curriculum or 404
    return get_roadmap(skill_data)  # Return roadmap stages and lesson titles


# Define GET endpoint for retrieving a single lesson
@app.get("/api/tutor/{skill}/lessons/{lesson_id}")  # GET route for lesson details
def get_tutor_lesson(skill: str, lesson_id: str):  # Lesson details endpoint handler
    skill_data = _load_skill_or_404(skill)  # Load curriculum or 404
    lesson = get_lesson(skill_data, lesson_id)  # Fetch lesson without expected_query
    if lesson is None:  # Check if lesson was found
        raise HTTPException(status_code=404, detail=f"Lesson '{lesson_id}' not found")  # Return 404 error
    return lesson  # Return lesson details


# Define POST endpoint for validating a lesson query
@app.post("/api/tutor/{skill}/check")  # POST route for checking lesson query
def check_tutor_lesson(skill: str, request: LessonCheckRequest):  # Lesson query check endpoint
    skill_data = _load_skill_or_404(skill)  # Load curriculum or 404
    lesson = get_lesson(skill_data, str(request.lesson_id))  # Verify lesson exists
    if lesson is None:  # Check if lesson was found
        raise HTTPException(status_code=404, detail=f"Lesson '{request.lesson_id}' not found")  # Return 404 error
    # Run evaluation via tutor engine
    return check_lesson(skill_data, str(request.lesson_id), request.query, request.attempt)  # Return check result


# Define GET endpoint for retrieving stage project questions
@app.get("/api/tutor/{skill}/projects/{stage_id}")  # GET route for project questions
def get_tutor_project(skill: str, stage_id: str):  # Project questions endpoint handler
    skill_data = _load_skill_or_404(skill)  # Load curriculum or 404
    stage = _find_stage_or_404(skill_data, stage_id)  # Verify stage exists or 404
    if "project" not in stage:  # Verify stage has project definition
        raise HTTPException(status_code=404, detail=f"No project found for stage '{stage_id}'")  # Return 404 error
    project = get_project(skill_data, stage.get("id"))  # Retrieve project without expected_query
    if not project:  # Ensure project was retrieved
        raise HTTPException(status_code=404, detail=f"No project found for stage '{stage_id}'")  # Return 404 error
    return project  # Return project questions data


# Define POST endpoint for validating a project task query
@app.post("/api/tutor/{skill}/project-check")  # POST route for checking project task query
def check_tutor_project(skill: str, request: ProjectCheckRequest):  # Project task check endpoint
    skill_data = _load_skill_or_404(skill)  # Load curriculum or 404
    stage = _find_stage_or_404(skill_data, request.stage_id)  # Verify stage exists or 404
    if "project" not in stage:  # Verify stage has project definition
        raise HTTPException(status_code=404, detail=f"No project found for stage '{request.stage_id}'")  # Return 404 error

    tasks = stage.get("project", {}).get("tasks", [])  # Retrieve tasks list
    task_found = False  # Track if task index/id matches
    for t in tasks:  # Check task ID matching
        if str(t.get("id", "")) == str(request.task_index):  # Match by task ID
            task_found = True  # Found matching task
            break  # Stop search
    if not task_found:  # If not matched by ID, check numeric index
        try:  # Guard integer conversion
            idx = int(request.task_index)  # Parse task index
            if 1 <= idx <= len(tasks) or (idx == 0 and len(tasks) > 0):  # Check 1-based or 0-based index range
                task_found = True  # Found matching index
        except (ValueError, TypeError):  # Handle non-integer values
            pass  # Ignore conversion failure

    if not task_found:  # Check if task was located
        raise HTTPException(status_code=404, detail=f"Task '{request.task_index}' not found")  # Return 404 error

    # Run project task evaluation via tutor engine
    return check_project_task(skill_data, stage.get("id"), request.task_index, request.query, request.attempt)


# Determine static folder path preferring static directory if present
static_directory = "static" if os.path.isdir("static") else "UI"  # Static directory location
# Mount the static directory to serve files at the /static URL path
app.mount("/static", StaticFiles(directory=static_directory), name="static")  # Mount static files
