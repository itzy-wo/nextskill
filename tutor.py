# Import json to load the curriculum file
import json
# Import sys for exiting politely and configuring stream encoding
import sys
# Import Path for reliable file path resolution
from pathlib import Path
# Import check_answer from sql_checker to validate student queries
from sql_checker import check_answer

# Ensure standard output can print Unicode characters safely on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


# Function to load curriculum data from skills/sql.json
def load_curriculum():
    # Resolve the path to skills/sql.json relative to this script
    script_dir = Path(__file__).resolve().parent
    json_path = script_dir / "skills" / "sql.json"
    # Fallback to local relative path if needed
    if not json_path.exists():
        json_path = Path("skills/sql.json")
    # Open and parse the JSON file
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


# Function to display tutor welcome and full curriculum roadmap
def print_welcome_and_roadmap(data):
    # Get tutor name and skill name
    tutor_name = data.get("tutor", "Sugar")
    skill_name = data.get("skill", "SQL")
    # Print welcome greeting from tutor
    print(f"Hello! I am {tutor_name}, your {skill_name} tutor.")
    print("Welcome to your interactive SQL journey!\n")
    # Print roadmap header
    print("Roadmap:")
    # Loop over all stages and print titles
    for stage in data.get("stages", []):
        stage_title = stage.get("title", "")
        print(f"Stage: {stage_title}")
        # Print lesson titles under each stage
        for lesson in stage.get("lessons", []):
            print(f"  - {lesson.get('title', '')}")
    print()


# Function to pause and wait for the student to press Enter
def wait_for_enter():
    # Safely handle keyboard interrupt or EOF during pause
    try:
        user_input = input("Press Enter to continue... ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nGoodbye! Happy learning!")
        sys.exit(0)
    # Allow the student to quit at pause prompts
    if user_input.lower() == "quit":
        print("\nGoodbye! Happy learning!")
        sys.exit(0)
    print()


# Function to ask the student for a single-line SQL query
def ask_student_query():
    # Safely handle keyboard interrupt or EOF
    try:
        user_input = input("Type your SQL query (or 'quit' to exit): ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nGoodbye! Happy learning!")
        sys.exit(0)
    # Check if user typed quit
    if user_input.lower() == "quit":
        print("\nGoodbye! Happy learning!")
        sys.exit(0)
    return user_input


# Function to assess query with 3 attempts (retry on 1st, hint on 2nd, answer on 3rd)
def run_query_assessment(expected_query, ordered, cheer, retry_msg, hint):
    # Track failed attempts
    fail_count = 0
    # Keep asking until passed or 3 fails reached
    while True:
        # Prompt student for query
        student_query = ask_student_query()
        # Evaluate query using sql_checker
        passed, msg = check_answer(student_query, expected_query, ordered)
        # If passed, print cheer and advance
        if passed:
            if cheer:
                print(cheer)
            print()
            return True
        # Increment failure count
        fail_count += 1
        # Check if the query failed due to a SQL error (e.g. invalid table or column)
        is_sql_error = msg.startswith("SQL error:") or msg.startswith("Only a single SELECT") or msg.startswith("Query cannot be empty")
        # Handle 1st failure
        if fail_count == 1:
            # If SQL error, show friendly message with the actual error text
            if is_sql_error:
                print(f"Oops, the database hit an error: {msg}")
                print("Double-check your table or column names, then try again!\n")
            # If query ran but produced wrong result, show lesson retry message
            else:
                print(retry_msg)
                print()
        # Handle 2nd failure: show hint
        elif fail_count == 2:
            if is_sql_error:
                print(f"Oops, the database hit an error: {msg}")
            print(f"Hint: {hint}")
            print()
        # Handle 3rd failure: print answer and move on
        else:
            print(f"Answer: {expected_query}")
            print()
            return False


# Function to run an individual lesson
def run_lesson(lesson):
    # Print lesson header and intro
    print(f"--- Lesson: {lesson.get('title', '')} ---\n")
    print(lesson.get("intro", ""))
    print()
    # Print easy_words in full
    print(lesson.get("easy_words", ""))
    print()
    # Pause after easy_words
    wait_for_enter()

    # Print syntax (with 'Syntax:' once), syntax_note, example, and example_result
    print("Syntax:")
    print(lesson.get("syntax", ""))
    print()
    print(lesson.get("syntax_note", ""))
    print()
    print("Example:")
    print(lesson.get("example", ""))
    print()
    print(lesson.get("example_result", ""))
    print()
    # Pause before the task is shown
    wait_for_enter()

    # Print task
    print("Task:")
    print(lesson.get("task", ""))
    print()

    # Run the query assessment loop
    expected_query = lesson.get("expected_query", "")
    ordered = lesson.get("ordered", False)
    cheer = lesson.get("cheer", "Great job!")
    retry_msg = lesson.get("retry", "Ooh, so close! Try once more?")
    hint = lesson.get("hint", "")
    run_query_assessment(expected_query, ordered, cheer, retry_msg, hint)


# Function to run project tasks for a stage
def run_project(project):
    # Print project title and intro
    print(f"=== {project.get('title', 'Project')} ===\n")
    if project.get("intro"):
        print(f"{project.get('intro')}\n")
    # Sugar's sweet retry message for project tasks
    sugar_retry = "Ooh, not quite! Take a breath and give it another whirl. 🍬"
    # Run each task in the project
    tasks = project.get("tasks", [])
    for idx, task in enumerate(tasks, 1):
        print(f"Question {idx}: {task.get('question', '')}\n")
        expected_query = task.get("expected_query", "")
        ordered = task.get("ordered", False)
        cheer = task.get("cheer", "Correct!")
        hint = task.get("hint", "")
        run_query_assessment(expected_query, ordered, cheer, sugar_retry, hint)
    # Print project cheer after all tasks are completed
    if project.get("cheer"):
        print(project.get("cheer"))
        print()


# Main tutor loop
def main():
    # Load curriculum
    data = load_curriculum()
    # 1. Print welcome and roadmap
    print_welcome_and_roadmap(data)
    # Process each stage
    for stage in data.get("stages", []):
        # 2-3. Process lessons
        for lesson in stage.get("lessons", []):
            run_lesson(lesson)
        # 4. Process project tasks and cheer
        if "project" in stage:
            run_project(stage["project"])
    # Final completion message
    print("You have completed all stages! Great work!")


# Script entry point
if __name__ == "__main__":
    main()
