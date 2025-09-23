#!/usr/bin/env python3
"""
manim_pipeline.py

End-to-end pipeline:
  1. Load allowed classes CSV.
  2. Ask Gemini to generate a storyboard (frames with visuals + dialogue + duration).
  3. For each frame: generate TTS audio file with Gemini TTS.
  4. Build a Manim script that plays audio + visuals in sync.
  5. Render video with Manim.
"""

import os
import csv
import subprocess
import wave
import sys
from typing import Dict, List

import google.generativeai as genai
from google import genai as genai_client
from google.genai import types

try:
    import pyaudio
    HAVE_PYAUDIO = True
except Exception:
    HAVE_PYAUDIO = False

CSV_FILE = "manim_classes_with_description.csv"
MAX_RETRIES = 3
MANIM_OUTPUT_DIR = "media/videos"
AUDIO_SAMPLE_RATE = 24000
AUDIO_CHANNELS = 1
AUDIO_SAMPLE_WIDTH = 2

API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    print("ERROR: GEMINI_API_KEY not set in environment.")
    sys.exit(1)

# Configure Gemini
genai.configure(api_key=API_KEY)
g_text_model = genai.GenerativeModel("gemini-1.5-flash")
g_tts_client = genai_client.Client(api_key=API_KEY)

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

def request_storyboard_from_gemini(topic: str, allowed: Dict[str, set], max_frames: int = 8) -> List[dict]:
    allowed_summary = (
        f"Scenes: {sorted(allowed['Scene'])}\n"
        f"Mobjects: {sorted(allowed['Mobject'])}\n"
        f"Animations: {sorted(allowed['Animation'])}"
    )

    prompt = f"""
You are an expert Manim video designer. Produce a STORYBOARD for the topic below.
Output MUST be valid JSON (an array).

Topic: "{topic}"

Each frame:
- frame_index: int
- visual_instructions: short Manim-friendly description
- dialogue: concise spoken text
- duration: float seconds

Allowed classes:
{allowed_summary}
"""

    import json
    for attempt in range(1, MAX_RETRIES + 1):
        resp = g_text_model.generate_content(prompt)
        text = resp.text.strip()
        if "[" in text and "]" in text:
            start = text.find("[")
            end = text.rfind("]") + 1
            json_like = text[start:end]
            try:
                storyboard = json.loads(json_like)
                if isinstance(storyboard, list):
                    return storyboard
            except Exception as e:
                print(f"Attempt {attempt}: JSON parse error {e}")
        print(f"Attempt {attempt}: malformed output, retrying...")
    raise RuntimeError("Failed to obtain storyboard from Gemini.")

def generate_tts_for_text(text: str, out_wav_path: str):
    speech_config = types.SpeechConfig(
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Zephyr")
        )
    )

    response = g_tts_client.models.generate_content(
        model="models/gemini-2.5-flash-preview-tts",
        contents=text,
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=speech_config,
        ),
    )

    audio_bytes = response.candidates[0].content.parts[0].inline_data.data

    if HAVE_PYAUDIO:
        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(AUDIO_SAMPLE_WIDTH),
                        channels=AUDIO_CHANNELS,
                        rate=AUDIO_SAMPLE_RATE,
                        output=True)
        stream.write(audio_bytes)
        stream.stop_stream()
        stream.close()
        p.terminate()

    with wave.open(out_wav_path, "wb") as wf:
        wf.setnchannels(AUDIO_CHANNELS)
        wf.setsampwidth(AUDIO_SAMPLE_WIDTH)
        wf.setframerate(AUDIO_SAMPLE_RATE)
        wf.writeframes(audio_bytes)

    with wave.open(out_wav_path, "rb") as r:
        nframes = r.getnframes()
        fr = r.getframerate()
        duration = nframes / float(fr)
    return duration

