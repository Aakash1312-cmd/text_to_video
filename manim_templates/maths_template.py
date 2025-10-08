# =================================================================
# General Manim Template for Mathematical Animations
#
# TOPIC: Visualizing the Derivative of a Function
#
# Template Structure:
# 1. Imports: Essential Manim and NumPy libraries.
# 2. Scene Class: A class inheriting from manim.Scene.
#    - CONFIG: A dictionary for easy customization of parameters.
#    - setup(): (Optional) For initializing state variables.
#    - construct(): The main method that orchestrates the animation.
#    - Helper Methods: Modular functions for specific tasks
#      (e.g., creating axes, animating concepts, showing equations).
# =================================================================

from manim import *
import numpy as np

class MathConceptAnimation(Scene):
    """
    A template scene for creating mathematical animations.
    This example visualizes the concept of the derivative.
    """
    
    # -----------------------------------------------------------------
    # 1. CONFIGURATION
    #    - Store constants here for easy tweaking of the animation.
    # -----------------------------------------------------------------
    CONFIG = {
        "function": lambda x: 0.1 * (x - 2) * (x + 2) * x + 1,
        "function_color": BLUE,
        "tangent_line_color": GREEN,
        "secant_line_color": YELLOW,
        "axes_config": {
            "x_range": [-4, 4, 1],
            "y_range": [-2, 4, 1],
            "x_length": 10,
            "y_length": 6,
            "axis_config": {"include_tip": False},
        },
        "initial_x": 2.0,
        "dx_initial": 1.5,
        "dx_final": 0.01,
        "animation_run_time": 5,
    }

    def construct(self):
        """
        The main method that defines the animation sequence.
        It calls helper methods in a logical order to build the story.
        """
        # --- SCENE SETUP ---
        self.setup_axes_and_graph()
        
        # --- INTRODUCTION ---
        self.introduce_secant_line()
        
        # --- CORE ANIMATION ---
        self.animate_secant_to_tangent()
        
        # --- CONCLUSION ---
        self.display_derivative_formula()
        
        self.wait(2)

    # -----------------------------------------------------------------
    # 2. HELPER METHODS (Building Blocks of the Animation)
    # -----------------------------------------------------------------

    def setup_axes_and_graph(self):
        """Creates and displays the axes and the function graph."""
        self.axes = Axes(**self.CONFIG["axes_config"])
        self.graph = self.axes.plot(
            self.CONFIG["function"], 
            color=self.CONFIG["function_color"]
        )
        graph_label = self.axes.get_graph_label(self.graph, label="f(x)")
        
        self.play(Create(self.axes), Create(self.graph), Write(graph_label))
        self.wait(1)

    def introduce_secant_line(self):
        """Introduces the concept of a secant line between two points."""
        # ValueTrackers to make points and lines dynamic
        self.x_tracker = ValueTracker(self.CONFIG["initial_x"])
        self.dx_tracker = ValueTracker(self.CONFIG["dx_initial"])

        # Create the secant line Mobject
        self.secant_group = self.get_secant_line_group()

        # Animate its creation
        self.play(
            Create(self.secant_group),
            run_time=2
        )
        self.wait(1)

    def animate_secant_to_tangent(self):
        """Animates the transformation of the secant line into a tangent line."""
        
        # The secant_group already has updaters, so we just animate the dx_tracker.
        self.play(
            self.dx_tracker.animate.set_value(self.CONFIG["dx_final"]),
            run_time=self.CONFIG["animation_run_time"]
        )
        self.wait(1)

        # Change color to signify it is now the tangent line
        self.secant_group.submobjects[0].set_color(self.CONFIG["tangent_line_color"]) # The line itself
        self.play(
            Write(
                Tex("Tangent Line", color=self.CONFIG["tangent_line_color"])
                .next_to(self.secant_group, UR, buff=0.2)
            )
        )
        self.wait(1)

    def display_derivative_formula(self):
        """Displays the final formula for the derivative."""
        formula = MathTex(
            r"\frac{df}{dx} = \lim_{h \to 0} \frac{f(x+h) - f(x)}{h}",
            font_size=48
        )
        formula.to_edge(UP)
        
        self.play(Write(formula))
        self.wait(1)

    # -----------------------------------------------------------------
    # 3. UTILITY METHODS (Reusable Mobject Creators)
    #    - These methods generate Mobjects that can be updated.
    # -----------------------------------------------------------------
    
    def get_secant_line_group(self):
        """
        Creates a VGroup containing a secant line and its two endpoints.
        This group is updatable.
        """
        # Define points based on the trackers
        def get_point_p1():
            x = self.x_tracker.get_value()
            return self.axes.c2p(x, self.CONFIG["function"](x))

        def get_point_p2():
            x = self.x_tracker.get_value()
            dx = self.dx_tracker.get_value()
            return self.axes.c2p(x + dx, self.CONFIG["function"](x + dx))

        # Create the visual elements (dots and a line)
        p1 = Dot(point=get_point_p1(), color=YELLOW)
        p2 = Dot(point=get_point_p2(), color=YELLOW)
        line = Line(p1.get_center(), p2.get_center(), color=self.CONFIG["secant_line_color"])
        
        # Add updaters so they move when trackers change
        p1.add_updater(lambda m: m.move_to(get_point_p1()))
        p2.add_updater(lambda m: m.move_to(get_point_p2()))
        line.add_updater(lambda m: m.put_start_and_end_on(p1.get_center(), p2.get_center()))

        return VGroup(line, p1, p2)