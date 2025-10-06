from manim import *

class PerkinCondensation(Scene):
    def construct(self):
        title = Text("Perkin Condensation Reaction", font_size=50).to_edge(UP)
        self.play(Write(title))
        self.wait(1)

        # Reactants as plain text
        benzaldehyde = Text("C6H5CHO")
        acetic_acid = Text("CH3COOH")
        base = Text("NaOAc")
        plus1 = Text("+")
        plus2 = Text("+")
        arrow1 = Text("→")

        reactants = VGroup(benzaldehyde, plus1, acetic_acid, plus2, base, arrow1).arrange(RIGHT, buff=0.5).scale(1.2)
        reactants.next_to(title, DOWN, buff=1)
        self.play(FadeIn(reactants))
        self.wait(1)

        # Intermediate
        intermediate = Text("C6H5CH=C(COOH)CH3")
        intermediate.next_to(reactants, DOWN, buff=1)
        inter_label = Text("Intermediate", font_size=30).next_to(intermediate, DOWN)
        self.play(Write(intermediate), Write(inter_label))
        self.wait(1.5)

        # Product
        arrow2 = Text("→").next_to(intermediate, RIGHT, buff=1)
        product = Text("C6H5CH=CHCOOH").next_to(arrow2, RIGHT, buff=0.5)
        product_label = Text("Product", font_size=30).next_to(product, DOWN)
        self.play(Write(arrow2), Write(product), Write(product_label))
        self.wait(2)

        # Highlight intermediate
        self.play(Indicate(intermediate, scale_factor=1.2, color=YELLOW))
        self.wait(1)

        # Fade out
        self.play(*[FadeOut(mob) for mob in self.mobjects])
