# Import sys for exiting politely and configuring stream encoding
import sys
# Import tutor engine functions to manage curriculum, roadmap, lessons, and checks
from tutor_engine import (
    load_skill,
    get_roadmap,
    get_lesson,
    check_lesson,
    get_project,
    get_project_task,
    check_project_task,
)

# Ensure standard output can print Unicode characters safely on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


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
    # Fetch stages and lesson titles using get_roadmap from tutor_engine
    roadmap = get_roadmap(data)
    for stage in roadmap:
        stage_title = stage.get("title", "")
        print(f"Stage: {stage_title}")
        # Print lesson titles under each stage
        for lesson in stage.get("lessons", []):
            lesson_title = lesson.get("title", "") if isinstance(lesson, dict) else str(lesson)
            print(f"  - {lesson_title}")
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


# Function to run an individual lesson using tutor_engine
def run_lesson(skill_data_or_lesson, lesson_id=None):
    # Support both (skill_data, lesson_id) and (lesson_dict,)
    if lesson_id is None and isinstance(skill_data_or_lesson, dict) and "id" in skill_data_or_lesson:
        target_lesson = skill_data_or_lesson
        lesson_id = target_lesson.get("id")
        skill_data = load_skill("sql")
    else:
        skill_data = skill_data_or_lesson
        target_lesson = get_lesson(skill_data, lesson_id)

    # Print lesson header and intro
    print(f"--- Lesson: {target_lesson.get('title', '')} ---\n")
    print(target_lesson.get("intro", ""))
    print()
    # Print easy_words in full
    print(target_lesson.get("easy_words", ""))
    print()
    # Pause after easy_words
    wait_for_enter()

    # Print syntax (with 'Syntax:' once), syntax_note, example, and example_result
    print("Syntax:")
    print(target_lesson.get("syntax", ""))
    print()
    print(target_lesson.get("syntax_note", ""))
    print()
    print("Example:")
    print(target_lesson.get("example", ""))
    print()
    print(target_lesson.get("example_result", ""))
    print()
    # Pause before the task is shown
    wait_for_enter()

    # Print task
    print("Task:")
    print(target_lesson.get("task", ""))
    print()

    # Assessment loop with 3 attempts via check_lesson
    fail_count = 0
    while True:
        student_query = ask_student_query()
        attempt = fail_count + 1
        result = check_lesson(skill_data, lesson_id, student_query, attempt)

        # On success, print cheer and move to next lesson
        if result["passed"]:
            if result.get("message"):
                print(result["message"])
            print()
            return True

        # Increment failure count
        fail_count += 1
        if result.get("message"):
            print(result["message"])
        if result.get("hint") and not result.get("answer"):
            print(f"Hint: {result['hint']}")
        if result.get("answer"):
            print(f"Answer: {result['answer']}")
            print()
            return False
        print()


# Function to run project tasks for a stage using tutor_engine
def run_project(skill_data_or_project, stage_id=1):
    # Support both (skill_data, stage_id) and (project_dict,)
    if isinstance(skill_data_or_project, dict) and "tasks" in skill_data_or_project:
        project = skill_data_or_project
        skill_data = load_skill("sql")
    else:
        skill_data = skill_data_or_project
        project = get_project(skill_data, stage_id)

    if not project:
        return

    # Print project title and intro
    print(f"=== {project.get('title', 'Project')} ===\n")
    if project.get("intro"):
        print(f"{project.get('intro')}\n")

    # Run each task in the project
    tasks = project.get("tasks", [])
    for idx, task in enumerate(tasks, 1):
        print(f"Question {idx}: {task.get('question', '')}\n")
        fail_count = 0
        while True:
            student_query = ask_student_query()
            attempt = fail_count + 1
            result = check_project_task(skill_data, stage_id, idx, student_query, attempt)

            if result["passed"]:
                if result.get("message"):
                    print(result["message"])
                print()
                break

            fail_count += 1
            if result.get("message"):
                print(result["message"])
            if result.get("hint") and not result.get("answer"):
                print(f"Hint: {result['hint']}")
            if result.get("answer"):
                print(f"Answer: {result['answer']}")
                print()
                break
            print()

    # Print project cheer after all tasks are completed
    if project.get("cheer"):
        print(project.get("cheer"))
        print()


# Main tutor loop
def main():
    # Load skill curriculum through tutor_engine
    data = load_skill("sql")
    # 1. Print welcome and roadmap
    print_welcome_and_roadmap(data)
    # Process each stage
    for stage in data.get("stages", []):
        stage_id = stage.get("id", 1)
        # 2-3. Process lessons
        for lesson in stage.get("lessons", []):
            run_lesson(data, lesson.get("id"))
        # 4. Process project tasks and cheer
        if "project" in stage:
            run_project(data, stage_id)
    # Final completion message
    print("You have completed all stages! Great work!")


# Script entry point
if __name__ == "__main__":
    main()
