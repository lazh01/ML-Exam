import pandas as pd
import numpy as np
from tools.query_data import load_df
from logger import get_output_dir
BANNED = ["os.", "subprocess", "open(", "shutil", "__import__", "eval(", "exec("]

def validate_code(code: str) -> list:
    return [p for p in BANNED if p in code]

def execute_code(code: str) -> dict:
    violations = validate_code(code)
    if violations:
        return {"error": f"Forbudte mønstre fundet: {violations}"}

    df = load_df()
    namespace = {
        "df": df.copy(),
        "pd": pd,
        "np": np,
    }

    try:
        exec(code, namespace)
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}

    if "result" not in namespace:
        return {"error": "Koden tildelte ikke noget til `result`"}

    raw = namespace["result"]

    if isinstance(raw, pd.DataFrame):
        serialised = raw.to_dict(orient="records")
    elif isinstance(raw, pd.Series):
        serialised = raw.reset_index().to_dict(orient="records")
    else:
        return {"result": raw}

    # Gem store resultater til fil i stedet for at sende dem tilbage
    if len(serialised) > 20:
        import json
        import uuid
        from pathlib import Path
        out_path = get_output_dir() / f"data_{uuid.uuid4().hex[:8]}.json"
        with open(out_path, "w") as f:
            json.dump(serialised, f, default=str)
        return {
            "saved_to": str(out_path),
            "rows": len(serialised),
            "columns": list(serialised[0].keys()) if serialised else [],
            "preview": serialised[:3],
            "note": "Full data saved to file. Use this file path for plotting."
        }

    return {"result": serialised}