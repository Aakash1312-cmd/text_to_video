# =================================================================
# General Manim Template for Chemistry Animations
#
# TOPIC: Universal Template for Organic & Inorganic Chemistry Reactions
#
# Structure:
# 1. Imports and Configuration
# 2. Reaction Scene Class with Helper Functions
# 3. Add Molecules (.mol format using manim_chemistry)
# 4. Animate Reaction Mechanisms (e.g., bonds breaking/forming, arrows)
# 5. Add Text/Equations (reaction info, conditions)
# 6. Flexible to work with any topic (Aldol Condensation, Wurtz, SN1...)
# =================================================================

from manim import *
from manim_chemistry import *

class ChemistryReactionTemplate(Scene):
    """
    Universal template for animating chemical reactions.
    Works with organic and inorganic reactions using .mol files.
    """

    CONFIG = {
        # Aesthetic settings
        "molecule_scale": 1.2,
        "arrow_color": YELLOW,
        "reaction_time": 3,
        "text_color": WHITE,

        # File paths for .mol structures (replace with your molecules)
        "reagent_files": ["reagent1.mol", "reagent2.mol"],
        "product_files": ["product.mol"],

        # Reaction label
        "reaction_title": "General Reaction",
        "conditions": "Temperature: 25°C, Catalyst: None",
    }

    def construct(self):
        self.introduce_reaction()
        
        reagents = self.load_molecules(self.CONFIG["reagent_files"], direction=LEFT)
        products = self.load_molecules(self.CONFIG["product_files"], direction=RIGHT)

        # STEP 3: Show reagents
        self.play(*[FadeIn(m) for m in reagents])
        self.wait(1)

        # STEP 4: Add reaction arrow
        arrow = self.create_reaction_arrow()
        self.play(GrowArrow(arrow))
        self.wait(1)

        # STEP 5: Transform reagents into products
        self.animate_reaction(reagents, products, arrow)

        # STEP 6: Show conditions
        self.show_conditions()

        # STEP 7: End screen
        self.conclude_reaction()

    # ------------------------------------------------------------
    # Helper Functions
    # ------------------------------------------------------------
    def introduce_reaction(self):
        """Display the title of the reaction."""
        title = Title(self.CONFIG["reaction_title"])
        self.play(Write(title))
        self.wait(1)
        self.play(FadeOut(title))

    def load_molecules(self, file_list, direction=LEFT):
        """Load .mol files as molecule objects and position them."""
        molecules = []
        spacing = 4
        for i, file in enumerate(file_list):
            mol = MMoleculeObject.molecule_from_file(file)
            mol.scale(self.CONFIG["molecule_scale"])
            mol.move_to(direction * (i * spacing + 3))
            molecules.append(mol)
        return molecules

    def create_reaction_arrow(self):
        """Draws the reaction arrow between reagents and products."""
        arrow = Arrow(
            start=LEFT*2,
            end=RIGHT*2,
            color=self.CONFIG["arrow_color"],
            buff=0.3,
            stroke_width=5,
        )
        return arrow

    def animate_reaction(self, reagents, products, arrow):
        """Animate the reaction (Fade out reagents, Fade in products)."""
        self.play(*[FadeOut(r) for r in reagents])
        self.play(*[FadeIn(p) for p in products])
        self.wait(self.CONFIG["reaction_time"])

    def show_conditions(self):
        """Display reaction conditions below the arrow."""
        cond = Tex(self.CONFIG["conditions"], color=self.CONFIG["text_color"]).scale(0.7)
        cond.next_to(ORIGIN, DOWN)
        self.play(FadeIn(cond))
        self.wait(2)

    def conclude_reaction(self):
        """Highlight final products or give a summary."""
        summary = Tex("Reaction Complete!", color=GREEN).scale(1.2)
        summary.to_edge(UP)
        self.play(Write(summary))
        self.wait(2)
