import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).parent

_SESSION_ID = uuid.uuid4().hex[:8]
_SESSION_DIR = BASE_DIR / "sessions" / _SESSION_ID
_SESSION_DIR.mkdir(parents=True, exist_ok=True)

# Output og log mappe for denne session
OUTPUT_DIR = _SESSION_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

_LOG_FILE = _SESSION_DIR / "log.jsonl"


def get_output_dir() -> Path:
    return OUTPUT_DIR


def get_session_id() -> str:
    return _SESSION_ID


def log_tool_call(tool_name: str, tool_input: dict, tool_result) -> None:
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "session_id": _SESSION_ID,
        "tool": tool_name,
        "input": tool_input,
        "result": tool_result if isinstance(tool_result, (dict, list)) else str(tool_result)
    }
    with _LOG_FILE.open("a") as f:
        f.write(json.dumps(record, default=str) + "\n")


def get_session_log() -> list[dict]:
    if not _LOG_FILE.exists():
        return []
    with _LOG_FILE.open() as f:
        return [json.loads(line) for line in f if line.strip()]
    
def new_session() -> str:
    global _SESSION_ID, _SESSION_DIR, OUTPUT_DIR, _LOG_FILE

    _SESSION_ID = uuid.uuid4().hex[:8]
    _SESSION_DIR = BASE_DIR / "sessions" / _SESSION_ID
    _SESSION_DIR.mkdir(parents=True, exist_ok=True)

    OUTPUT_DIR = _SESSION_DIR / "outputs"
    OUTPUT_DIR.mkdir(exist_ok=True)

    _LOG_FILE = _SESSION_DIR / "log.jsonl"

    return _SESSION_ID