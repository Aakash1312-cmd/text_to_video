import os
import time
import json
import traceback
import subprocess
from google import genai

MODEL = "gemini-2.5-flash"
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("❌ GEMINI_API_KEY not set in environment variables!")

client = genai.Client(api_key=API_KEY)

MASTER_RULESET = '''
# MASTER RULESET for Manim Code Generation
1. Imports:
   - Always: `from manim import *`
   - Always: Generate the latest manim code with latest attributes which is supported in the version of v0.20+
   - Do not: Strictly do not use attributes in the code that are not supported in the latest Manim version.

2. Scene & Classes:
   - Each script must have at least one Scene subclass with `construct(self)`
   - Helper methods allowed inside the class

3. Mobjects:
   - Use only valid Manim objects: Dot, Line, Circle, Polygon, ParametricFunction,
     MathTex, Text, RightAngle, Angle
   - Avoid overlapping text/mobjects using `.next_to()`, `.shift()`, `.to_edge()`

4. Colors:
   - Only valid Manim colors (WHITE, BLACK, RED, GREEN, BLUE, etc.)
   - Custom colors must be hex

5. To avoid overlapping text in Manim, adjust the text's positioning using methods like .shift(), or use the Text.wrap() method to control line breaks, or ensure sufficient spacing between text elements, either by modifying font size, line height, or using the Tex() object with a LaTeX minipage environment for more complex layouts. Below are the given methods to prevent overlapping of text and allow text wrapping. Use the required method in necessary situation in the 

6. Adjust Object Positioning : If the text is overlapping with another object (not just itself), you can move the text or the other object to create separation.
   - shift() method: Use the shift() method to move an object in a specific direction.
   - Example: 
     from manim import *
    class ShiftTextExample(Scene):
        def construct(self):
            text1 = Text("Hello")
            text2 = Text("World").next_to(text1, RIGHT) # This will position them side by side
            text2.shift(RIGHT * 0.5) # Shift text2 to the right to avoid overlap if they are too close

            self.play(Write(text1), Write(text2))
            self.wait()

7. Control Text Line Breaks and Wrapping: If your text is too long to fit on a single line and is causing overlap, you can wrap it.
    - Text.wrap(): Use this method to wrap text to the specified width.
    - Example:
      from manim import *

      class WrapTextExample(Scene):
        def construct(self):
            long_text = Text("This is a very long sentence that will need to be wrapped to prevent it from overlapping with other parts of the scene.")
            wrapped_text = long_text.wrap(6 * RIGHT) # Wrap at 6 units width

            self.play(Write(wrapped_text))
            self.wait()

    - Tex() with minipage: For more control over text formatting and wrapping within mathematical contexts, use the Tex() object with a LaTeX minipage environment.
    - Example:
      from manim import *

      class TexMinipageExample(Scene):
         def construct(self):
            latex_text = Tex(r"""
            \begin{minipage}{5cm}
            This is a very long sentence that will be wrapped inside a minipage environment.
            \end{minipage}
            """)
            latex_text.scale(0.5) # Adjust scale as needed

            self.play(Write(latex_text))
            self.wait()

8. Modify Font and Line Height: If you're working with a large block of text, adjust the line height to create more vertical spaces.
    - line_spacing attribute: You can set the line_spacing attribute on a Text object, though this may require more advanced setup.
    - Example:
      from manim import *

      class SpacedTextExample(Scene):
         def construct(self):
            text_with_spacing = Text("Text with greater line spacing").set_color(BLUE)
            text_with_spacing.line_spacing = 2 # Adjust this value for more space

            self.play(Write(text_with_spacing))
            self.wait()

9. MathTex:
   - Fractions/equations as ONE string: MathTex(r"\\frac{a}{b}")
   - Never index MathTex like expr[0]; split into separate MathTex objects if needed
10. Animations:
   - Only valid animations: FadeIn, FadeOut, Write, Create, Transform,
     ReplacementTransform, Indicate
   - Wait before removing objects: self.wait(0.5) or more
   - Clear scene safely: self.play(FadeOut(Group(*self.mobjects)))
11. Dynamic Objects / Updaters:
   - Use always_redraw(lambda: ...) for moving objects
   - Avoid intersections of parallel lines to prevent errors
12. Graphs / Functions:
   - Use NumberPlane.plot(func, x_range=[a, b], ...) instead of get_graph
   - Define axes explicitly before plotting
13. Geometry:
   - RightAngle requires two Line objects: RightAngle(line1, line2, length=0.3)
14. Execution Safety:
    - Gemini must dry-run exec() the script inside its response
    - Scripts must run standalone with `manim -pql <filename> <SceneClass>`
    - No placeholders or undefined variables
15. Multi-topic Support:
    - Works for Math, Physics, Electronics, Chemistry, Biology, AI, etc.
    - For diagrams/formulas, split complex objects into smaller parts
16. Output Format:
    - Return ONLY JSON: {"code": "<python_code>"}
    - No explanations, comments outside JSON, or TODOs
17. Text Handling:
    - Do not split `Text("...")` strings across multiple lines without quotes
    - For multi-line text, use `"""..."""` or embed `\\n` explicitly
18. Width & Positioning:
    - Do not chain `.get_center()` before `.set_width()` (invalid, returns ndarray)
    - Apply `.set_width(...)` directly on Mobjects, then use `.next_to(...)`
19. Layout Safety:
    - Always use `buff` in `.next_to(...)` to avoid overlaps
    - Verify placement visually with `.shift(...)` if necessary
20. Colors Restriction:
    - Only use built-in Manim named colors from the official palette
    - No custom hex colors, RGB tuples, or external definitions allowed
    - If a non-listed color is attempted, replace it with the nearest valid Manim color
    - Valid Manim colors include:
      WHITE, BLACK, RED, GREEN, BLUE, YELLOW, PURPLE, ORANGE, PINK,
      GRAY, GOLD, MAROON, TEAL, LIGHT_BROWN, DARK_GRAY
21. Vector & NumPy Safety:
    - Never call `.normalize()` on a NumPy ndarray
    - To normalize vectors: use `v_unit = v / np.linalg.norm(v)` for any numpy array `v`
    - For reflected rays, motion vectors, or custom directions:
        * Use NumPy arrays only for computation, then convert to Manim points via `.get_center() + vector`
    - Always define lengths separately: e.g., `reflected_ray_length = 3.0`
    - Use unit vectors for direction: `vector_unit = vector / np.linalg.norm(vector)` 
22. Updater Safety:
    - When using updaters that compute vectors, always normalize manually if needed
    - Avoid `.normalize()` calls; always prefer `v / np.linalg.norm(v)` 
23. Error Prevention:
    - Gemini-generated code must dry-run in Python to ensure:
        * All `.normalize()` calls replaced
        * All vectors are valid NumPy arrays or Manim points
        * No operations assume `.normalize()` exists on ndarrays, so normalize it using NumPy:
        * To move any mobject (including Axes) to the center, you should use move_to(ORIGIN) or simply .center().
        * In latest version of Manim CE, FRAME_WIDTH and FRAME_HEIGHT are not global constants anymore, use config.frame_width and config.frame_height instead. 
'''

