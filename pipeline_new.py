import csv
import os
import subprocess
from typing import Dict, Set

# Google Gemini client
import google.generativeai as genai

CSV_FILE = "manim_classes_with_description.csv"
MAX_RETRIES = 3  
MANIM_OUTPUT_DIR = "media/videos"  


genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

def load_allowed_classes(csv_file: str) -> Dict[str, set]:
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

def call_gemini(prompt: str, model: str = "gemini-1.5-flash") -> str:
    model = genai.GenerativeModel(model)
    response = model.generate_content(prompt)
    return response.text.strip()

def build_direct_script_prompt(topic: str, allowed: dict) -> str:
    return f"""
You are an expert Manim video designer.

Topic: "{topic}"

Generate a complete **valid Python Manim script** directly (no JSON, no explanation).
Rules:
- Only import and use the following classes:
  Scenes: {sorted(allowed['Scene'])}
  Mobjects: {sorted(allowed['Mobject'])}
  Animations: {sorted(allowed['Animation'])}
- Do NOT include markdown fences (like ```python).
- Do NOT invent new classes.
- Always use `self.play(Create(...))` instead of `self.add(...)` when adding mobjects.
- Never create Angle objects between parallel lines.
- If two lines might be parallel, slightly adjust them so they intersect.
- At the top of the script, include the helper function:

from manim import *
def safe_angle(line1, line2, **kwargs):
    try:
        return Angle(line1, line2, **kwargs)
    except ValueError:
        return None

- When creating an Angle, always use safe_angle(...). 
  Example:
  angle = safe_angle(line1, line2, radius=0.5, color=GREEN)
  if angle:
      self.play(Create(angle))

Output: Pure Python Manim script only.
"""

def render_manim(script_path: str):
    try:
        print("\n🎬 Rendering video with Manim...")
        subprocess.run(["manim", "-pql", script_path], check=True)
        print("\n Video rendered successfully!")
    except subprocess.CalledProcessError as e:
        print("Manim rendering failed:", e)

def main():
    topic = input("Enter your topic: ")
    allowed_classes = load_allowed_classes(CSV_FILE)

    # Direct Gemini call to generate Manim script
    for attempt in range(1, MAX_RETRIES + 1):
        print(f"\nAttempt {attempt} to generate Manim script...")
        script_prompt = build_direct_script_prompt(topic, allowed_classes)
        manim_script = call_gemini(script_prompt)

        # Clean unwanted ``` fences if they appear
        if manim_script.startswith("```"):
            manim_script = manim_script.strip("`").replace("python", "").strip()

        # Validate script looks like Manim
        if "class" in manim_script and "Scene" in manim_script:
            break
        else:
            print("Invalid script output, retrying...")

    print("\n=== Generated Manim Code ===")
    print(manim_script)

    # Save script
    script_path = "generated_script.py"
    with open(script_path, "w") as f:
        f.write(manim_script)
    print(f"\nScript saved to {script_path}")

    # Render video
    render_manim(script_path)

if __name__ == "__main__":
    main()
