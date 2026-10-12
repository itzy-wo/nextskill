# Import the os module to read environment variables
import os  # Access system environment variables
# Import the requests library to make HTTP network calls
import requests  # Send HTTP requests
# Import load_dotenv from python-dotenv to load variables from .env
from dotenv import load_dotenv  # Load local .env file
# Load the environment variables from the .env file in the current directory
load_dotenv()  # Parse and load .env values into os.environ
# Read the GEMINI_API_KEY from environment variables
api_key = os.getenv("GEMINI_API_KEY")  # Retrieve Gemini API key string
# Check if the GEMINI_API_KEY is available
if not api_key:  # Guard against missing API key
    # Print error message if the key is missing without exposing secrets
    print("Error: GEMINI_API_KEY not found in .env file.")  # Print missing key notice
    # Exit early if the API key is not present
    raise SystemExit(1)  # Terminate execution with exit code 1
# Define the Gemini generateContent REST endpoint URL using model gemini-3.5-flash-lite
url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent"  # REST API endpoint
# Construct HTTP headers including Content-Type and x-goog-api-key with the key
headers = {"Content-Type": "application/json", "x-goog-api-key": api_key}  # Send key in x-goog-api-key header
# Build JSON payload containing the prompt text for generateContent
payload = {"contents": [{"parts": [{"text": "Say hello in one short sentence"}]}]}  # Request body with prompt
# Send POST request to the Gemini REST API endpoint
response = requests.post(url, headers=headers, json=payload)  # Perform POST request
# Check if the HTTP status code is 200 indicating success
if response.status_code == 200:  # Validate successful response
    # Parse the response body as JSON
    data = response.json()  # Decode JSON response
    # Extract candidate text reply from candidates content parts
    reply = data["candidates"][0]["content"]["parts"][0]["text"]  # Get reply text
    # Print only the extracted reply text as requested
    print(reply.strip())  # Output reply text only
# Handle non-200 responses when the request fails
else:  # Branch for HTTP errors
    # Print the status code and error message on failure without printing the key
    print(f"Status {response.status_code}: {response.text}")  # Output status code and error
