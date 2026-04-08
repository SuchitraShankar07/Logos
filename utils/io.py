from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def read_text(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def write_json(data: Any) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False)


def load_prompt(path: str | Path, **kwargs: Any) -> str:
    template = Path(path).read_text(encoding="utf-8")
    if not kwargs:
        return template
    rendered = template
    for key, value in kwargs.items():
        rendered = rendered.replace(f"{{{key}}}", str(value))
    return rendered
