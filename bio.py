from manim import *

class DNAStrand(VGroup):
    """A VGroup representing a single strand of DNA."""
    def __init__(self, sequence, direction=UP, **kwargs):
        super().__init__(**kwargs)
        self.sequence = sequence
        self.direction = direction
        self.colors = {'A': BLUE, 'T': GREEN, 'G': GOLD, 'C': RED}
        self.build_strand()

    def build_strand(self):
        """Builds the visual representation of the DNA strand."""
        bases = VGroup()
        for letter in self.sequence:
            base = self.create_base(letter)
            bases.add(base)
        bases.arrange(self.direction, buff=0.2)
        self.add(bases)
        self.bases = bases

    def create_base(self, letter):
        """Creates a single nucleotide base."""
        color = self.colors.get(letter, WHITE)
        base = Square(side_length=0.4, fill_color=color, fill_opacity=1, stroke_width=0)
        label = Text(letter, font_size=20, weight=BOLD).move_to(base.get_center())
        return VGroup(base, label)

class DNAReplication(Scene):
    """An animation of the DNA replication process."""
    def construct(self):
        # --- SCENE SETUP ---
        title = Title("DNA Replication").to_edge(UP)
        self.add(title)

        # --- CREATE PARENT DNA ---
        parent_seq_top = "ATGCCGAT"
        parent_seq_bottom = "TACGGCTA"

        parent_strand_top = DNAStrand(parent_seq_top).shift(UP * 0.5)
        parent_strand_bottom = DNAStrand(parent_seq_bottom).shift(DOWN * 0.5)

        parent_dna = VGroup(parent_strand_top, parent_strand_bottom).center()
        self.play(FadeIn(parent_dna))
        self.wait(1)

        # --- HELICASE UNWINDS DNA ---
        helicase = Triangle(fill_color=ORANGE, fill_opacity=1).scale(0.5).rotate(-PI/2)
        helicase.next_to(parent_dna.get_left(), buff=-0.1)
        helicase_label = Text("Helicase", font_size=24).next_to(helicase, DOWN)

        self.play(FadeIn(helicase), Write(helicase_label))
        self.wait(0.5)

        # Animate unwinding
        self.play(
            helicase.animate.move_to(parent_dna.get_right() + RIGHT*0.1),
            parent_strand_top.animate.shift(UP*1.5),
            parent_strand_bottom.animate.shift(DOWN*1.5),
            run_time=3
        )
        self.wait(1)
        self.play(FadeOut(helicase), FadeOut(helicase_label))

        # --- LEADING STRAND SYNTHESIS ---
        leading_strand_label = Text("Leading Strand", font_size=28).to_edge(UP, buff=1.5).align_to(parent_strand_top, LEFT)
        dna_polymerase_leading = Circle(radius=0.3, color=PINK, fill_opacity=1)
        dna_polymerase_leading.move_to(parent_strand_bottom.get_left() + UP * 0.7)

        new_strand_leading_seq = parent_seq_top
        new_strand_leading = DNAStrand(new_strand_leading_seq)
        new_strand_leading.next_to(parent_strand_bottom, UP, buff=0.1)
        new_strand_leading.set_opacity(0) # Initially invisible

        self.play(Write(leading_strand_label), FadeIn(dna_polymerase_leading))

        # Animate polymerase and new strand creation
        self.play(
            dna_polymerase_leading.animate.move_to(parent_strand_bottom.get_right() + UP * 0.7),
            new_strand_leading.animate.set_opacity(1),
            run_time=3
        )
        self.play(FadeOut(dna_polymerase_leading))
        self.wait(1)

        # --- LAGGING STRAND SYNTHESIS ---
        lagging_strand_label = Text("Lagging Strand (Okazaki Fragments)", font_size=28).to_edge(DOWN, buff=1.5).align_to(parent_strand_top, LEFT)
        self.play(Write(lagging_strand_label))

        dna_polymerase_lagging = Circle(radius=0.3, color=PURPLE, fill_opacity=1)
        new_strand_lagging_seq = parent_seq_bottom
        
        # Animate synthesis in fragments
        fragments = VGroup()
        
        for i in range(len(new_strand_lagging_seq) - 1, -1, -2):
            fragment_seq = new_strand_lagging_seq[max(0, i-1):i+1]
            fragment = DNAStrand(fragment_seq)
            
            original_bases = parent_strand_top.bases[max(0, i-1):i+1]
            fragment.next_to(VGroup(*original_bases), DOWN, buff=0.1)
            
            dna_polymerase_lagging.move_to(fragment.get_right() + UP * 0.2)
            
            self.play(FadeIn(dna_polymerase_lagging))
            self.play(
                dna_polymerase_lagging.animate.move_to(fragment.get_left() + UP*0.2),
                Create(fragment),
                run_time=1.5
            )
            self.play(FadeOut(dna_polymerase_lagging))
            fragments.add(fragment)

        self.wait(2)

        # --- FINAL SCENE ---
        final_text = Text("Replication Complete: Two DNA Molecules Formed", font_size=32).to_edge(DOWN)
        self.play(
            FadeOut(leading_strand_label, lagging_strand_label),
            VGroup(parent_strand_bottom, new_strand_leading).animate.shift(DOWN*1.5),
            VGroup(parent_strand_top, fragments).animate.shift(UP*1.5)
        )
        self.play(Write(final_text))
        self.wait(3)