"""
Base template for Manim DSA storytelling videos.
All 5 acts pre-implemented: Cold open → Brute force → Insight → Optimized → Payoff.
"""
from manim import *
import numpy as np

# ============================================================
# CONSTANTS — Dark Studio palette (from style-guide.md)
# ============================================================
DARK_BG    = "#0e0f12"
CUBE_COLOR = "#3a3f4b"
ACCENT     = "#f2a154"   # naive / brute-force color
GOOD       = "#5ad1a6"   # optimized / idiomatic color
PANEL_BG   = "#17181c"
WHITE      = "#ffffff"

SCENE_SHIFT = RIGHT * 3.0  # shift 3D space right so code panel fits on left


class TrickScene(ThreeDScene):
    """
    All trick scenes inherit this. Subclasses must define:
        NAIVE_CODE: str       # Python code string for naive/manual approach
        IDIOMATIC_CODE: str   # Python code string for idiomatic/optimized approach
        INPUT_DATA: list      # Example input data for the data space
        SOLID_TYPE: str       # One of: "cubes", "spheres", "cones", "surface", "torus"
        TITLE: str            # Video title
        INSIGHT_TEXT: str     # One-sentence hinge fact for Act 3
        bf_complexity: staticmethod returning f(t)  # naive complexity curve
        opt_complexity: staticmethod returning f(t) # optimized complexity curve
    """
    
    # Subclasses override these:
    NAIVE_CODE     = ""
    IDIOMATIC_CODE = ""
    INPUT_DATA     = []
    SOLID_TYPE     = "cubes"
    TITLE          = "Python Trick"
    INSIGHT_TEXT   = ""
    
    @staticmethod
    def bf_complexity(t): return t ** 2
    @staticmethod
    def opt_complexity(t): return t

    def construct(self):
        self.camera.background_color = DARK_BG
        
        # ---- ACT 1: Cold Open ----
        self.play_act1_cold_open()
        self.wait(0.3)
        
        # ---- ACT 2: Brute Force (Naive) ----
        self.play_act2_brute()
        self.wait(0.2)
        
        # ---- ACT 3: Insight ----
        self.play_act3_insight()
        self.wait(0.5)
        
        # ---- ACT 4: Optimized (Idiomatic) ----
        self.play_act4_optimized()
        self.wait(0.3)
        
        # ---- ACT 5: Payoff (Complexity Graph) ----
        self.play_act5_payoff()
        self.wait(1.5)

    # ========================================================
    # ACT 1: Cold Open — Problem as 3D Spatial Shape
    # ========================================================
    def play_act1_cold_open(self):
        # Title (fixed in frame as HUD)
        self.title = Text(self.TITLE, color=WHITE).scale(0.6)
        self.add_fixed_in_frame_mobjects(self.title)
        self.title.to_edge(UP)
        self.play(Write(self.title), run_time=1)
        
        # Camera orientation for 3D
        self.set_camera_orientation(phi=65 * DEGREES, theta=-60 * DEGREES)
        
        # Build data space (axes + solids + labels)
        self.axes, self.solids, self.labels = self.make_data_space(
            self.INPUT_DATA, self.SOLID_TYPE
        )
        self.axes.shift(SCENE_SHIFT)
        self.solids.shift(SCENE_SHIFT)
        self.labels.shift(SCENE_SHIFT)
        
        self.play(Create(self.axes), run_time=1)
        self.play(
            LaggedStart(*[FadeIn(s, shift=UP * 0.3) for s in self.solids], lag_ratio=0.1),
            run_time=1.5
        )
        self.play(
            LaggedStart(*[FadeIn(l) for l in self.labels], lag_ratio=0.1),
            run_time=1
        )

    # ========================================================
    # ACT 2: Brute Force / Naive Approach
    # ========================================================
    def play_act2_brute(self):
        # Label
        bf_label = Text("Naive / Manual  O(n\u00b2)", color=ACCENT).scale(0.45)
        self.add_fixed_in_frame_mobjects(bf_label)
        bf_label.to_corner(UL).shift(DOWN * 0.7)
        
        # Code panel (fixed in frame, left side)
        self.bf_code = Code(
            code_string=self.NAIVE_CODE,
            language="python",
            formatter_style="native",
            background="window",
            add_line_numbers=True,
            paragraph_config={"font_size": 14}
        )
        self.add_fixed_in_frame_mobjects(self.bf_code)
        self.bf_code.scale(0.5).to_edge(LEFT, buff=0.3).shift(DOWN * 0.3)
        
        self.play(FadeIn(bf_label), FadeIn(self.bf_code), run_time=0.5)
        
        # Synced highlight - safe indexing (use .submobjects for Paragraph)
        first_line_idx = 0 if len(self.bf_code.code_lines.submobjects) == 0 else min(1, len(self.bf_code.code_lines.submobjects) - 1)
        self.bf_hl = SurroundingRectangle(
            self.bf_code.code_lines.submobjects[first_line_idx],
            color=ACCENT, buff=0.05
        )
        self.add_fixed_in_frame_mobjects(self.bf_hl)
        self.play(Create(self.bf_hl), run_time=0.3)
        
        # Particle + trail
        self.bf_particle = Dot3D(radius=0.07, color=ACCENT)
        self.bf_particle.move_to(self._get_start_pos())
        self.bf_trail = TracedPath(
            self.bf_particle.get_center,
            stroke_color=ACCENT, stroke_width=1.5, stroke_opacity=0.5
        )
        self.add(self.bf_trail, self.bf_particle)
        
        # Run the naive logic (subclass implements _run_naive())
        self._run_naive()
        
        # Clean up
        self.play(
            FadeOut(bf_label), FadeOut(self.bf_code), FadeOut(self.bf_hl),
            FadeOut(self.bf_trail), FadeOut(self.bf_particle),
            run_time=0.5
        )

    # ========================================================
    # ACT 3: Insight
    # ========================================================
    def play_act3_insight(self):
        insight = Text(self.INSIGHT_TEXT, color=WHITE).scale(0.4)
        self.add_fixed_in_frame_mobjects(insight)
        insight.to_edge(DOWN)
        self.play(Write(insight), run_time=1)
        self.wait(1.5)
        self.play(FadeOut(insight), run_time=0.5)

    # ========================================================
    # ACT 4: Optimized / Idiomatic Approach
    # ========================================================
    def play_act4_optimized(self):
        opt_label = Text("Idiomatic Python  O(n)", color=GOOD).scale(0.45)
        self.add_fixed_in_frame_mobjects(opt_label)
        opt_label.to_corner(UL).shift(DOWN * 0.7)
        
        self.opt_code = Code(
            code_string=self.IDIOMATIC_CODE,
            language="python",
            formatter_style="native",
            background="window",
            add_line_numbers=True,
            paragraph_config={"font_size": 14}
        )
        self.add_fixed_in_frame_mobjects(self.opt_code)
        self.opt_code.scale(0.5).to_edge(LEFT, buff=0.3).shift(DOWN * 0.2)
        
        self.play(FadeIn(opt_label), FadeIn(self.opt_code), run_time=0.5)
        
        self.opt_hl = SurroundingRectangle(
            self.opt_code.code_lines.submobjects[0] if len(self.opt_code.code_lines.submobjects) == 0 else self.opt_code.code_lines.submobjects[min(1, len(self.opt_code.code_lines.submobjects) - 1)],
            color=GOOD, buff=0.05
        )
        self.add_fixed_in_frame_mobjects(self.opt_hl)
        self.play(Create(self.opt_hl), run_time=0.3)
        
        self.opt_particle = Dot3D(radius=0.07, color=GOOD)
        self.opt_particle.move_to(self._get_start_pos())
        self.opt_trail = TracedPath(
            self.opt_particle.get_center,
            stroke_color=GOOD, stroke_width=3, stroke_opacity=0.9
        )
        self.add(self.opt_trail, self.opt_particle)
        
        # Run the optimized logic (subclass implements _run_optimized())
        self._run_optimized()
        
        # Clean up
        self.play(
            FadeOut(opt_label), FadeOut(self.opt_code), FadeOut(self.opt_hl),
            FadeOut(self.opt_trail), FadeOut(self.opt_particle),
            run_time=0.5
        )

    # ========================================================
    # ACT 5: Payoff — Complexity Graph
    # ========================================================
    def play_act5_payoff(self):
        # Camera to top-down for 2D graph
        self.move_camera(phi=0, theta=-90 * DEGREES, run_time=0.5)
        self.play(
            FadeOut(self.axes), FadeOut(self.solids),
            FadeOut(self.labels), FadeOut(self.title),
            run_time=0.5
        )
        
        # 2D Axes for complexity graph
        graph_axes = Axes(
            x_range=[0, 20, 5],
            y_range=[0, 400, 50],
            x_length=7, y_length=4,
            axis_config={"color": WHITE}
        ).to_edge(DOWN, buff=0.8)
        
        x_label = graph_axes.get_x_axis_label("n").scale(0.6)
        y_label = graph_axes.get_y_axis_label("operations").scale(0.6)
        
        # True complexity curves — Axes.plot calls fn(t) with parameter t
        bf_curve = graph_axes.plot(
            lambda t: self.bf_complexity(t), x_range=[0, 20], color=ACCENT
        )
        opt_curve = graph_axes.plot(
            lambda t: self.opt_complexity(t), x_range=[0, 20], color=GOOD
        )
        
        bf_tag = Text("naive O(n\u00b2)", color=ACCENT).scale(0.4).next_to(bf_curve, UR, buff=0.1)
        opt_tag = Text("idiomatic O(n)", color=GOOD).scale(0.4).next_to(opt_curve.get_end(), UP, buff=0.15)
        
        self.play(Create(graph_axes), Write(x_label), Write(y_label), run_time=1)
        self.play(Create(bf_curve), Write(bf_tag), run_time=1.2)
        self.play(Create(opt_curve), Write(opt_tag), run_time=1.2)

    # ========================================================
    # HELPER METHODS (can be overridden by subclasses)
    # ========================================================
    
    def make_data_space(self, data, solid_type):
        """Build axes + solids + labels for the given data and solid type."""
        n = len(data)
        
        # Try to compute numeric y_range; fall back to fixed range for non-numeric data
        try:
            numeric_data = [float(d) for d in data]
            y_min = min(numeric_data) * 1.2
            y_max = max(numeric_data) * 1.2
        except (ValueError, TypeError):
            y_min, y_max = -2, 2
        
        # 3D Axes
        axes = ThreeDAxes(
            x_range=[0, n, 1],
            y_range=[y_min, y_max, 1],
            z_range=[-4, 4, 1],
            x_length=max(6, n * 0.8),
            y_length=4,
            z_length=3
        )
        
        solids = VGroup()
        labels = VGroup()
        
        if solid_type == "cubes":
            for i, val in enumerate(data):
                h = max(abs(val) * 0.25, 0.25) if isinstance(val, (int, float)) else 0.5
                c = Cube(side_length=0.5, fill_color=CUBE_COLOR, fill_opacity=0.9, stroke_color=WHITE)
                c.stretch_to_fit_height(h)
                c.move_to(axes.c2p(i + 0.5, 0, 0))
                c.shift(UP * h / 2)
                solids.add(c)
                
                lbl = Text(str(val), color=WHITE).scale(0.35)
                lbl.rotate(90 * DEGREES, axis=RIGHT)  # stand upright, not flat on floor
                lbl.next_to(c, DOWN, buff=0.12)
                labels.add(lbl)
                
        elif solid_type == "spheres":
            for i, val in enumerate(data):
                s = Sphere(radius=0.3, fill_color=CUBE_COLOR, fill_opacity=0.8, resolution=(16, 16))
                s.move_to(axes.c2p(i + 0.5, 0, np.random.uniform(-1, 1)))
                solids.add(s)
                lbl = Text(str(val), color=WHITE).scale(0.3)
                lbl.rotate(90 * DEGREES, axis=RIGHT)
                lbl.next_to(s, DOWN, buff=0.1)
                labels.add(lbl)
                
        elif solid_type == "cones":
            for i, val in enumerate(data):
                h = max(abs(val) * 0.3, 0.3) if isinstance(val, (int, float)) else 0.5
                c = Cone(base_radius=0.3, height=h, fill_color=CUBE_COLOR, fill_opacity=0.9)
                c.move_to(axes.c2p(i + 0.5, 0, 0))
                c.shift(UP * h / 2)
                solids.add(c)
                lbl = Text(str(val), color=WHITE).scale(0.3)
                lbl.rotate(90 * DEGREES, axis=RIGHT)
                lbl.next_to(c, DOWN, buff=0.1)
                labels.add(lbl)
                
        elif solid_type == "surface":
            # For 2D grid / DP table
            pass  # Implement if needed
            
        elif solid_type == "torus":
            # For cyclic structures
            pass  # Implement if needed
        
        return axes, solids, labels

    def _get_start_pos(self):
        """Starting position for particle (top of first solid)."""
        if len(self.solids) > 0:
            return self.solids[0].get_top()
        return ORIGIN

    # ========================================================
    # ABSTRACT METHODS — SUBCLASSES MUST IMPLEMENT
    # ========================================================
    
    def _run_naive(self):
        """Animate the naive/manual approach with synced code highlights.
        Move bf_particle, update bf_hl to track code lines.
        """
        raise NotImplementedError("Subclass must implement _run_naive()")
    
    def _run_optimized(self):
        """Animate the idiomatic approach with synced code highlights.
        Move opt_particle, update opt_hl to track code lines.
        """
        raise NotImplementedError("Subclass must implement _run_optimized()")


if __name__ == "__main__":
    pass