from manim import *

class FriedelCraftsReaction(Scene):
    def construct(self):
        # ===== Load and scale images =====
        reactant = ImageMobject("benzene.png").scale(1.5)
        reagent = ImageMobject("alcl3.png").scale(1.5)
        alkyl_halide = ImageMobject("alkyl.png").scale(1.5)
        product = ImageMobject("product.png").scale(1.5)

        # ===== Position images =====
        reactant.to_edge(LEFT)
        reagent.next_to(reactant, RIGHT, buff=1.0)
        alkyl_halide.next_to(reagent, RIGHT, buff=1.0)
        product.to_edge(RIGHT)

        # ===== Add reactants =====
        self.play(FadeIn(reactant), FadeIn(reagent), FadeIn(alkyl_halide))
        self.wait(1)

        # ===== Show arrows =====
        arrow1 = Arrow(start=reactant.get_right(), end=product.get_left(), buff=0.2, color=YELLOW)
        self.play(GrowArrow(arrow1))
        self.wait(1)

        # ===== Fade out reactants and show product =====
        self.play(FadeOut(reactant), FadeOut(reagent), FadeOut(alkyl_halide))
        self.play(FadeIn(product))
        self.wait(2)

        # ===== Label reaction =====
        label = Text("Friedel-Crafts Alkylation", font_size=36).to_edge(UP)
        self.play(FadeIn(label))
        self.wait(2)
