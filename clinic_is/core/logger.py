from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_PATH = BASE_DIR / "logs" / "audit.log"


def audit_log(event_type: str, actor: str, details: str) -> None:
    entry: Dict[str, Any] = {
        "timestamp": datetime.utcnow().isoformat(),
        "event": event_type,
        "actor": actor,
        "details": details,
    }
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError:
        pass
