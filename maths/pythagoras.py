# =================================================================
# Manim Animation for the Pythagorean Theorem (2D - CORRECTED)
#
# TOPIC: a^2 + b^2 = c^2
#
# This version is corrected to work with modern Manim APIs,
# resolving errors related to 'get_edge' and 'Checkmark'.
# =================================================================

from manim import *
import numpy as np

class PythagoreanTheoremScene(Scene):
    """
    An animation that introduces, visually proves, and provides an example
    of the Pythagorean Theorem.
    """
    
    # --- CONFIGURATION ---
    CONFIG = {
        "side_a": 3.0,
        "side_b": 4.0,
        "triangle_color": WHITE,
        "square_a_color": BLUE,
        "square_b_color": RED,
        "square_c_color": GREEN,
        "angle_color": YELLOW,
    }

    def construct(self):
        """
        The main method that defines the animation sequence.
        """
        self.introduce_theorem()
        self.animate_visual_proof()
        self.show_concrete_example()
        self.wait(3)

    # --- HELPER METHODS (Building Blocks of the Animation) ---

    def introduce_theorem(self):
        """Creates a right-angled triangle and displays the theorem's formula."""
        # Define triangle vertices
        p1 = ORIGIN
        p2 = RIGHT * self.CONFIG["side_b"]
        p3 = p2 + UP * self.CONFIG["side_a"]
        
        # ✅ FIX: Create sides as individual Line objects
        self.side_b = Line(p1, p2, color=self.CONFIG["triangle_color"])
        self.side_a = Line(p2, p3, color=self.CONFIG["triangle_color"])
        self.side_c = Line(p3, p1, color=self.CONFIG["triangle_color"])
        
        # Group the lines to form the visual triangle
        self.triangle = VGroup(self.side_a, self.side_b, self.side_c)
        
        right_angle = Square(
            side_length=0.4, 
            color=self.CONFIG["angle_color"], 
            stroke_width=3
        ).move_to(p2, aligned_edge=UL)
        
        # ✅ FIX: Use the Line objects for positioning labels
        label_a = MathTex("a").next_to(self.side_a, LEFT)
        label_b = MathTex("b").next_to(self.side_b, DOWN)
        label_c = MathTex("c").next_to(self.side_c, UR, buff=-0.2)
        self.labels = VGroup(label_a, label_b, label_c)

        # Create formula
        self.formula = MathTex("a^2", "+", "b^2", "=", "c^2").to_edge(UP)
        self.formula[0].set_color(self.CONFIG["square_a_color"])
        self.formula[2].set_color(self.CONFIG["square_b_color"])
        self.formula[4].set_color(self.CONFIG["square_c_color"])

        # Animate
        self.play(Create(self.triangle), Create(right_angle))
        self.play(Write(self.labels))
        self.wait(1)
        self.play(Write(self.formula))
        self.wait(2)

    def animate_visual_proof(self):
        """Animates the classic rearrangement proof of the theorem."""
        intro_group = VGroup(self.triangle, self.labels, self.formula.copy()[0:5:2])
        self.play(intro_group.animate.scale(0.6).to_edge(DL))
        
        # ✅ FIX: Use the Line objects for positioning squares
        square_a = Square(side_length=self.CONFIG["side_a"], color=self.CONFIG["square_a_color"], fill_opacity=0.7).next_to(self.side_a, LEFT, buff=0)
        square_b = Square(side_length=self.CONFIG["side_b"], color=self.CONFIG["square_b_color"], fill_opacity=0.7).next_to(self.side_b, DOWN, buff=0)
        
        c_length = self.side_c.get_length()
        angle = self.side_c.get_angle()
        square_c = Square(side_length=c_length, color=self.CONFIG["square_c_color"], fill_opacity=0.7)
        square_c.move_to(self.side_c.get_center()).rotate(angle, about_point=square_c.get_center())

        self.play(Create(square_a), Create(square_b), Create(square_c))
        self.wait(2)
        
        area_a_copy = square_a.copy()
        area_b_copy = square_b.copy()
        
        self.play(
            FadeOut(intro_group),
            FadeOut(self.formula),
            ReplacementTransform(area_a_copy, square_c),
            ReplacementTransform(area_b_copy, square_c),
            run_time=3
        )
        self.wait(2)
        self.proof_mobjects = VGroup(square_a, square_b, square_c)

    def show_concrete_example(self):
        """Clears the scene and shows a calculation with a 3-4-5 triangle."""
        self.play(FadeOut(self.proof_mobjects))
        
        title = Title("Example: A 3-4-5 Triangle")
        self.play(Write(title))

        formula_345 = MathTex("3^2", "+", "4^2", "=", "5^2", font_size=60).shift(UP * 0.5)
        formula_345[0].set_color(self.CONFIG["square_a_color"])
        formula_345[2].set_color(self.CONFIG["square_b_color"])
        formula_345[4].set_color(self.CONFIG["square_c_color"])
        
        self.play(Write(formula_345))
        self.wait(1)

        calculation_1 = MathTex("9", "+", "16", "=", "25", font_size=60).next_to(formula_345, DOWN, buff=0.8)
        calculation_1[0].set_color(self.CONFIG["square_a_color"])
        calculation_1[2].set_color(self.CONFIG["square_b_color"])
        calculation_1[4].set_color(self.CONFIG["square_c_color"])

        self.play(ReplacementTransform(formula_345.copy(), calculation_1))
        self.wait(1)

        final_result = MathTex("25", "=", "25", font_size=60).next_to(calculation_1, DOWN, buff=0.8)
        final_result.set_color(GREEN)
        
        # ✅ FIX: Replaced Checkmark() with MathTex(r"\checkmark")
        checkmark = MathTex(r"\checkmark", color=GREEN).next_to(final_result, RIGHT)

        self.play(ReplacementTransform(calculation_1.copy(), final_result))
        self.play(Create(checkmark))
