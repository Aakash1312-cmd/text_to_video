from manim import *

# helper requested by user
def safe_angle(line1, line2, **kwargs):
    try:
        return Angle(line1, line2, **kwargs)
    except ValueError:
        return None

class GeneratedStoryboardScene(Scene):
    def construct(self):

        # small helper utilities to interpret visual_instructions strings
        def _pos(tok):
            mapping = {
                'LEFT': LEFT, 'RIGHT': RIGHT, 'UP': UP, 'DOWN': DOWN, 'ORIGIN': ORIGIN,
                'UL': UP+LEFT, 'UR': UP+RIGHT, 'DL': DOWN+LEFT, 'DR': DOWN+RIGHT
            }
            return mapping.get(tok.upper(), ORIGIN)

        def _label(mob, text):
            lbl = Text(text).next_to(mob, DOWN)
            return lbl

        # Frame 0
        if self.mobjects:
            self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.3)
        t0 = Triangle().shift(UP)
        mt0 = MathTex("e^{i\\pi} + 1 = 0").to_edge(UP)
        lbl0 = Text('a').next_to(t0, DOWN)
        self.play(Create(t0), Create(lbl0))
        self.add_sound(r'audio_frame_0.wav')
        self.wait(5.0)
        if self.mobjects:
            self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.2)

        # Frame 1
        if self.mobjects:
            self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.3)
        r1 = Rectangle(width=1.5, height=1).shift(DOWN)
        t1 = Triangle().shift(UP)
        mt1 = MathTex("e^{i\\pi} + 1 = 0").to_edge(UP)
        lbl1 = Text('the').next_to(r1, DOWN)
        self.play(Create(r1), Create(lbl1))
        self.add_sound(r'audio_frame_1.wav')
        self.wait(6.0)
        if self.mobjects:
            self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.2)

        # Frame 2
        if self.mobjects:
            self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.3)
        r2 = Rectangle(width=1.5, height=1).shift(DOWN)
        self.play(Create(r2))
        self.add_sound(r'audio_frame_2.wav')
        self.wait(8.0)
        if self.mobjects:
            self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.2)

        # Frame 3
        if self.mobjects:
            self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.3)
        mt3 = MathTex("e^{i\\pi} + 1 = 0").to_edge(UP)
        self.play(Create(mt3))
        self.add_sound(r'audio_frame_3.wav')
        self.wait(5.0)
        if self.mobjects:
            self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.2)
