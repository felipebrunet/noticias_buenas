import os
import datetime
import sys
import google.generativeai as genai
import re

# --- Configuration ---
# Get the API key from the environment variable set in GitHub Actions
API_KEY = os.getenv("GEMINI_API_KEY")
# The question to ask Gemini. We ask it to provide a title on the first line.
PROMPT = "Tell me a short, positive, and interesting news story or fact. The story should be suitable for a blog post. Start the response with a catchy title on the first line, and only the title."
# The directory where Hugo posts are stored
POSTS_DIR = "content/posts"
# --- End Configuration ---

def create_new_post():
    """
    Queries the Gemini API and creates a new Hugo post from the response.
    """
    if not API_KEY:
        print("Error: GEMINI_API_KEY environment variable not set.")
        sys.exit(1)

    # Ensure the posts directory exists before trying to write to it
    os.makedirs(POSTS_DIR, exist_ok=True)

    try:
        # Configure the Gemini client
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash-latest')

        print("Querying Gemini API...")
        response = model.generate_content(PROMPT)
        
        # The first line of the response is the title, the rest is the body
        parts = response.text.strip().split('\n', 1)
        title = parts[0].strip()
        body = parts[1].strip() if len(parts) > 1 else "No content was generated."

        # Create a slug from the title (e.g., "My Great Story" -> "my-great-story")
        slug = re.sub(r'[^\w\s-]', '', title).strip().lower()
        slug = re.sub(r'[-\s]+', '-', slug)
        
        today = datetime.date.today()
        filename = f"{today.strftime('%Y-%m-%d')}-{slug}.md"
        filepath = os.path.join(POSTS_DIR, filename)

        # Create the front matter and body for the post
        content = f"""---
title: "{title.replace('"', "'")}"
date: "{today.isoformat()}"
draft: false
type: "post"
---

{body}
"""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        
        print(f"Successfully created new post: {filepath}")

    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    create_new_post()
