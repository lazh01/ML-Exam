import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from pathlib import Path
import uuid
import json

from tools.execute_code import validate_code

from logger import get_output_dir
OUTPUT_DIR = get_output_dir()

DATA_PATH = Path(__file__).parent.parent / "data" / "ads.csv"


def plot_code(code: str) -> dict:
    violations = validate_code(code)
    if violations:
        return {"error": f"Forbudte mønstre: {violations}"}

    df = pd.read_csv(DATA_PATH)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # Generer filepath og giv den til koden via namespace
    plot_id = uuid.uuid4().hex[:8]
    filepath = OUTPUT_DIR / f"plot_{plot_id}.html"
    filepath_png = OUTPUT_DIR / f"plot_{plot_id}.png"

    namespace = {
        "df": df.copy(),
        "pd": pd,
        "np": np,
        "plt": plt,
        "sns": sns,
        "px": px,
        "go": go,
        "filepath": filepath,
        "filepath_png": filepath_png,
        "OUTPUT_DIR": OUTPUT_DIR,
    }

    try:
        exec(code, namespace)
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}

    if filepath.exists():
        return {"saved_to": str(filepath), "type": "html"}
    elif filepath_png.exists():
        return {"saved_to": str(filepath_png), "type": "png"}
    else:
        return {"error": "Plot blev ikke gemt. Brug filepath til plotly HTML eller filepath_png til matplotlib PNG."}

    return {"saved_to": str(filepath)}