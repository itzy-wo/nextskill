# Import json for parsing skill configuration files
import json
# Import Path for resolving skill file paths
from pathlib import Path
# Import check_answer from sql_checker to validate queries
from sql_checker import check_answer


# String subclass for lesson titles so they can behave as both strings and dicts
class LessonTitle(str):
    # Initialize with lesson title and optional lesson id
    def __new__(cls, title, lesson_id=None):
        obj = super().__new__(cls, str(title))
        obj.id = str(lesson_id) if lesson_id is not None else ""
        return obj

    # Support dict-like get method for backwards compatibility
    def get(self, key, default=None):
        if key == "title":
            return str(self)
        if key == "id":
            return self.id
        return default

    # Support dict-like key access
    def __getitem__(self, key):
        if key == "title":
            return str(self)
        if key == "id":
            return self.id
        return super().__getitem__(key)


# Dict subclass for stage information in roadmap
class StageInfo(dict):
    # Initialize dictionary with id, title, stage name, and lesson titles
    def __init__(self, stage_id, title, lessons):
        super().__init__({
            "id": stage_id,
            "title": title,
            "stage": title,
            "lessons": lessons
        })


# Function to load a skill curriculum JSON file by name
def load_skill(name):
    p = Path(name)
    if not p.suffix:
        p = p.with_suffix(".json")
    script_dir = Path(__file__).resolve().parent
    candidates = [
        script_dir / "skills" / p.name,
        script_dir / p,
        Path("skills") / p.name,
        p
    ]
    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            with open(candidate, "r", encoding="utf-8") as f:
                return json.load(f)
    raise FileNotFoundError(f"Skill file not found for: {name}")


# Function to extract stage and lesson titles for the roadmap
def get_roadmap(skill):
    roadmap = []
    # Loop over stages in the skill dictionary
    for stage in skill.get("stages", []):
        lessons = [
            LessonTitle(lesson.get("title", ""), lesson.get("id"))
            for lesson in stage.get("lessons", [])
        ]
        roadmap.append(StageInfo(stage.get("id"), stage.get("title", ""), lessons))
    return roadmap


# Function to retrieve lesson fields excluding expected_query
def get_lesson(skill, lesson_id):
    # Find matching lesson across all stages
    for stage in skill.get("stages", []):
        for lesson in stage.get("lessons", []):
            if str(lesson.get("id")) == str(lesson_id):
                # Return all fields except expected_query
                return {k: v for k, v in lesson.items() if k != "expected_query"}
    return None


# Helper function to find a raw lesson (including expected_query)
def _find_raw_lesson(skill, lesson_id):
    for stage in skill.get("stages", []):
        for lesson in stage.get("lessons", []):
            if str(lesson.get("id")) == str(lesson_id):
                return lesson
    return None


# Function to check student's lesson query and return feedback dict
def check_lesson(skill, lesson_id, student_query, attempt=1):
    # Find the target lesson definition
    lesson = _find_raw_lesson(skill, lesson_id)
    if not lesson:
        return {
            "passed": False,
            "message": f"Lesson '{lesson_id}' not found.",
            "hint": None,
            "answer": None
        }

    # Extract reference query and ordered requirement
    expected_query = lesson.get("expected_query", "")
    ordered = lesson.get("ordered", False)

    try:
        attempt_num = int(attempt)
    except (TypeError, ValueError):
        attempt_num = 1

    # Validate query using sql_checker
    passed, msg = check_answer(student_query, expected_query, ordered)

    # Determine hint (provided starting from 2nd failed attempt)
    hint = lesson.get("hint") if not passed and attempt_num >= 2 else None
    # Determine answer (provided only on 3rd or later failed attempt)
    answer = expected_query if not passed and attempt_num >= 3 else None

    # Check whether failure was due to SQL error or wrong results
    is_sql_error = (
        msg.startswith("SQL error:")
        or msg.startswith("Only a single SELECT")
        or msg.startswith("Query cannot be empty")
    )

    # Construct the feedback message
    if passed:
        message = lesson.get("cheer", "Great job!")
    else:
        if is_sql_error:
            if attempt_num == 1:
                message = f"Oops, the database hit an error: {msg}\nDouble-check your table or column names, then try again!"
            elif attempt_num == 2:
                message = f"Oops, the database hit an error: {msg}"
            else:
                message = ""
        else:
            if attempt_num == 1:
                message = lesson.get("retry", "Ooh, so close! Try once more?")
            else:
                message = ""

    return {
        "passed": passed,
        "message": message,
        "hint": hint,
        "answer": answer
    }


