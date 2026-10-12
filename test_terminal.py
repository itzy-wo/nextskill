# Import get_suggestions and GeminiError from core module
from core import get_suggestions, GeminiError  # Core career recommendation tools
# Define sample answers dictionary representing student background
answers = {  # Sample student answers dict
    # Current degree / field of study
    "field": "BCA",  # Bachelor of Computer Applications
    # Chosen technology area of interest
    "interest": "Data and AI",  # Focus area
    # Activity the student enjoys most
    "enjoy": "Digging into data",  # Favorite activity
    # List of skills already acquired
    "skills": ["Python", "SQL"],  # Acquired skills list
    # Self-assessed comfort level with skills
    "level": "Can build small things",  # Skill level
    # Target goal for the next year
    "goal": "An internship"  # Career goal
}  # End of answers dictionary
# Print section header for the terminal run
print("--- Fetching Career Suggestions from NEXT-SKILL ---")  # Section title
# Wrap API call in try-except block to handle GeminiError gracefully
try:  # Error handling wrapper
    # Call get_suggestions to build prompt, call Gemini in JSON mode, and parse
    suggestions = get_suggestions(answers)  # Fetch parsed suggestions list
    # Iterate through each suggestion with index starting at 1
    for i, s in enumerate(suggestions, 1):  # Loop through suggestions
        # Print numbered role header
        print(f"\n{i}. Role: {s['role']}")  # Role name
        # Print short reason why this path fits the student
        print(f"   Why: {s['why']}")  # Fit rationale
        # Print comma-separated list of skills to learn next
        print(f"   Learn Next: {', '.join(s['learn_next'])}")  # Recommended skills
    # Print completion footer
    print("\n--- Done! ---")  # End of test run
# Catch and report any GeminiError encountered
except GeminiError as err:  # Exception handler
    # Print user-friendly error message
    print(f"Error fetching suggestions: {err}")  # Report friendly error
