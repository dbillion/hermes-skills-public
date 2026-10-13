#!/usr/bin/env python3
"""
Scene generator for Manim DSA video pipeline.
Reads references/tricks.yaml and generates all scene files with correct structure.
"""
import os
import yaml

def main():
    scene_dir = os.path.dirname(os.path.dirname(__file__))
    yaml_path = os.path.join(scene_dir, "references", "tricks.yaml")
    
    with open(yaml_path, 'r') as f:
        config = yaml.safe_load(f)
    
    tricks = config.get("tricks", [])
    
    template = '''"""
{title}
"""
from manim import *
from template import TrickScene


class {class_name}(TrickScene):
    TITLE = "{title}"
    SOLID_TYPE = "{solid_type}"
    INPUT_DATA = {input_data}
    INSIGHT_TEXT = "{insight_text}"
    
    NAIVE_CODE = """{naive_code}"""
    
    IDIOMATIC_CODE = """{idiomatic_code}"""
    
    @staticmethod
    def bf_complexity(t):
        return {bf_complexity_body}
    
    @staticmethod
    def opt_complexity(t):
        return {opt_complexity_body}

    def _run_naive(self):
        lines = self.bf_code.code_lines.submobjects
        n = len(lines)
        for i in range(min(n, {naive_lines})):
            self.play(self.bf_hl.animate.move_to(lines[i]), run_time=0.3)
        self.wait(0.5)

    def _run_optimized(self):
        lines = self.opt_code.code_lines.submobjects
        n = len(lines)
        for i in range(min(n, {opt_lines})):
            self.play(self.opt_hl.animate.move_to(lines[i]), run_time=0.3)
        self.wait(0.5)


if __name__ == "__main__":
    pass
'''

    for trick in tricks:
        fname = f"trick_{trick['id'].zfill(2)}_{trick['name'].lower().replace(' ', '_')}.py"
        class_name = "Trick" + "".join(word.capitalize() for word in trick['name'].split())
        
        # Extract body from lambda expressions
        bf_body = trick['bf_complexity'].replace("lambda t: ", "").replace("lambda x: ", "")
        opt_body = trick['opt_complexity'].replace("lambda t: ", "").replace("lambda x: ", "")
        
        content = template.format(
            title=trick['title'],
            class_name=class_name,
            solid_type=trick['solid_type'],
            input_data=trick['input_data'],
            insight_text=trick['insight_text'],
            naive_code=trick['naive_code'],
            idiomatic_code=trick['idiomatic_code'],
            bf_complexity_body=bf_body,
            opt_complexity_body=opt_body,
            naive_lines=trick['naive_lines'],
            opt_lines=trick['opt_lines'],
        )
        
        path = os.path.join(scene_dir, fname)
        with open(path, 'w') as fp:
            fp.write(content)
        
        print(f"Generated: {fname}")

    print(f"\nAll {len(tricks)} scene files generated in {scene_dir}")

if __name__ == "__main__":
    main()