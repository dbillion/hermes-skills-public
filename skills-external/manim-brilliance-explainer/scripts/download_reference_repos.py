import subprocess
from pathlib import Path

REPOS = [
    ("https://github.com/3b1b/manim.git", "grant-manim"),
    ("https://github.com/ManimCommunity/manim.git", "community-manim"),
]

for url, folder in REPOS:
    if Path(folder).exists():
        print(f"{folder} already exists, skipping.")
        continue

    print(f"Cloning {url} into {folder}...")
    subprocess.run(["git", "clone", "--depth=1", url, folder], check=False)

print("Done.")