example_input = "Youngs Double Slit Experiment"  
example_output = """from manim import *
import numpy as np

class YoungsDoubleSlit(Scene):
    def construct(self):
        # geometry / layout
        screen_x = 4.0
        barrier_x = -1.5
        slit_separation = 1.0
        slit_height = 0.5

        # Title
        title = Text("Young's Double Slit Experiment", font_size=50).to_edge(UP)
        self.play(Write(title))
        self.wait(0.5)

        # Screen (right)
        screen_line = Line(np.array([screen_x, 2.5, 0]), np.array([screen_x, -2.5, 0]))
        screen_label = Text("Screen", font_size=24).next_to(screen_line, RIGHT, buff=0.2)
        self.play(Create(screen_line), Write(screen_label))
        self.wait(0.4)

        # Barrier (two rectangles with a gap)
        top_rect = Rectangle(width=0.2, height=1.4).move_to(np.array([barrier_x, 1.0, 0]))
        bottom_rect = Rectangle(width=0.2, height=1.4).move_to(np.array([barrier_x, -1.0, 0]))
        top_rect.set_fill(GRAY, 1.0)
        bottom_rect.set_fill(GRAY, 1.0)
        self.play(FadeIn(top_rect), FadeIn(bottom_rect))
        self.wait(0.3)

        # slit points S1 and S2
        s1_pos = np.array([barrier_x, slit_separation / 2, 0])
        s2_pos = np.array([barrier_x, -slit_separation / 2, 0])
        s1_dot = Dot(s1_pos, color=BLUE, radius=0.08)
        s2_dot = Dot(s2_pos, color=BLUE, radius=0.08)
        slit_label_s1 = Text("S1", font_size=20).next_to(s1_dot, LEFT, buff=0.1)
        slit_label_s2 = Text("S2", font_size=20).next_to(s2_dot, LEFT, buff=0.1)
        self.play(FadeIn(s1_dot), FadeIn(s2_dot), Write(slit_label_s1), Write(slit_label_s2))
        self.wait(0.2)

        # 'd' separation annotation (use MathTex placed next to Brace)
        d_line = Line(s1_pos, s2_pos, color=GOLD)
        d_brace = Brace(d_line, LEFT)
        d_label = MathTex("d", font_size=30).next_to(d_brace, LEFT, buff=0.12)
        self.play(Create(d_line), Create(d_brace), Write(d_label))
        self.wait(0.3)

        # 'D' distance (slit center to screen center)
        D_line = Line(np.array([barrier_x, 0, 0]), np.array([screen_x, 0, 0]), color=GOLD)
        D_label = MathTex("D", font_size=30).next_to(D_line, DOWN, buff=0.2)
        self.play(Create(D_line), Write(D_label))
        self.wait(0.3)

        # Plane wave (visual)
        plane_wave_rect = Rectangle(width=1.0, height=5, fill_opacity=0.2, color=YELLOW).move_to(np.array([-6, 0, 0]))
        plane_wave_arrow = Arrow(np.array([-6.8, 0, 0]), np.array([-5.2, 0, 0]))
        plane_wave_text = Text("Plane Wave", font_size=24).next_to(plane_wave_rect, UP, buff=0.1)
        self.play(FadeIn(plane_wave_rect), FadeIn(plane_wave_arrow), Write(plane_wave_text))
        self.play(plane_wave_rect.animate.shift(RIGHT * 3), FadeOut(plane_wave_arrow), run_time=1.1)
        self.play(FadeOut(plane_wave_rect), FadeOut(plane_wave_text))
        self.wait(0.2)

        # Wavefronts from slits (several concentric circles)
        waves_group = Group()  # ✅ FIX: use Group, not VGroup
        max_radius = np.linalg.norm(np.array([screen_x - barrier_x, 0, 0])) + 0.5
        num_waves = 5
        wave_spacing = 0.6
        wave_anims = []
        for i in range(1, num_waves + 1):
            radius = i * wave_spacing
            if radius <= max_radius:
                wave1 = Circle(radius=radius).move_to(s1_pos).set_stroke(opacity=(num_waves - i + 1) / num_waves).set_color(BLUE)
                wave2 = Circle(radius=radius).move_to(s2_pos).set_stroke(opacity=(num_waves - i + 1) / num_waves).set_color(RED)
                waves_group.add(wave1, wave2)
                wave_anims.append(Create(wave1, run_time=0.12))
                wave_anims.append(Create(wave2, run_time=0.12))
        if wave_anims:
            self.play(LaggedStart(*wave_anims, lag_ratio=0.02))
        self.wait(0.7)

        # Highlight a point P on the screen and show S1P / S2P
        p_point = Dot(np.array([screen_x, 1.5, 0]), color=GREEN)
        p_label = Text("P", font_size=24).next_to(p_point, RIGHT, buff=0.12)
        self.play(FadeIn(p_point), Write(p_label))
        self.wait(0.15)
        line_s1p = Line(s1_pos, p_point.get_center(), color=BLUE)
        line_s2p = Line(s2_pos, p_point.get_center(), color=RED)
        self.play(Create(line_s1p), Create(line_s2p))
        self.wait(0.25)

        path_diff_label = MathTex(r"\text{Path Diff.} = S_2P - S_1P", font_size=35).to_edge(UP).shift(LEFT * 1.5)
        self.play(Write(path_diff_label))
        self.wait(0.25)

        # Angle theta representation (lines & Angle mobject)
        center_screen_point = np.array([screen_x, 0, 0])
        center_to_p_line = Line(center_screen_point, p_point.get_center(), color=GRAY)
        center_to_slit_center = Line(np.array([barrier_x, 0, 0]), center_screen_point, color=GRAY)
        self.play(Create(center_to_p_line), Create(center_to_slit_center))
        angle_theta = Angle(center_to_slit_center, center_to_p_line, radius=0.7)
        theta_label = MathTex(r"\theta", font_size=30).next_to(angle_theta, UP + RIGHT * 0.2)
        self.play(Create(angle_theta), Write(theta_label))
        self.wait(0.25)

        path_diff_formula_1 = MathTex(r"S_2P - S_1P \approx d \sin(\theta)", font_size=32).next_to(path_diff_label, DOWN, buff=0.3)
        self.play(Write(path_diff_formula_1))
        self.wait(0.5)

        # Conditions for interference
        constructive_text = Text("Constructive Interference (Bright Fringes):", font_size=26).to_edge(LEFT).shift(DOWN * 0.4)
        constructive_formula = MathTex(r"d \sin(\theta) = n \lambda \quad (n=0, \pm 1, \pm 2, ...)", font_size=28).next_to(constructive_text, DOWN, buff=0.15).align_to(constructive_text, LEFT)
        destructive_text = Text("Destructive Interference (Dark Fringes):", font_size=26).next_to(constructive_formula, DOWN, buff=0.35).align_to(constructive_text, LEFT)
        destructive_formula = MathTex(r"d \sin(\theta) = (n + \tfrac{1}{2}) \lambda \quad (n=0, \pm 1, \pm 2, ...)", font_size=28).next_to(destructive_text, DOWN, buff=0.15).align_to(constructive_text, LEFT)
        self.play(Write(constructive_text), Write(constructive_formula))
        self.wait(0.25)
        self.play(Write(destructive_text), Write(destructive_formula))
        self.wait(0.6)

        # Clear wave/path annotations to show fringes
        self.play(
            FadeOut(waves_group),
            FadeOut(line_s1p), FadeOut(line_s2p),
            FadeOut(p_point), FadeOut(p_label),
            FadeOut(path_diff_label), FadeOut(path_diff_formula_1),
            FadeOut(angle_theta), FadeOut(theta_label),
            FadeOut(center_to_p_line), FadeOut(center_to_slit_center),
        )
        self.wait(0.2)

        # Remove text formulas to make room
        self.play(FadeOut(constructive_text), FadeOut(constructive_formula), FadeOut(destructive_text), FadeOut(destructive_formula))
        self.wait(0.2)

        # Show fringe pattern on screen (visual)
        fringe_unit = 0.5
        fringe_dots = Group()  # ✅ FIX: use Group here
        num_fringes = 3  # 3 bright above + central + 3 bright below
        central_bright_dot = None
        first_upper_bright_dot = None

        for n in range(-num_fringes, num_fringes + 1):
            y_bright = n * fringe_unit
            bright_dot = Dot(center_screen_point + np.array([0, y_bright, 0]), color=RED, radius=0.12)
            fringe_dots.add(bright_dot)
            if n == 0:
                central_bright_dot = bright_dot
            if n == 1:
                first_upper_bright_dot = bright_dot

            # dark fringes
            if n < num_fringes:
                y_dark_upper = (n + 0.5) * fringe_unit
                dark_dot_upper = Dot(center_screen_point + np.array([0, y_dark_upper, 0]), color=DARK_GRAY, radius=0.08)
                fringe_dots.add(dark_dot_upper)
                if n > -num_fringes:
                    y_dark_lower = (n - 0.5) * fringe_unit
                    dark_dot_lower = Dot(center_screen_point + np.array([0, y_dark_lower, 0]), color=DARK_GRAY, radius=0.08)
                    fringe_dots.add(dark_dot_lower)

        self.play(LaggedStart(*[FadeIn(dot) for dot in fringe_dots], lag_ratio=0.05))
        self.wait(0.6)

        # Fringe width annotation between central and first upper bright fringe
        if central_bright_dot and first_upper_bright_dot:
            fringe_width_line = Line(central_bright_dot.get_center(), first_upper_bright_dot.get_center(), color=GOLD)
            fringe_width_brace = Brace(fringe_width_line, RIGHT)
            fringe_width_label = MathTex(r"\beta", font_size=30).next_to(fringe_width_brace, RIGHT, buff=0.12)
            self.play(Create(fringe_width_line), Create(fringe_width_brace), Write(fringe_width_label))
            self.wait(0.4)

        # Fringe width formula + references
        fringe_width_formula = MathTex(r"\beta = \frac{\lambda D}{d}", font_size=36).to_edge(UP).shift(LEFT * 1.2)
        lambda_label = MathTex(r"\lambda = \text{Wavelength}", font_size=24).next_to(fringe_width_formula, DOWN, buff=0.2).align_to(fringe_width_formula, LEFT)
        D_ref_label = MathTex(r"D = \text{Slit-Screen Dist.}", font_size=24).next_to(lambda_label, DOWN, buff=0.1).align_to(fringe_width_formula, LEFT)
        d_ref_label = MathTex(r"d = \text{Slit Separation}", font_size=24).next_to(D_ref_label, DOWN, buff=0.1).align_to(fringe_width_formula, LEFT)

        self.play(Write(fringe_width_formula))
        self.play(Write(lambda_label), Write(D_ref_label), Write(d_ref_label))
        self.wait(1.2)

        # Final fade out
        self.play(FadeOut(Group(*self.mobjects)))  # ✅ FIX: use Group not VGroup
        self.wait(0.5)"""  

