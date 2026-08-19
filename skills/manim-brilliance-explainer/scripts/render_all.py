import subprocess
import sys

SCENES = [
    # Base examples
    ("examples/derivative_tangent.py", "DerivativeInsight"),
    ("examples/matrix_transform.py", "MatrixTransform"),
    ("templates/cinematic_template.py", "CinematicTemplate"),
    # Topic scenes
    ("examples/topics/fourier_epicycles.py", "FourierEpicycles"),
    ("examples/topics/eigenvectors.py", "Eigenvectors"),
    ("examples/topics/neural_network.py", "NeuralNetwork"),
    ("examples/topics/calculus_trio.py", "RiemannToIntegral"),
    ("examples/topics/calculus_trio.py", "CircleToTriangle"),
    ("examples/topics/calculus_trio.py", "TangentAngle"),
    ("examples/topics/electromagnetism.py", "EMWave"),
    ("examples/topics/electromagnetism.py", "WireField"),
    # Technique gallery
    ("techniques/matching_transforms.py", "MatchingTransforms"),
    ("techniques/transform_from_copy.py", "TransformFromCopyDemo"),
    ("techniques/traced_path.py", "TracedPathDemo"),
    ("techniques/annotations_demo.py", "AnnotationsDemo"),
    ("techniques/updaters.py", "UpdatersDemo"),
    ("techniques/rate_functions_gallery.py", "RateFunctionsDemo"),
    ("techniques/complex_mapping.py", "ComplexMappingDemo"),
    ("techniques/surfaces_3d.py", "PotentialSurface"),
    ("techniques/choreography.py", "ChoreographyDemo"),
    ("techniques/homotopy.py", "HomotopyDemo"),
]

failed = []
for path, scene in SCENES:
    print(f"Rendering {scene} from {path}")
    result = subprocess.run([sys.executable, "-m", "manim", "-ql", path, scene])
    if result.returncode != 0:
        failed.append((path, scene))

if failed:
    print("Failed scenes:")
    for path, scene in failed:
        print(f"  {path} :: {scene}")
else:
    print("All scenes rendered.")