def build_manim_script(storyboard: List[dict], allowed: Dict[str, set], script_path: str):
    import textwrap

    header = textwrap.dedent("""\
    from manim import *
    def safe_angle(line1, line2, **kwargs):
        try:
            return Angle(line1, line2, **kwargs)
        except ValueError:
            return None

    class GeneratedStoryboardScene(Scene):
        def construct(self):
    """)

    body_lines = []
    body_prelude = textwrap.dedent("""
        def _pos(tok):
            mapping = {
                'LEFT': LEFT, 'RIGHT': RIGHT, 'UP': UP, 'DOWN': DOWN,
                'ORIGIN': ORIGIN, 'UL': UP+LEFT, 'UR': UP+RIGHT,
                'DL': DOWN+LEFT, 'DR': DOWN+RIGHT
            }
            return mapping.get(tok.upper(), ORIGIN)
    """)
    body_lines.append(textwrap.indent(body_prelude, " " * 8))

    for frame in storyboard:
        i = frame["frame_index"]
        instr = frame["visual_instructions"]
        dialogue = frame["dialogue"].replace('"', r'\"')
        duration = float(frame["duration"])
        audio_filename = f"audio_frame_{i}.wav"

        frame_code = []
        frame_code.append(f"# Frame {i}: {instr}")
        frame_code.append("if self.mobjects:")
        frame_code.append("    self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.3)")

        instr_upper = instr.upper()
        created_names = []
        if "CIRCLE" in instr_upper:
            var = f"c{i}"
            frame_code.append(f"{var} = Circle().shift(LEFT)")
            created_names.append(var)
        if "DOT" in instr_upper:
            var = f"d{i}"
            frame_code.append(f"{var} = Dot().shift(RIGHT)")
            created_names.append(var)
        if "TRIANGLE" in instr_upper:
            var = f"t{i}"
            frame_code.append(f"{var} = Triangle().shift(UP)")
            created_names.append(var)
        if "RECTANGLE" in instr_upper:
            var = f"r{i}"
            frame_code.append(f"{var} = Rectangle(width=2, height=1).shift(DOWN)")
            created_names.append(var)
        if "MATH" in instr_upper or "EQUATION" in instr_upper:
            var = f"mt{i}"
            frame_code.append(f'{var} = MathTex(r"e^{{i\\pi}} + 1 = 0").to_edge(UP)')
            created_names.append(var)

        if created_names:
            frame_code.append(f"self.play({', '.join(['Create('+n+')' for n in created_names])})")
        else:
            frame_code.append(f"txt{i} = Text('{dialogue[:40]}')")
            frame_code.append(f"self.play(Create(txt{i}))")

        frame_code.append(f"self.add_sound(r'{audio_filename}')")
        frame_code.append(f"self.wait({duration})")

        frame_code.append("if self.mobjects:")
        frame_code.append("    self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.2)")

        body_lines.append("\n" + textwrap.indent("\n".join(frame_code), " " * 8))

    script_text = header + "\n".join(body_lines)

    with open(script_path, "w", encoding="utf-8") as f:
        f.write(script_text)
    print(f"Manim script written to {script_path}")

def render_manim(script_path: str):
    try:
        print("\n🎬 Rendering video with Manim...")
        subprocess.run(["manim", "-pql", script_path], check=True)
        print("\n✅ Video rendered successfully!")
    except subprocess.CalledProcessError as e:
        print("❌ Manim rendering failed:", e)

def pipeline_main():
    topic = input("Enter your topic: ").strip()
    if not topic:
        print("No topic supplied. Exiting.")
        return

    allowed = load_allowed_classes(CSV_FILE)
    print("Allowed classes loaded.")

    print("Requesting storyboard from Gemini...")
    storyboard = request_storyboard_from_gemini(topic, allowed, max_frames=6)
    print(f"Received storyboard with {len(storyboard)} frames.")

    audio_files = []
    for frame in storyboard:
        i = frame["frame_index"]
        dialogue = frame["dialogue"].strip()
        filename = f"audio_frame_{i}.wav"
        print(f"Generating TTS for frame {i}: {dialogue}")
        duration = generate_tts_for_text(dialogue, filename)
        print(f"  saved {filename} ({duration:.2f}s)")
        audio_files.append(filename)

    script_path = "generated_script.py"
    build_manim_script(storyboard, allowed, script_path)
    render_manim(script_path)

    print("\nPipeline complete.")
    print("Generated script:", script_path)
    for af in audio_files:
        print("Audio:", af)

if __name__ == "__main__":
    pipeline_main()
