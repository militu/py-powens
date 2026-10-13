"""Prove the declared Python minimum and the installed distribution."""

from __future__ import annotations

import os
import re
import subprocess
import tempfile
import tomllib
from pathlib import Path

metadata = tomllib.loads(Path("pyproject.toml").read_text())
requirement = metadata["project"]["requires-python"]
match = re.match(r">=(\d+\.\d+)(?:\.\d+)?(?:$|,)", requirement)
if match is None:
    raise SystemExit(f"Declare how to test the Python minimum: {requirement}")
minimum = match.group(1)
current = Path(".python-version").read_text().strip()
wheels = list(Path("dist").glob("*.whl"))
if len(wheels) != 1:
    raise SystemExit("Build exactly one wheel before checking compatibility")

# Reuse the quality suite already run on the current interpreter. Only the
# additional compatibility interpreter gets a second suite, in its own venv.
if not current.startswith(f"{minimum}."):
    with tempfile.TemporaryDirectory(prefix="powens-compat-") as environment:
        variables = {**os.environ, "UV_PROJECT_ENVIRONMENT": environment}
        variables.pop("VIRTUAL_ENV", None)
        command = ["uv", "run", "--locked", "--python", minimum]
        subprocess.run([*command, "python", "--version"], env=variables, check=True)
        subprocess.run([*command, "pytest", "-q"], env=variables, check=True)

for interpreter in dict.fromkeys([minimum, current]):
    subprocess.run(
        [
            "uv",
            "run",
            "--isolated",
            "--no-project",
            "--python",
            interpreter,
            "--with",
            str(wheels[0].resolve()),
            "python",
            "-I",
            "-c",
            "import powens",
        ],
        check=True,
    )
