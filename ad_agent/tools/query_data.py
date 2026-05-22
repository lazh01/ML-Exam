import pandas as pd
from pathlib import Path

_DATA_PATH = Path(__file__).parent.parent / "data" / "ads.csv"
_df = None

def load_df() -> pd.DataFrame:
    global _df
    if _df is None:
        _df = pd.read_csv(_DATA_PATH)
        _df.columns = [c.strip().lower().replace(" ", "_") for c in _df.columns]
    return _df

def get_schema() -> dict:
    df = load_df()
    return {
        "columns": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "shape": list(df.shape),
        "sample": df.head(3).to_dict(orient="records")
    }

def query_data(question: str) -> dict:
    df = load_df()
    return {
        "schema": get_schema(),
        "question": question
    }