import csv
import json
import os
import re
from typing import Dict, Set
import subprocess
from manim import *

# Google Gemini client
import google.generativeai as genai

# =====================================
# CONFIG
# =====================================
CSV_FILE = "manim_classes_with_description.csv"
MAX_ROW_OBJECTS = 5  # default max objects per row
ROW_WIDTH_LIMIT = 12  # approximate width in scene units

# Set your Gemini API key:
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

def extract_json(text: str) -> str:
    fenced = re.search(r"```json(.*?)```", text, re.DOTALL)
    if fenced:
        return fenced.group(1).strip()
    brace = re.search(r"(\{.*\})", text, re.DOTALL)
    if brace:
        return brace.group(1).strip()
    return text.strip()

def make_json_safe(text: str) -> str:
    """Convert Gemini's Python-like JSON into valid JSON."""
    # Replace Python booleans and None
    text = text.replace("True", "true").replace("False", "false").replace("None", "null")

    # Replace single quotes with double quotes (carefully)
    text = re.sub(r"'", '"', text)

    # Replace lambda expressions with placeholder strings
    text = re.sub(r'"function":\s*"lambda.*?"', '"function": "x_plus_one"', text)

    return text

# =====================================
# PROMPT TEMPLATES
# =====================================
def build_storyboard_prompt(topic: str, allowed: Dict[str, Set[str]]) -> str:
    return f"""
You are an expert video designer using Manim.

Topic: "{topic}"

RULES:
- You may ONLY use the following classes:

Scenes:
{sorted(allowed['Scene'])}

Mobjects:
{sorted(allowed['Mobject'])}

Animations:
{sorted(allowed['Animation'])}

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

# =====================================
# SCRIPT GENERATION HELPERS
# =====================================
def sanitize_mobject_kwargs(kwargs: dict) -> dict:
    """Remove unsupported kwargs for Manim v0.19."""
    allowed_keys = {
        "radius", "side_length", "height", "fill_color", "fill_opacity",
        "stroke_color", "stroke_width", "font_size", "text", "x_range", "y_range",
        "axis_config", "color", "start", "end", "point", "matrix"
    }
    return {k: v for k, v in kwargs.items() if k in allowed_keys}

def storyboard_to_manim_code(storyboard: dict) -> str:
    """Convert storyboard JSON to Manim code with automatic positioning & scaling."""
    lines = [
        "from manim import *",
        "",
        f"class {storyboard['title'].replace(' ', '')}(ThreeDScene):",
        "    def construct(self):"
    ]

    for idx, scene in enumerate(storyboard["scenes"], 1):
        lines.append(f"        # Scene {idx}: {scene['narration'][:50]}...")

        mobjects_map = {}
        row_objs = []
        row_count = 0
        row_width = 0

        # Create mobjects
        for mobj_idx, mobj in enumerate(scene.get("mobjects", []), 1):
            mobj_type = mobj["type"]
            mobj_name = mobj.get("kwargs", {}).get("name", f"{mobj_type.lower()}{idx}_{mobj_idx}")
            kwargs = sanitize_mobject_kwargs(mobj.get("kwargs", {}))
            kwargs_str = ", ".join(f"{k}={repr(v)}" for k, v in kwargs.items())
            lines.append(f"        {mobj_name} = {mobj_type}({kwargs_str})")

            # Automatic scaling based on row width
            approx_size = kwargs.get("radius", kwargs.get("side_length", 1))
            row_width += approx_size + 0.5  # buffer
            row_objs.append(mobj_name)
            row_count += 1

            if row_count >= MAX_ROW_OBJECTS or row_width > ROW_WIDTH_LIMIT:
                scale_factor = min(1, ROW_WIDTH_LIMIT / row_width)
                for obj in row_objs:
                    lines.append(f"        {obj}.scale({scale_factor})")
                # position row
                for i, obj in enumerate(row_objs):
                    if i == 0:
                        lines.append(f"        {obj}.to_edge(UP)")
                    else:
                        lines.append(f"        {obj}.next_to({row_objs[i-1]}, RIGHT, buff=0.5)")
                row_objs = []
                row_count = 0
                row_width = 0

            mobjects_map[mobj_name] = mobj_type

        # Place remaining objects if any
        if row_objs:
            for i, obj in enumerate(row_objs):
                if i == 0:
                    lines.append(f"        {obj}.to_edge(UP)")
                else:
                    lines.append(f"        {obj}.next_to({row_objs[i-1]}, RIGHT, buff=0.5)")

        # Play animations
        for anim in scene.get("animations", []):
            anim_type = anim.get("type")
            target = anim.get("target")
            if not target:
                continue

            # Map Gemini target (class name) to actual variable
            if isinstance(target, str):
                matched = None
                for name, cls in mobjects_map.items():
                    if cls == target or name == target:
                        matched = name
                        break
                if matched:
                    lines.append(f"        self.play({anim_type}({matched}))")

            elif isinstance(target, list):
                targets = []
                for t in target:
                    for name, cls in mobjects_map.items():
                        if cls == t or name == t:
                            targets.append(name)
                if targets:
                    targets_str = ", ".join(targets)
                    lines.append(f"        self.play({anim_type}({targets_str}))")

        lines.append("        self.wait(1)\n")

    return "\n".join(lines)

# =====================================
# MAIN PIPELINE
# =====================================
def main():
    topic = input("Enter your topic: ")

    # 1. Load allowed classes
    allowed_classes = load_allowed_classes(CSV_FILE)

    # 2. Storyboard generation
    print("Attempting to generate storyboard...")
    storyboard_prompt = build_storyboard_prompt(topic, allowed_classes)
    storyboard_text = call_gemini(storyboard_prompt)

    cleaned = extract_json(storyboard_text)
    cleaned = make_json_safe(cleaned)

    try:
        storyboard = json.loads(cleaned)
        print("✅ Storyboard JSON successfully parsed and validated")
    except json.JSONDecodeError as e:
        print("❌ Gemini did not return valid JSON:", e)
        print("Cleaned text:\n", cleaned)
        return

    # 3. Convert to Manim code
    script_code = storyboard_to_manim_code(storyboard)
    with open("generated_script.py", "w") as f:
        f.write(script_code)
    print("✅ Script saved to generated_script.py")

    # 4. Optional: render video
    try:
        print("\n🎬 Rendering video with Manim...")
        subprocess.run(["manim", "-pql", "generated_script.py"], check=True)
    except subprocess.CalledProcessError:
        print("❌ Rendering failed. Check your Manim installation and script.")

if __name__ == "__main__":
    main()
