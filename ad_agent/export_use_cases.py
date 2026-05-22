import json
from pathlib import Path

SESSIONS_DIR = Path(__file__).parent / "sessions"
OUTPUT_FILE = Path(__file__).parent / "use_cases.md"


def load_session(session_dir: Path) -> dict | None:
    log_file = session_dir / "log.jsonl"
    if not log_file.exists():
        return None

    records = []
    with log_file.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

    if not records:
        return None

    # Find user_query og final_answer
    query = None
    answer = None
    timestamp = None

    for r in records:
        if r["tool"] == "user_query":
            query = r["input"].get("query")
            timestamp = r["timestamp"]
        if r["tool"] == "final_answer":
            answer = r["result"].get("answer")

    if not query or not answer:
        return None

    return {
        "session_id": records[0]["session_id"],
        "timestamp": timestamp,
        "query": query,
        "answer": answer
    }


def main():
    if not SESSIONS_DIR.exists():
        print("Ingen sessions mappe fundet.")
        return

    sessions = []
    for session_dir in sorted(SESSIONS_DIR.iterdir()):
        if session_dir.is_dir():
            data = load_session(session_dir)
            if data:
                sessions.append(data)

    if not sessions:
        print("Ingen komplette sessioner fundet.")
        return

    # Sorter efter timestamp
    sessions.sort(key=lambda x: x["timestamp"])

    # Skriv markdown fil
    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        f.write("# Ad Campaign Agent — Use Cases\n\n")
        f.write(f"*{len(sessions)} use cases collected.*\n\n")
        f.write("---\n\n")

        for i, s in enumerate(sessions, 1):
            f.write(f"## Use Case {i}\n\n")
            f.write(f"**Session ID:** `{s['session_id']}`  \n")
            f.write(f"**Timestamp:** {s['timestamp']}\n\n")
            f.write(f"### Input\n\n")
            f.write(f"{s['query']}\n\n")
            f.write(f"### Output\n\n")
            f.write(f"{s['answer']}\n\n")
            f.write("---\n\n")

    print(f"Eksporteret {len(sessions)} use cases til {OUTPUT_FILE}")


if __name__ == "__main__":
    main()