def generate_manim_script(topic: str) -> str:
    """
    Generate a full advanced Manim script using few-shot prompting with MASTER_RULESET.
    """
    prompt = f"""
    Generate a full advanced Manim script on "{topic}".
    Follow the MASTER_RULESET strictly.
    Use few-shot examples:
    Example Input: {example_input}
    Example Output: {example_output}
    IMPORTANT:
    - Include a dry-run execution test using exec() inside the code to ensure it runs without syntax/runtime errors.
    - Return ONLY JSON: {{"code": "<python_code>"}}
    {MASTER_RULESET}
    """

    start_time = time.time()
    resp = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config={"response_mime_type": "application/json"}
    )
    end_time = time.time()
    print(f"[INFO] Script generation completed in {end_time - start_time:.2f} seconds.")

    try:
        result = json.loads(resp.text)
    except json.JSONDecodeError as e:
        print("[❌] Failed to parse JSON from Gemini:")
        print(resp.text)
        raise e

    return result["code"]

def debug_code(topic: str, code: str, error: str, max_retries: int = 5) -> str:
    """
    Iteratively fix Manim code using Gemini until it's error-free.
    """
    error_history = [error]
    attempt = 0
    fixed_code = code

    while attempt < max_retries:
        attempt += 1
        print(f"[DEBUG] Attempt {attempt} to fix code...")

        prompt = f"""
        {{
          "Role": "Senior Python & Manim debugging expert",
          "Context": "Fix Manim scripts that must run without errors",
          "Instructions": {{
            - Return ONLY JSON: {{"code": "<fixed_python_code>"}}
            - Do NOT include explanations or comments
            - Apply the MASTER_RULESET strictly
            - Fix ALL errors in error_history
            - Dry-run exec() the code internally to verify
          }},
          "Input": {{
            "topic": "{topic}",
            "current_code": {repr(fixed_code)},
            "error_history": {repr(error_history)}
          }},
          "Output": {{"code": "string"}}
        }}
        """

        resp = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "max_output_tokens": 3000
            }
        )

        try:
            result = json.loads(resp.text)
            fixed_code = result["code"]
        except json.JSONDecodeError as e:
            print("[❌] Failed to parse JSON during debug:")
            print(resp.text)
            raise e

        try:
            exec(fixed_code, {})
            print("[✅] Debugged code executed successfully in dry-run.")
            return fixed_code
        except Exception as e2:
            new_error = traceback.format_exc()
            print(f"[❌] Still failing. Error captured:\n{new_error}")
            error_history.append(new_error)

    raise RuntimeError("❌ Max retries reached. Could not fix the code automatically.")