# Helper function to locate a stage's project and specific task
def _find_project_and_task(skill, stage_id, task_id):
    target_stage = None
    for stage in skill.get("stages", []):
        if stage.get("id") == stage_id or str(stage.get("id")) == str(stage_id):
            target_stage = stage
            break

    # Fallback to first stage if matching stage not found
    if not target_stage and skill.get("stages"):
        target_stage = skill["stages"][0]

    if not target_stage:
        return None, None

    project = target_stage.get("project", {})
    tasks = project.get("tasks", [])
    if not tasks:
        return project, None

    # Match by task id if present
    for t in tasks:
        if str(t.get("id", "")) == str(task_id):
            return project, t

    # Match by numeric index (1-based Question 1..N, or 0-based Question 0)
    try:
        idx = int(task_id)
        if 1 <= idx <= len(tasks):
            return project, tasks[idx - 1]
        elif idx == 0 and len(tasks) > 0:
            return project, tasks[0]
    except (ValueError, TypeError):
        pass

    return project, None


# Function to retrieve stage project details excluding expected_query
def get_project(skill, stage_id=1):
    target_stage = None
    for stage in skill.get("stages", []):
        if stage.get("id") == stage_id or str(stage.get("id")) == str(stage_id):
            target_stage = stage
            break
    if not target_stage:
        for stage in skill.get("stages", []):
            if "project" in stage:
                target_stage = stage
                break
    if not target_stage or "project" not in target_stage:
        return None

    proj = target_stage["project"]
    # Return project copy with expected_query removed from all tasks
    proj_copy = {k: v for k, v in proj.items() if k != "tasks"}
    proj_copy["tasks"] = [
        {k: v for k, v in t.items() if k != "expected_query"}
        for t in proj.get("tasks", [])
    ]
    return proj_copy


# Function to retrieve a single project task excluding expected_query
def get_project_task(skill, arg1, arg2=None):
    if arg2 is None:
        stage_id = 1
        task_id = arg1
    else:
        stage_id = arg1
        task_id = arg2

    project, task = _find_project_and_task(skill, stage_id, task_id)
    if not task:
        return None
    # Return task fields except expected_query
    return {k: v for k, v in task.items() if k != "expected_query"}


# Function to check student query on a project task
def check_project_task(skill, *args, **kwargs):
    stage_id = kwargs.get("stage_id", 1)
    attempt = kwargs.get("attempt", 1)
    task_id = kwargs.get("task_id", None)
    student_query = kwargs.get("student_query", None)

    if len(args) == 4:
        stage_id, task_id, student_query, attempt = args
    elif len(args) == 3:
        if isinstance(args[2], int) or (isinstance(args[2], str) and args[2].isdigit()):
            task_id, student_query, attempt = args
            stage_id = 1
        else:
            stage_id, task_id, student_query = args
            attempt = 1
    elif len(args) == 2:
        task_id, student_query = args
    elif len(args) == 1:
        task_id = args[0]

    try:
        attempt_num = int(attempt)
    except (TypeError, ValueError):
        attempt_num = 1

    project, task = _find_project_and_task(skill, stage_id, task_id)
    if not task:
        return {
            "passed": False,
            "message": "Project task not found.",
            "hint": None,
            "answer": None
        }

    expected_query = task.get("expected_query", "")
    ordered = task.get("ordered", False)

    # Validate query using sql_checker
    passed, msg = check_answer(student_query, expected_query, ordered)

    # Determine hint (provided starting from 2nd failed attempt)
    hint = task.get("hint") if not passed and attempt_num >= 2 else None
    # Determine answer (provided only on 3rd or later failed attempt)
    answer = expected_query if not passed and attempt_num >= 3 else None

    # Check if failure was due to SQL error
    is_sql_error = (
        msg.startswith("SQL error:")
        or msg.startswith("Only a single SELECT")
        or msg.startswith("Query cannot be empty")
    )

    # Sugar's project retry message
    sugar_retry = task.get("retry", "Ooh, not quite! Take a breath and give it another whirl. 🍬")

    if passed:
        message = task.get("cheer", "Correct!")
    else:
        if is_sql_error:
            if attempt_num == 1:
                message = f"Oops, the database hit an error: {msg}\nDouble-check your table or column names, then try again!"
            elif attempt_num == 2:
                message = f"Oops, the database hit an error: {msg}"
            else:
                message = ""
        else:
            if attempt_num == 1:
                message = sugar_retry
            else:
                message = ""

    return {
        "passed": passed,
        "message": message,
        "hint": hint,
        "answer": answer
    }
