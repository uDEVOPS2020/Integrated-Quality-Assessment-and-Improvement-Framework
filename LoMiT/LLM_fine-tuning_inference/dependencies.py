import subprocess

dependencies = [
    "datasets", "transformers", "evaluate", "accelerate",
    "sacrebleu", "torch", "git-lfs", "Levenshtein", "huggingface_hub"
]

for dep in dependencies:
    subprocess.run(["pip", "install", dep])
