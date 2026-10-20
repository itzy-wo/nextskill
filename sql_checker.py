# Import the built-in sqlite3 module for SQLite database operations
import sqlite3  # Built-in SQLite database library
# Helper function to create and populate an in-memory SQLite database
def get_db_connection():  # Database initialization function
    # Create a fresh in-memory SQLite database connection
    conn = sqlite3.connect(":memory:")  # In-memory database connection
    # Create a cursor object to execute SQL statements
    cursor = conn.cursor()  # Database cursor
    # Define SQL command string to create the students table schema
    create_table_sql = (  # SQL string definition
        "CREATE TABLE students ("  # Create students table
        "id INTEGER PRIMARY KEY, "  # Unique student ID
        "name TEXT NOT NULL, "  # Student name
        "city TEXT NOT NULL, "  # Student city
        "course TEXT NOT NULL, "  # Enrolled course
        "marks INTEGER NOT NULL, "  # Student marks
        "joined_year INTEGER NOT NULL"  # Enrollment year
        ");"  # End of table definition
    )  # End of create table string
    # Execute the table creation statement
    cursor.execute(create_table_sql)  # Create table in memory
    # Prepare list of student records to seed the database
    student_records = [  # Student seed data
        (1, "Aarav", "Pune", "BCA", 78, 2023),  # Record for Aarav
        (2, "Diya", "Delhi", "BSc IT", 91, 2022),  # Record for Diya
        (3, "Kabir", "Pune", "BCA", 64, 2024),  # Record for Kabir
        (4, "Meera", "Mumbai", "B.Tech", 85, 2022),  # Record for Meera
        (5, "Rohan", "Delhi", "BCA", 72, 2023),  # Record for Rohan
        (6, "Sana", "Jaipur", "BSc IT", 88, 2024),  # Record for Sana
        (7, "Vihaan", "Mumbai", "B.Tech", 59, 2023),  # Record for Vihaan
        (8, "Zoya", "Pune", "BSc IT", 95, 2022),  # Record for Zoya
    ]  # End of seed records
    # Insert all student records into the students table
    cursor.executemany("INSERT INTO students VALUES (?, ?, ?, ?, ?, ?);", student_records)  # Insert records
    # Commit changes to persist the table data
    conn.commit()  # Commit transaction
    # Return the populated connection object
    return conn  # Return connection
# Function to validate and compare student queries against expected queries
def check_answer(student_query, expected_query, ordered=False):  # Query checker function
    # Verify student_query is a non-empty string instance
    if not student_query or not isinstance(student_query, str):  # Check query validity
        # Return error if query is missing or invalid type
        return (False, "Query cannot be empty.")  # Return invalid query error
    # Trim leading and trailing whitespace from the query
    stripped_query = student_query.strip()  # Strip whitespace
    # Remove single trailing semicolon if present
    clean_query = stripped_query[:-1].strip() if stripped_query.endswith(";") else stripped_query  # Strip trailing semicolon
    # Check if multiple queries exist by inspecting remaining semicolons
    if ";" in clean_query:  # Check for multiple statements
        # Reject multiple statement queries for security and correctness
        return (False, "Only a single SELECT statement is allowed.")  # Reject multi-statement
    # Split query into words to examine the leading command keyword
    words = clean_query.split()  # Split into tokens
    # Verify the query contains at least one word token
    if not words:  # Check token count
        # Return error if query contains no words
        return (False, "Query cannot be empty.")  # Return empty query error
    # Verify the first keyword is strictly SELECT
    if words[0].upper() != "SELECT":  # Check for SELECT statement
        # Reject non-SELECT queries such as INSERT, UPDATE, or DELETE
        return (False, "Only a single SELECT statement is allowed.")  # Reject non-SELECT
    # Obtain a fresh in-memory database connection
    conn = get_db_connection()  # Get database connection
    # Open try block to run SQL queries safely
    try:  # Guard SQL execution
        # Create a database cursor
        cursor = conn.cursor()  # Database cursor
        # Execute the student's query
        cursor.execute(student_query)  # Run student query
        # Fetch all rows returned by student query
        student_rows = cursor.fetchall()  # Get student rows
        # Execute the reference expected query
        cursor.execute(expected_query)  # Run expected query
        # Fetch all rows returned by expected query
        expected_rows = cursor.fetchall()  # Get expected rows
        # Check if row ordering must strictly match
        if ordered:  # Ordered check branch
            # Compare rows in exact returned sequence
            passed = (student_rows == expected_rows)  # Direct sequence comparison
        # Compare rows ignoring row order
        else:  # Unordered check branch
            # Wrap sorting in try block to handle tuple values
            try:  # Sort comparison block
                # Compare sorted row lists
                passed = (sorted(student_rows) == sorted(expected_rows))  # Sorted row comparison
            # Handle potential type error during sorting
            except TypeError:  # Catch sorting type error
                # Compare rows sorted by string representation
                passed = (sorted(student_rows, key=str) == sorted(expected_rows, key=str))  # String sort comparison
        # Check if the query results matched the expected rows
        if passed:  # Result match check
            # Return success tuple with confirmation message
            return (True, "Correct! Your query produced the expected result.")  # Success tuple
        # Handle case where results did not match
        else:  # Result mismatch
            # Return failure tuple with explanatory message
            return (False, "Query result does not match the expected output.")  # Mismatch tuple
    # Catch SQLite execution and syntax errors gracefully
    except sqlite3.Error as err:  # SQLite exception handler
        # Return failure tuple with friendly error description without traceback
        return (False, f"SQL error: {err}")  # Friendly error message
    # Ensure database connection is closed after testing
    finally:  # Cleanup block
        # Close the database connection
        conn.close()  # Close connection
# Main execution block to test sample queries
if __name__ == "__main__":  # Main script entry point
    # Define expected query for filtering students with marks over 80
    expected_q = "SELECT name, marks FROM students WHERE marks > 80;"  # Expected query
    # Define correct student query matching expected output
    correct_q = "SELECT name, marks FROM students WHERE marks > 80;"  # Correct query
    # Define wrong student query returning different rows
    wrong_q = "SELECT name, marks FROM students WHERE marks > 90;"  # Wrong query
    # Define unauthorized DELETE query to test rejection
    delete_q = "DELETE FROM students WHERE id = 1;"  # Forbidden DELETE query
    # Test checking the correct query
    res_correct = check_answer(correct_q, expected_q)  # Run correct test
    # Test checking the wrong query
    res_wrong = check_answer(wrong_q, expected_q)  # Run wrong test
    # Test checking the DELETE query
    res_delete = check_answer(delete_q, expected_q)  # Run delete test
    # Print header for test outputs
    print("--- SQL Checker Test Results ---")  # Output header
    # Print result of the correct query test
    print(f"Correct query test : {res_correct}")  # Print correct result
    # Print result of the wrong query test
    print(f"Wrong query test   : {res_wrong}")  # Print wrong result
    # Print result of the DELETE query test
    print(f"DELETE query test  : {res_delete}")  # Print delete result
