# Import os module for directory path operations
import os  # Standard operating system interface
# Import typing module for type annotations
from typing import List  # Type hint for list of strings
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
# Define root endpoint route redirecting to the welcome page
@app.get("/", include_in_schema=False)  # Route handler for root URL
# Function redirecting incoming root requests to static index.html
def redirect_to_index():  # Root redirection function
    # Return HTTP redirect response pointing to /static/index.html
    return RedirectResponse(url="/static/index.html")  # Redirect to welcome page
# Define POST endpoint for generating career suggestions
@app.post("/api/suggest")  # POST route for suggestions API
# Handler function receiving validated request and returning recommendations
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
# Determine static folder path preferring static directory if present
static_directory = "static" if os.path.isdir("static") else "UI"  # Static directory location
# Mount the static directory to serve files at the /static URL path
app.mount("/static", StaticFiles(directory=static_directory), name="static")  # Mount static files
