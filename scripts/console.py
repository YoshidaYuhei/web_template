#!/usr/bin/env python
"""
対話型コンソール

使い方:
    uv run python scripts/console.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# アプリケーションのimport
from sqlalchemy import text  # noqa: E402

from app.core.config import get_settings  # noqa: E402
from app.db.session import AsyncSessionLocal  # noqa: E402
from app.main import app  # noqa: E402

settings = get_settings()
db = AsyncSessionLocal()

if __name__ == "__main__":
    from IPython import embed

    embed(using="asyncio")
