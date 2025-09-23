from manim import *

class SilverMirrorTest(ThreeDScene):
    def construct(self):
        # Scene 1: Title + Silver Nitrate
        title = Text("Silver Mirror Test").scale(1.5).to_edge(UP)
        self.play(FadeIn(title))
        self.wait(1)

        silver_solution = Sphere(radius=0.5, fill_opacity=1, fill_color="#c0c0c0")
        label1 = Text("Ag(NH3)2+ solution", font_size=24).next_to(silver_solution, DOWN)
        aldehyde = Cube(side_length=0.3, fill_opacity=0.7, fill_color="#FFD700").next_to(silver_solution, RIGHT, buff=0.5)

        self.play(Create(silver_solution), Write(label1), Create(aldehyde))
        self.wait(2)
        self.play(FadeOut(title))

        # Scene 2: Aldehyde rotates + reaction
        self.play(Rotate(aldehyde, angle=PI, axis=[0,1,0]))
        reaction_text = Text("R-CHO + Ag(NH3)2+ -> R-COO- + Ag + NH3", font_size=24).next_to(silver_solution, DOWN, buff=0.5)
        self.play(Write(reaction_text))
        self.wait(3)

        # Scene 3: Silver mirror forms
        test_tube = Cylinder(radius=0.6, height=1.5, fill_opacity=0.3, fill_color="#a0a0a0").next_to(silver_solution, DOWN, buff=0.5)
        silver_mirror = Cylinder(radius=0.5, height=0.2, fill_opacity=0.9, fill_color="#c0c0c0").move_to(silver_solution)

        self.play(FadeIn(test_tube), Transform(silver_solution, silver_mirror), FadeOut(aldehyde, reaction_text))
        self.wait(2)

        # Scene 4: Positive result
        positive_result = Text("Positive Result!", font_size=36).to_edge(UP)
        self.play(Write(positive_result))
        self.wait(2)

        # Scene 5: Optional: Add automatic scaling of multiple objects
        # (example with 3 spheres)
        spheres = VGroup(*[Sphere(radius=0.3, fill_color=color).shift(RIGHT*i) for i, color in enumerate(["#FF0000","#00FF00","#0000FF"])])
        for i, s in enumerate(spheres):
            self.play(Create(s))
        self.wait(2)

