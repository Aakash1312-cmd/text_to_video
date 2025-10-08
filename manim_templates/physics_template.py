# =================================================================
# General Manim Template for Physics Animations
#
# TOPIC: Projectile Motion (Example)
#
# Template Structure:
# 1. Imports and Configuration: Manim, NumPy, and scene settings.
# 2. Scene Class: Inherits from manim.Scene or manim.ThreeDScene.
#    - CONFIG: A dictionary for easy customization of physical parameters and styles.
#    - construct(): The main "script" that orchestrates the animation sequence.
#    - Helper Methods: Modular functions for distinct parts of the explanation
#      (e.g., setup, simulation, explanation, conclusion).
# =================================================================

from manim import *
import numpy as np

class PhysicsSimulationTemplate(Scene):
    """
    A template for creating physics animations. This example demonstrates
    projectile motion, but the structure is applicable to a wide range
    of physics topics.
    """

    # -----------------------------------------------------------------
    # 1. CONFIGURATION
    #    - Store constants for physics (e.g., gravity, initial velocity)
    #      and aesthetics (e.g., colors, text size) here for easy modification.
    # -----------------------------------------------------------------
    CONFIG = {
        # Physical Parameters
        "gravity": 9.8,
        "initial_velocity": 20.0,
        "launch_angle_deg": 60,

        # Simulation Parameters
        "simulation_runtime": 5,

        # Aesthetic Parameters
        "projectile_color": YELLOW,
        "path_color": BLUE,
        "vector_color": GREEN,
        "axes_config": {
            "x_range": [0, 40, 5],
            "y_range": [0, 20, 5],
            "x_length": 12,
            "y_length": 7,
        }
    }

    def construct(self):
        """
        The main method defining the animation sequence. It calls helper
        methods in a logical order to build a coherent explanation.
        """
        # --- INTRODUCTION ---
        self.introduce_concept()

        # --- SETUP & SIMULATION ---
        self.setup_environment()
        self.run_simulation()

        # --- EXPLANATION ---
        self.show_equations()

        # --- CONCLUSION ---
        self.summarize_key_takeaways()
        self.wait(2)

    # -----------------------------------------------------------------
    # 2. HELPER METHODS (The "Scenes" of your video)
    # -----------------------------------------------------------------

    def introduce_concept(self):
        """Introduce the topic with a title and brief description."""
        title = Title("Visualizing Projectile Motion")
        question = Tex("What path does a thrown object follow under gravity?")

        self.play(Write(title))
        self.play(FadeIn(question, shift=UP))
        self.wait(2)
        self.play(FadeOut(title), FadeOut(question))

    def setup_environment(self):
        """Create the physical environment, like axes, ground, etc."""
        self.axes = Axes(**self.CONFIG["axes_config"])
        labels = self.axes.get_axis_labels(x_label="Distance (m)", y_label="Height (m)")
        self.play(Create(self.axes), Write(labels))

        # Create the projectile object
        self.projectile = Dot(
            point=self.axes.c2p(0, 0),
            color=self.CONFIG["projectile_color"],
            radius=0.1
        )
        self.play(FadeIn(self.projectile))

    def run_simulation(self):
        """Animate the physical process based on the defined parameters."""
        # Convert angle to radians for calculations
        angle_rad = np.deg2rad(self.CONFIG["launch_angle_deg"])
        v0 = self.CONFIG["initial_velocity"]
        g = self.CONFIG["gravity"]

        # Parametric equations of motion
        def get_projectile_position(t):
            x = v0 * np.cos(angle_rad) * t
            y = v0 * np.sin(angle_rad) * t - 0.5 * g * t**2
            # Stop the projectile if it hits the ground (y < 0)
            if y < 0:
                time_of_flight = 2 * v0 * np.sin(angle_rad) / g
                x = v0 * np.cos(angle_rad) * time_of_flight
                y = 0
            return self.axes.c2p(x, y)

        # Create the path traced by the projectile
        path = self.axes.plot(
            lambda x: (
                np.tan(angle_rad) * x
                - (g / (2 * (v0 * np.cos(angle_rad))**2)) * x**2
            ),
            x_range=[
                0,
                (v0**2 * np.sin(2 * angle_rad) / g) # Calculate max range
            ],
            color=self.CONFIG["path_color"]
        )

        # Use an updater to move the projectile along the path
        self.projectile.add_updater(
            lambda m, dt: m.move_to(get_projectile_position(self.time - m.initial_time))
        )
        self.projectile.initial_time = self.time

        self.play(
            Create(path),
            run_time=self.CONFIG["simulation_runtime"],
            rate_func=linear
        )
        self.projectile.clear_updaters() # Stop the animation
        self.wait(1)

    def show_equations(self):
        """Display and explain the mathematical principles."""
        # Create MathTex objects for the equations of motion
        eq_x = MathTex("x(t) = v_0 \\cos(\\theta) \\cdot t")
        eq_y = MathTex("y(t) = v_0 \\sin(\\theta) \\cdot t - \\frac{1}{2} g t^2")

        equations = VGroup(eq_x, eq_y).arrange(DOWN, aligned_edge=LEFT).to_corner(UR)
        
        # Add a surrounding rectangle for emphasis
        box = SurroundingRectangle(equations, buff=0.2, color=BLUE)

        self.play(Write(equations), Create(box))
        self.wait(4)

    def summarize_key_takeaways(self):
        """Provide a concluding summary."""
        # Fade out everything except the path
        mobjects_to_fade = VGroup(
            self.axes,
            self.projectile,
            *self.mobjects # Catch any remaining mobjects like labels and equations
        ).remove(self.projectile, self.axes.get_axis_labels())

        self.play(FadeOut(mobjects_to_fade, run_time=1.5))

        # Highlight key results
        summary_text = VGroup(
            Tex("The path is a parabola."),
            Tex("Maximum height and range depend on launch angle and initial velocity.")
        ).arrange(DOWN, buff=0.5).to_edge(UP)

        self.play(Write(summary_text))
        self.wait(3)