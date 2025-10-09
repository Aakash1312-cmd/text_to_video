# =================================================================
# SN2 Substitution Reaction Animation using Manim + manim_chemistry
# Fixed for v0.19.0 — replaced GrowArrow with Create
# =================================================================

from manim import *
from manim_chemistry import *

class SN2Reaction(Scene):
    CONFIG = {
        "molecule_scale": 1.2,
        "arrow_color": YELLOW,
        "reaction_time": 3,
        "text_color": WHITE,
        "reagent_files": ["CH3Br.mol", "OH.mol"],
        # Replaced Br.mol with a special flag so we can render as MathTex
        "product_files": ["CH3OH.mol", "Br_MINUS"],
        "reaction_title": "SN2 Substitution Reaction",
        "conditions": "Solvent: Aqueous, Temp: Room Temperature",
    }

    def construct(self):
        # STEP 1: Intro
        self.introduce_reaction()

        # STEP 2: Load reagents & products
        reagents = self.load_molecules(self.CONFIG["reagent_files"], direction=LEFT)
        products = self.load_molecules(self.CONFIG["product_files"], direction=RIGHT)

        # STEP 3: Show reagents
        self.play(*[FadeIn(m) for m in reagents])
        self.wait(1)

        # STEP 4: Nucleophilic attack arrow
        attack_arrow = CurvedArrow(
            start_point=reagents[1].get_center(),
            end_point=reagents[0].get_center(),
            color=BLUE
        )
        self.play(Create(attack_arrow))   # ⬅ FIXED
        self.wait(1)

        # STEP 5: Leaving group arrow (Br⁻ leaves)
        leaving_arrow = CurvedArrow(
            start_point=reagents[0].get_center(),
            end_point=RIGHT * 4,
            color=RED
        )
        self.play(Create(leaving_arrow))  # ⬅ FIXED
        self.wait(1)

        # STEP 6: Reaction arrow
        reaction_arrow = self.create_reaction_arrow()
        self.play(Create(reaction_arrow)) # ⬅ FIXED
        self.wait(1)

        # STEP 7: Transform reagents into products
        self.animate_reaction(reagents, products, reaction_arrow, [attack_arrow, leaving_arrow])

        # STEP 8: Show conditions
        self.show_conditions()

        # STEP 9: Conclude
        self.conclude_reaction()

    # ------------------------------------------------------------
    # Helper Functions
    # ------------------------------------------------------------
    def introduce_reaction(self):
        title = Title(self.CONFIG["reaction_title"])
        self.play(Write(title))
        self.wait(1)
        self.play(FadeOut(title))

    def load_molecules(self, file_list, direction=LEFT):
        """
        Loads molecules. If file is 'Br_MINUS', renders Br- as MathTex instead of mol.
        """
        molecules = []
        spacing = 4
        for i, file in enumerate(file_list):
            if file == "Br_MINUS":
                mol = MathTex(r"\mathrm{Br}^{-}", font_size=64)
            else:
                mol = MMoleculeObject.molecule_from_file(file)
                mol.scale(self.CONFIG["molecule_scale"])
            mol.move_to(direction * (i * spacing + 3))
            molecules.append(mol)
        return molecules

    def create_reaction_arrow(self):
        return Arrow(
            start=LEFT*2,
            end=RIGHT*2,
            color=self.CONFIG["arrow_color"],
            buff=0.3,
            stroke_width=5,
        )

    def animate_reaction(self, reagents, products, reaction_arrow, arrows_to_remove):
        self.play(*[FadeOut(a) for a in arrows_to_remove])
        self.play(*[FadeOut(r) for r in reagents])
        self.play(*[FadeIn(p) for p in products])
        self.wait(self.CONFIG["reaction_time"])

    def show_conditions(self):
        cond = Tex(self.CONFIG["conditions"], color=self.CONFIG["text_color"]).scale(0.7)
        cond.next_to(ORIGIN, DOWN)
        self.play(FadeIn(cond))
        self.wait(2)

    def conclude_reaction(self):
        summary = Tex("Reaction Complete: CH$_3$OH + Br$^-$", color=GREEN).scale(1.1)
        summary.to_edge(UP)
        self.play(Write(summary))
        self.wait(2)
