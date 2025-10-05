# =================================================================
# Zener Diode Animation - Manim v0.19.0 Compatible
# =================================================================

from manim import *
import numpy as np

class ZenerDiodeScene(Scene):
    CONFIG = {
        "zener_voltage": 5.1,
        "forward_voltage": 0.7,
        "p_color": BLUE,
        "n_color": RED,
        "depletion_color": GREY_BROWN,
        "electron_color": RED,
        "hole_color": BLUE,
        "circuit_color": WHITE,
        "arrow_color": YELLOW,
    }

    def construct(self):
        self.introduce_concept()
        self.unbiased_state()
        self.forward_bias_state()
        self.reverse_bias_and_breakdown()
        self.show_vi_characteristics_and_application()
        self.wait(3)

    # -------------------- Helper Methods --------------------
    def introduce_concept(self):
        title = Title("The Zener Diode")

        cathode = Line(LEFT, RIGHT).scale(0.5)
        anode_line = Line(LEFT, ORIGIN).scale(0.5)
        z_part1 = Line(0.2*RIGHT + 0.2*UP, ORIGIN)
        z_part2 = Line(0.2*LEFT - 0.2*DOWN, ORIGIN)
        z_symbol_end = VGroup(z_part1, z_part2).shift(0.25*RIGHT)

        anode = Polygon(LEFT, 0.5*UP, 0.5*DOWN, color=self.CONFIG["circuit_color"], fill_opacity=1).scale(0.5).shift(0.25*LEFT)
        symbol = VGroup(anode, anode_line, cathode, z_symbol_end).move_to(ORIGIN).scale(2)

        anode_label = MathTex("A").next_to(symbol, LEFT, buff=0.5)
        cathode_label = MathTex("K").next_to(symbol, RIGHT, buff=0.5)

        description = Tex("A special diode designed to operate in reverse breakdown.").next_to(symbol, DOWN, buff=1)

        self.play(Write(title))
        self.play(Create(symbol), Write(anode_label), Write(cathode_label))
        self.play(Write(description))
        self.wait(2)
        self.play(FadeOut(title, symbol, anode_label, cathode_label, description))

    def unbiased_state(self):
        subtitle = Title("Unbiased Condition")

        p_region = Rectangle(width=4, height=3, color=self.CONFIG["p_color"], fill_opacity=0.7).shift(2*LEFT)
        n_region = Rectangle(width=4, height=3, color=self.CONFIG["n_color"], fill_opacity=0.7).shift(2*RIGHT)
        p_label = Tex("P-Type").move_to(p_region.get_center() + 1*UP)
        n_label = Tex("N-Type").move_to(n_region.get_center() + 1*UP)

        depletion_region = Rectangle(width=2, height=3, color=self.CONFIG["depletion_color"], fill_opacity=0.8)
        depletion_label = Tex("Depletion Region", font_size=36).next_to(depletion_region, DOWN)

        self.play(Write(subtitle))
        self.play(FadeIn(p_region, n_region), Write(p_label), Write(n_label))
        self.play(Create(depletion_region), Write(depletion_label))

        barrier_arrow = DoubleArrow(LEFT, RIGHT, color=self.CONFIG["arrow_color"]).move_to(depletion_region.get_center()+1*UP)
        barrier_text = MathTex("V_{barrier}").next_to(barrier_arrow, UP)
        self.play(GrowArrow(barrier_arrow), Write(barrier_text))
        self.wait(2)

        self.junction_group = VGroup(p_region, n_region, p_label, n_label, depletion_region, depletion_label, barrier_arrow, barrier_text)
        self.play(FadeOut(subtitle), self.junction_group.animate.scale(0.7).to_edge(UP))

    def forward_bias_state(self):
        subtitle = Tex("Forward Bias (> 0.7V)").to_edge(DOWN)

        plus = Tex("+").scale(1.5).shift(5*LEFT)
        minus = Tex("-").scale(2).shift(5*RIGHT)  # ✅ Fixed minus

        wire1 = Line(self.junction_group[0].get_left(), plus.get_right())
        wire2 = Line(self.junction_group[1].get_right(), minus.get_left())
        circuit = VGroup(wire1, wire2, plus, minus)

        self.play(Write(subtitle), Create(circuit))

        self.play(
            self.junction_group[4].animate.set_width(0.2),
            self.junction_group[6].animate.set_width(0.2),
            FadeOut(self.junction_group[7], self.junction_group[5])
        )

        holes = VGroup(*[Dot(color=self.CONFIG["hole_color"]) for _ in range(5)]).arrange(RIGHT, buff=0.5).move_to(wire1.get_center())
        electrons = VGroup(*[Dot(color=self.CONFIG["electron_color"]) for _ in range(5)]).arrange(LEFT, buff=0.5).move_to(wire2.get_center())
        current_arrow = Arrow(3*LEFT, 3*RIGHT, color=self.CONFIG["arrow_color"], buff=0).next_to(self.junction_group, DOWN, buff=1)
        current_label = MathTex("I_{\\text{Conventional}}").next_to(current_arrow, DOWN)

        self.play(
            MoveAlongPath(holes, Line(wire1.get_start(), wire1.get_end())),
            MoveAlongPath(electrons, Line(wire2.get_start(), wire2.get_end())),
            Create(current_arrow), Write(current_label),
            run_time=3
        )
        self.wait(2)

        self.play(FadeOut(subtitle, circuit, holes, electrons, current_arrow, current_label))
        self.play(self.junction_group[4].animate.set_width(2), self.junction_group[6].animate.set_width(2), FadeIn(self.junction_group[5]))

    def reverse_bias_and_breakdown(self):
        subtitle = Tex("Reverse Bias").to_edge(DOWN)

        plus = Tex("+").scale(1.5).shift(5*RIGHT)
        minus = Tex("-").scale(2).shift(5*LEFT)  # ✅ Fixed minus

        wire1 = Line(self.junction_group[0].get_left(), minus.get_right())
        wire2 = Line(self.junction_group[1].get_right(), plus.get_left())
        circuit = VGroup(wire1, wire2, plus, minus)
        self.play(Write(subtitle), Create(circuit))

        self.play(self.junction_group[4].animate.set_width(4), self.junction_group[6].animate.set_width(4))
        self.wait(2)

        breakdown_title = Tex(f"Reverse Voltage > {self.CONFIG['zener_voltage']}V (Zener Breakdown)").to_edge(DOWN)
        self.play(ReplacementTransform(subtitle, breakdown_title))

        field_lines = VGroup(*[Arrow(UP, DOWN, color=YELLOW, max_tip_length_to_length_ratio=0.1) for _ in range(10)]).arrange(RIGHT, buff=0.3).move_to(self.junction_group[4])
        self.play(Create(field_lines))

        pairs = VGroup()
        for _ in range(15):
            pair_center = self.junction_group[4].get_center() + np.array([np.random.uniform(-1.5, 1.5), np.random.uniform(-1, 1), 0])
            e = Dot(pair_center + 0.1*LEFT, color=self.CONFIG["electron_color"], radius=0.05)
            h = Dot(pair_center + 0.1*RIGHT, color=self.CONFIG["hole_color"], radius=0.05)
            pairs.add(VGroup(e, h))

        self.play(LaggedStart(*[FadeIn(p) for p in pairs], lag_ratio=0.1))

        avalanche = VGroup(*[p.copy() for p in pairs])
        self.play(
            LaggedStart(*[p[0].animate.shift(4*RIGHT) for p in avalanche], lag_ratio=0.05),
            LaggedStart(*[p[1].animate.shift(4*LEFT) for p in avalanche], lag_ratio=0.05),
            run_time=4
        )
        self.wait(2)

        self.play(FadeOut(self.junction_group, breakdown_title, circuit, field_lines, pairs, avalanche))

    def show_vi_characteristics_and_application(self):
        title = Title("V-I Characteristics and Application")
        self.play(Write(title))

        axes = Axes(
            x_range=[-8, 2, 2],
            y_range=[-10, 10, 5],
            x_length=10,
            y_length=6,
            axis_config={"include_numbers": True},
        )
        labels = axes.get_axis_labels(x_label="V", y_label="I (mA)")
        self.play(Create(axes), Write(labels))

        zv = self.CONFIG["zener_voltage"]
        fv = self.CONFIG["forward_voltage"]

        # Forward Bias curve
        forward_curve = axes.plot(lambda x: 10*(np.exp(2.5*(x-fv))-1), x_range=[fv, 1], color=YELLOW)
        # Reverse bias linear curve
        reverse_curve = axes.plot(lambda x: 0.1*x, x_range=[-zv, 0], color=YELLOW)
        # Breakdown
        breakdown_curve = axes.plot(lambda x: -9, x_range=[-zv, -zv+0.01], color=RED)

        self.play(Create(forward_curve), Create(reverse_curve))
        self.play(Create(breakdown_curve), run_time=2)

        zener_label = MathTex(f"V_Z = {zv}V").next_to(axes.c2p(-zv, -5), LEFT)
        forward_label = Tex("Forward Bias").next_to(axes.c2p(1, 5), UR)
        self.play(Write(zener_label), Write(forward_label))
        self.wait(2)

        self.play(
            VGroup(axes, labels, forward_curve, reverse_curve, breakdown_curve, zener_label, forward_label).animate.scale(0.6).to_edge(LEFT)
        )

        vin = MathTex("V_{\\text{in}} \\text{ (unregulated)}").shift(4*RIGHT + 2*UP)
        resistor = Tex("Resistor").shift(4*RIGHT + 0.7*UP)
        zener = Tex("Zener Diode").shift(4*RIGHT - 0.7*UP)
        vout = MathTex("V_{\\text{out}} = V_Z \\text{ (regulated)}").shift(4*RIGHT - 2*UP)

        circuit_text = VGroup(vin, resistor, zener, vout).arrange(DOWN, buff=0.7)
        self.play(Write(circuit_text))
        self.wait(2)
