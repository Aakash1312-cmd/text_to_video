import csv
import json
import os
import re
import subprocess
from typing import Dict, Set

# Google Gemini client
import google.generativeai as genai

# =====================================
# CONFIG
# =====================================
CSV_FILE = "manim_classes_with_description.csv"
MAX_RETRIES = 3  # retry Gemini calls if JSON is invalid
MANIM_OUTPUT_DIR = "media/videos"  # default Manim output

# Make sure to set your API key before running:
# export GEMINI_API_KEY="your_api_key_here"
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# =====================================
# LOAD ALLOWED CLASSES
# =====================================
def load_allowed_classes(csv_file: str) -> Dict[str, Set[str]]:
    allowed = {"Scene": set(), "Mobject": set(), "Animation": set()}
    current_type = None
    with open(csv_file, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or not row[0].strip():
                continue
            first = row[0].strip().lower()
            if first == "mobjects":
                current_type = "Mobject"
                continue
            elif first == "animations":
                current_type = "Animation"
                continue
            elif first == "scenes":
                current_type = "Scene"
                continue
            if "class name" in first:
                continue
            if current_type:
                allowed[current_type].add(row[0].strip())
    return allowed

# =====================================
# GEMINI HELPERS
# =====================================
def call_gemini(prompt: str, model: str = "gemini-1.5-flash") -> str:
    model = genai.GenerativeModel(model)
    response = model.generate_content(prompt)
    return response.text

# =====================================
# JSON CLEANING & FIXING
# =====================================
def fix_gemini_json(text: str) -> str:
    fenced = re.search(r"```json(.*?)```", text, re.DOTALL)
    if fenced:
        text = fenced.group(1).strip()
    text = re.sub(r"\((\d+),\s*(\d+)\)", r"[\1, \2]", text)  # tuples → lists
    text = re.sub(r",(\s*[\]}])", r"\1", text)  # remove trailing commas
    text = re.sub(r"[\x00-\x1f]", "", text)  # control chars
    # balance braces/brackets
    open_braces, close_braces = text.count("{"), text.count("}")
    if open_braces > close_braces:
        text += "}" * (open_braces - close_braces)
    open_brackets, close_brackets = text.count("["), text.count("]")
    if open_brackets > close_brackets:
        text += "]" * (open_brackets - close_brackets)
    return text

# =====================================
# STORYBOARD VALIDATION
# =====================================
def validate_storyboard(storyboard: dict) -> dict:
    for scene in storyboard.get("scenes", []):
        if "mobjects" not in scene or not isinstance(scene["mobjects"], list):
            scene["mobjects"] = []
        if "animations" not in scene or not isinstance(scene["animations"], list):
            scene["animations"] = []
    return storyboard

# =====================================
# PROMPT TEMPLATES
# =====================================
def build_storyboard_prompt(topic: str, allowed: dict) -> str:
    return f"""
You are an expert video designer using Manim.

Topic: "{topic}"

Your job is to design a storyboard for an educational video.
RULES:
- You may ONLY use the following classes:

Scenes:
{sorted(allowed['Scene'])}

Mobjects:
{sorted(allowed['Mobject'])}

Animations:
{sorted(allowed['Animation'])}

Output must be valid JSON:
- Use [] for arrays, {{}} for objects
- No Python tuples
- No trailing commas
- Close all braces properly

Output format: JSON with this schema:
{{
  "title": "...",
  "scenes": [
    {{
      "scene_class": "Scene",
      "narration": "text",
      "mobjects": [{{"type": "Square", "kwargs": {{"side_length": 2}}}}],
      "animations": [{{"type": "FadeIn", "target": "Square"}}]
    }}
  ]
}}
    """

def build_script_prompt(storyboard_json: str, allowed: dict) -> str:
    return f"""
Convert the following storyboard JSON into a valid Manim script.

Storyboard:
{storyboard_json}

RULES:
- Only import and use the classes listed in this allowed set:
Scenes: {sorted(allowed['Scene'])}
Mobjects: {sorted(allowed['Mobject'])}
Animations: {sorted(allowed['Animation'])}
- Do not invent new classes or animations.
- Ensure Python code is valid.

Output only Python code, no explanation.
    """

# =====================================
# AUTOMATIC MANIM RENDERING
# =====================================
def render_manim(script_path: str):
    """
    Runs Manim to render the generated script.
    Output video will be in the default media folder.
    """
    try:
        print("\n🎬 Rendering video with Manim...")
        subprocess.run(["manim", "-pql", script_path], check=True)
        print("\n✅ Video rendered successfully!")
    except subprocess.CalledProcessError as e:
        print("❌ Manim rendering failed:", e)

# =====================================
# MAIN PIPELINE
# =====================================
def main():
    topic = input("Enter your topic: ")
    allowed_classes = load_allowed_classes(CSV_FILE)

    # Generate storyboard with retry
    for attempt in range(1, MAX_RETRIES + 1):
        print(f"\nAttempt {attempt} to generate storyboard...")
        storyboard_prompt = build_storyboard_prompt(topic, allowed_classes)
        raw_storyboard = call_gemini(storyboard_prompt)
        cleaned = fix_gemini_json(raw_storyboard)

        try:
            storyboard = json.loads(cleaned)
            storyboard = validate_storyboard(storyboard)
            break
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON on attempt {attempt}: {e}")
            if attempt == MAX_RETRIES:
                print("❌ Failed to generate valid storyboard after maximum retries.")
                print("Cleaned text:\n", cleaned)
                return

    print("\n✅ Storyboard JSON successfully parsed and validated")
    print(json.dumps(storyboard, indent=2))

    # Generate Manim script
    script_prompt = build_script_prompt(json.dumps(storyboard, indent=2), allowed_classes)
    manim_script = call_gemini(script_prompt)

    print("\n=== Generated Manim Code ===")
    print(manim_script)

    # Save script
    script_path = "generated_script.py"
    with open(script_path, "w") as f:
        f.write(manim_script)
    print(f"\n✅ Script saved to {script_path}")

    # Render video
    render_manim(script_path)

if __name__ == "__main__":
    main()
