from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

DATA_DIR = Path(os.getenv("DATA_DIR", "data"))
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-4o")
