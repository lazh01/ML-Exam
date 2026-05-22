import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
import uuid

OUTPUT_DIR = Path(__file__).parent.parent / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

def plot_chart(data: list, chart_type: str, x: str, y: str, title: str, group_by: str = None) -> dict:
    if not data:
        return {"error": "Ingen data at plotte"}

    if x not in data[0] or y not in data[0]:
        return {"error": f"Kolonner ikke fundet. Tilgængelige: {list(data[0].keys())}"}

    fig, ax = plt.subplots(figsize=(12, 6))
    colors = ["#4F8EF7", "#F7714F", "#4FF77A", "#F7E24F", "#C44FF7"]

    if group_by and group_by in data[0]:
        # Flere serier — gruppér på group_by kolonnen
        groups = {}
        for row in data:
            key = row[group_by]
            if key not in groups:
                groups[key] = []
            groups[key].append(row)

        for i, (group_name, rows) in enumerate(groups.items()):
            x_vals = [row[x] for row in rows]
            y_vals = [row[y] for row in rows]
            color = colors[i % len(colors)]

            if chart_type == "line":
                ax.plot(x_vals, y_vals, marker="o", label=group_name, color=color, linewidth=2)
            elif chart_type == "bar":
                import numpy as np
                n = len(groups)
                width = 0.8 / n
                positions = [j + (i - n/2 + 0.5) * width for j, _ in enumerate(x_vals)]
                ax.bar(positions, y_vals, width=width, label=group_name, color=color)
                ax.set_xticks(range(len(x_vals)))
                ax.set_xticklabels(x_vals)
            elif chart_type == "scatter":
                ax.scatter(x_vals, y_vals, label=group_name, color=color, alpha=0.6)

        ax.legend()

    else:
        # Enkelt serie — som før
        x_vals = [row[x] for row in data]
        y_vals = [row[y] for row in data]

        if chart_type == "bar":
            ax.bar(x_vals, y_vals, color=colors[0])
        elif chart_type == "line":
            ax.plot(x_vals, y_vals, marker="o", color=colors[0], linewidth=2)
        elif chart_type == "scatter":
            ax.scatter(x_vals, y_vals, color=colors[0], alpha=0.6)
        elif chart_type == "pie":
            ax.pie(y_vals, labels=x_vals, autopct="%1.1f%%")

    plt.xticks(rotation=45, ha="right")
    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    plt.tight_layout()

    filename = f"{chart_type}_{uuid.uuid4().hex[:8]}.png"
    filepath = OUTPUT_DIR / filename
    plt.savefig(filepath, dpi=150, bbox_inches="tight")
    plt.close(fig)

    return {"saved_to": str(filepath), "title": title}