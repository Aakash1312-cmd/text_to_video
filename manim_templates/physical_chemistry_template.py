# =================================================================
# General Manim Template for Physical Chemistry Animations
#
# TOPIC: Chemical Kinetics (First-Order Reaction Example)
#
# Template Structure:
# 1. Imports and Configuration: Manim, NumPy, and scene settings.
# 2. Scene Class: Inherits from manim.Scene.
#    - CONFIG: A dictionary for customizing chemical parameters (concentrations,
#      rate constants) and animation styles (colors, layout).
#    - construct(): The main script that directs the animation sequence.
#    - Helper Methods: Modular functions for each part of the explanation,
#      such as setting up the reaction vessel, running the simulation,
#      and displaying equations.
# =================================================================

from manim import *
import numpy as np
import random

class PhysicalChemistryTemplate(Scene):
    """
    A template for creating physical chemistry animations. This example demonstrates
    a first-order reaction (A -> B), but the structure is adaptable for a wide
    range of topics from thermodynamics to quantum chemistry.
    """

    # -----------------------------------------------------------------
    # 1. CONFIGURATION
    #    - Store constants for chemistry (e.g., concentrations, rate constants)
    #      and aesthetics (e.g., colors, text size) here for easy modification.
    # -----------------------------------------------------------------
    CONFIG = {
        # Chemical & Physical Parameters
        "initial_molecules_A": 100,
        "rate_constant": 0.5,

        # Simulation Parameters
        "simulation_runtime": 8,

        # Aesthetic Parameters
        "molecule_A_color": BLUE,
        "molecule_B_color": GREEN,
        "beaker_color": GRAY,
        "graph_color": YELLOW,
        "axes_config": {
            "x_range": [0, 8, 2],
            "y_range": [0, 110, 20],
            "x_length": 6,
            "y_length": 4,
            "axis_config": {"include_tip": False},
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
        self.run_reaction()

        # --- EXPLANATION ---
        self.show_equations()

        # --- CONCLUSION ---
        self.summarize_key_takeaways()
        self.wait(2)

    # -----------------------------------------------------------------
    # 2. HELPER METHODS (The "Scenes" of your video)
    # -----------------------------------------------------------------

    def introduce_concept(self):
        """Introduce the topic with a title and a brief description."""
        title = Title("Visualizing Chemical Kinetics")
        subtitle = Tex("A First-Order Reaction: A → B").next_to(title, DOWN)

        self.play(Write(title))
        self.play(FadeIn(subtitle, shift=UP))
        self.wait(2)
        self.play(FadeOut(title), FadeOut(subtitle))

    def setup_environment(self):
        """Create the environment: a beaker, molecules, and a graph."""
        # Create the reaction container
        beaker = Rectangle(width=4, height=4, color=self.CONFIG["beaker_color"]).to_edge(LEFT, buff=1)
        beaker_label = Tex("Reaction Vessel").next_to(beaker, DOWN)
        self.play(Create(beaker), Write(beaker_label))

        # Create initial reactant molecules (A)
        self.molecules_A = VGroup()
        for _ in range(self.CONFIG["initial_molecules_A"]):
            # Place molecules randomly within the beaker
            pos = beaker.get_center() + np.array([
                random.uniform(-1.8, 1.8),
                random.uniform(-1.8, 1.8),
                0
            ])
            self.molecules_A.add(Dot(pos, color=self.CONFIG["molecule_A_color"], radius=0.05))
        
        self.play(FadeIn(self.molecules_A, scale=0.5))
        self.molecules_B = VGroup() # For products

        # Create graph axes
        self.axes = Axes(**self.CONFIG["axes_config"]).to_edge(RIGHT, buff=1)
        labels = self.axes.get_axis_labels(x_label="Time (s)", y_label="[A] (% initial)")
        self.play(Create(self.axes), Write(labels))


    def run_reaction(self):
        """Animate the chemical reaction and plot the concentration change."""
        k = self.CONFIG["rate_constant"]
        n0 = self.CONFIG["initial_molecules_A"]

        # Function for the exponential decay of reactant A
        def concentration_func(t):
            return n0 * np.exp(-k * t)

        # Create the graph of concentration vs. time
        graph = self.axes.plot(lambda t: concentration_func(t) / n0 * 100,
                               x_range=[0, self.CONFIG["simulation_runtime"]],
                               color=self.CONFIG["graph_color"])

        # Use a ValueTracker to keep track of the current time in the simulation
        time = ValueTracker(0)

        # Updater to change molecules from A to B
        def update_molecules(mob):
            num_A_now = int(concentration_func(time.get_value()))
            
            # How many molecules have converted since the last frame
            num_to_convert = len(self.molecules_A) - num_A_now
            
            if num_to_convert > 0:
                for _ in range(num_to_convert):
                    if len(self.molecules_A) > 0:
                        # Pick a random A molecule, move it to B, and change color
                        mol = self.molecules_A.pop()
                        mol.set_color(self.CONFIG["molecule_B_color"])
                        self.molecules_B.add(mol)

        # Add the updater to the main scene so it runs every frame
        self.add_updater(update_molecules)

        self.play(
            Create(graph),
            time.animate.set_value(self.CONFIG["simulation_runtime"]),
            run_time=self.CONFIG["simulation_runtime"],
            rate_func=linear
        )
        
        # Stop the updater
        self.remove_updater(update_molecules)
        self.wait(1)

    def show_equations(self):
        """Display and explain the relevant mathematical principles."""
        rate_law = MathTex("Rate = k[A]").to_corner(UL)
        integrated_law = MathTex("[A]_t = [A]_0 e^{-kt}").next_to(rate_law, DOWN, aligned_edge=LEFT)

        equations = VGroup(rate_law, integrated_law)
        box = SurroundingRectangle(equations, buff=0.2, color=YELLOW)

        self.play(Write(equations), Create(box))
        self.wait(4)
        self.play(FadeOut(equations), FadeOut(box))

    def summarize_key_takeaways(self):
        """Provide a concluding summary."""
        summary_text = VGroup(
            Tex("Key Takeaways:"),
            Tex("- Reactant concentration decreases exponentially."),
            Tex("- The rate of reaction slows down over time."),
            Tex("- The half-life is constant for a first-order reaction.")
        ).arrange(DOWN, buff=0.4, aligned_edge=LEFT).to_center()

        self.play(FadeIn(summary_text))
        self.wait(4)
