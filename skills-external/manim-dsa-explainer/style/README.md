# Reference style helpers

Reference implementation of the shared helpers `SKILL.md` assumes exist in
your target project's scene module. Copy/adapt into your own repo's scenes
directory rather than importing across repos.

- `dsa_style.py` -- palette, `make_cube_row`, `code_panel`, `make_highlight`,
  `complexity_payoff` graph, fixed-in-frame title, and **`test_panel()`** --
  the Act 6 "verified by test" helper. This is the one every scene must call.
- `graph_tree_style.py` -- `make_graph`, `make_tree`, `make_vertical_stack`.
- `shapes3d.py` -- the extended solid vocabulary: `make_cylinder_queue`,
  `make_ring`, `make_cone_pointer`, `make_min_heap_tree`, `make_split_wedge`,
  `make_prism_grid`.
