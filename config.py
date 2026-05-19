from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

DATA_DIR = Path(os.getenv("DATA_DIR", "data"))
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-4o")

# Directory that contains .github/agents, .github/skills, etc.
# Can be overridden per-command with --workspace flag.
WORKSPACE_DIR = Path(os.getenv("WORKSPACE_DIR", "."))
GITHUB_DIR = WORKSPACE_DIR / ".github"

