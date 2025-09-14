import os
import datetime
import sys
import google.generativeai as genai
import unicodedata
import re

# --- Configuration ---
# Get the API key from the environment variable set in GitHub Actions
API_KEY = os.getenv("GEMINI_API_KEY")
# The question to ask Gemini. We ask it to provide a title on the first line.
PROMPT = "Dime una noticia relevante de entre 2015 y hoy del mundo. Tu texto debe tener en la primera línea un título de máximo 4 palabras, a partir de la segunda línea, el contenido, indicando la URL de la o las fuentes. En la última línea, debes indicar los tags de la noticia, pueden ser 1 o 2, como prefieras"
# PROMPT = "Dime una noticia relevante de entre 2015 y hoy del mundo. Tu texto debe tener en la primera línea un título de máximo 4 palabras y a partir de la segunda línea, el contenido, indicando la URL de la o las fuentes."
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
        model = genai.GenerativeModel('gemini-2.5-flash')

        print("Querying Gemini API...")
        response = model.generate_content(PROMPT)
        
        # The response is split into lines.
        # First line: Title
        # Middle lines: Body
        # Last line: Tags
        lines = response.text.strip().split('\n')
        
        if len(lines) < 2: # Must have at least a title and a tags line
            print("Error: The response from Gemini did not have the expected format (title, ..., tags).")
            print(f"Response received:\n{response.text}")
            sys.exit(1)

        title = lines[0].strip()
        
        # The last line contains the tags, which may be prefixed with "Tags: "
        tags_line = lines[-1].strip()
        if tags_line.lower().startswith("tags:"):
            tags_string = tags_line[len("tags:"):].strip()
        else:
            tags_string = tags_line
        
        # The body is everything between the title and the tags line
        body_lines = lines[1:-1]
        body = "\n".join(body_lines).strip() if body_lines else "No content was generated."

        # Create a slug from the title (e.g., "My Great Story" -> "my-great-story")
        # Transliterate characters to their basic ASCII representation (e.g., "acción" -> "accion")
        normalized_title = unicodedata.normalize('NFD', title)
        ascii_title = normalized_title.encode('ascii', 'ignore').decode('utf-8')
        
        slug = re.sub(r'[^\w\s-]', '', ascii_title).strip().lower() # Remove remaining non-alphanumeric characters
        slug = re.sub(r'[-\s]+', '-', slug) # Replace spaces and hyphens with a single hyphen
        
        today = datetime.date.today()
        filename = f"{today.strftime('%Y-%m-%d')}-{slug}.md"
        filepath = os.path.join(POSTS_DIR, filename)

        # Create a YAML-formatted list of tags for the front matter
        tags_list = [tag.strip() for tag in tags_string.split(",") if tag.strip()]
        # Format each tag as a double-quoted string for the YAML list.
        quoted_tags = [f'"{tag}"' for tag in tags_list]
        tags_yaml = f"[{', '.join(quoted_tags)}]"

        # Create the front matter and body for the post
        content = f"""---
title: "{title.replace('"', "'")}"
date: "{today.isoformat()}"
draft: false
type: "post"
tags: {tags_yaml}
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