def main():
    topic = input("Enter the topic for Manim script: ").strip()
    if not topic:
        print("Topic cannot be empty!")
        return

    start_total = time.time()
    print("[INFO] Generating Manim script...")

    script_code = generate_manim_script(topic)

    try:
        exec(script_code, {})
    except Exception:
        print("[ERROR] Initial script execution failed, sending to debug...")
        traceback_details = traceback.format_exc()
        script_code = debug_code(topic, script_code, traceback_details)

    safe_topic = topic.replace(" ", "_")
    filename = f"{safe_topic}.py"
    with open(filename, "w") as f:
        f.write(script_code)

    print(f"[INFO] Script saved as: {filename}")

    class_name = None
    for line in script_code.splitlines():
        if line.strip().startswith("class ") and "(Scene)" in line:
            class_name = line.split("class ")[1].split("(")[0].strip()
            break

    if not class_name:
        raise ValueError("❌ Could not find a Scene class in the script.")

    print(f"[INFO] Running: manim -pql {filename} {class_name}")
    try:
        subprocess.run(["manim", "-pql", filename, class_name], check=True)
    except subprocess.CalledProcessError as e:
        print("[❌] Manim CLI execution failed.")
        print(e)

    end_total = time.time()
    print(f"[INFO] Total pipeline execution time: {end_total - start_total:.2f} seconds.")

if __name__ == "__main__":
    main()
