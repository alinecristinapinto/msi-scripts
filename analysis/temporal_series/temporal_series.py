import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

CSV_PATH = "../post-sums-query.csv"  

OUT_DIR = Path("./")
OUT_DIR.mkdir(parents=True, exist_ok=True)

tag_colors = {
    "python":     "#1f77b4",
    "javascript": "#ff7f0e",
    "java":       "#2ca02c",
    "c#":         "#d62728",
    "r":          "#9467bd",
    "Julia":      "#8c564b",
    "bash":       "#e377c2",
    "dart":       "#7f7f7f",
}

df = pd.read_csv(CSV_PATH)
df["month_start"] = pd.to_datetime(df["month_start"])

def plot_group_total(df_group: pd.DataFrame, group_name: str, out_png: Path):
    monthly = (
        df_group.groupby("month_start")[["questions", "answers", "total_q_a"]]
        .sum()
        .reset_index()
    )

    plt.figure(figsize=(10, 6))
    plt.plot(monthly["month_start"], monthly["questions"], label="Perguntas", color="#1f77b4")
    plt.plot(monthly["month_start"], monthly["answers"], label="Respostas", color="#ff7f0e")
    plt.plot(monthly["month_start"], monthly["total_q_a"], label="Total (Perguntas + Respostas)", color="#2ca02c", linewidth=2)
    titleName = "Alto Recurso" if group_name == "alto_recurso" else "Moderado Recurso"
    plt.title(f"Stack Overflow (2018–2025): Total por grupo — {titleName}")
    plt.xlabel("Mês")
    plt.xlim(pd.Timestamp("2018-01-01"), pd.Timestamp("2025-12-31"))
    plt.ylabel("Quantidade")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_png, dpi=160)
    plt.close()
    print(f"Gráfico salvo: {out_png}")

def plot_group_metric(df_group: pd.DataFrame, metric: str, title: str, out_png: Path):
    pivot = df_group.pivot(index="month_start", columns="tagname", values=metric).fillna(0)

    plt.figure(figsize=(10, 6))
    for tag in sorted(pivot.columns):
        plt.plot(pivot.index, pivot[tag], label=tag, color=tag_colors.get(tag))
    ylabel = "Perguntas" if metric == "questions" else "Respostas"
    plt.title(title)
    plt.xlabel("Mês")
    plt.xlim(pd.Timestamp("2018-01-01"), pd.Timestamp("2025-12-31"))
    plt.ylabel(ylabel)
    plt.legend(ncol=2)
    plt.tight_layout()
    plt.savefig(out_png, dpi=160)
    plt.close()
    print(f"✅ Salvo: {out_png}")

for group in ["alto_recurso", "baixo_moderado"]:
    gdf = df[df["group_name"] == group].copy()
    titleName = "Alto Recurso" if group == "alto_recurso" else "Moderado Recurso"

    # 1) Perguntas por linguagem
    plot_group_metric(
        gdf, "questions",
        f"Stack Overflow (2018–2025): {titleName} — Perguntas",
        OUT_DIR / f"timeline_{group}_perguntas.png",
    )

    # 2) Respostas por linguagem
    plot_group_metric(
        gdf, "answers",
        f"Stack Overflow (2018–2025): {titleName} — Respostas ",
        OUT_DIR / f"timeline_{group}_respostas.png",
    )

for group_name in ["alto_recurso", "baixo_moderado"]:
    df_group = df[df["group_name"] == group_name]
    out_path = OUT_DIR / f"timeline_{group_name}_total.png"
    plot_group_total(df_group, group_name, out_path)

print("Finalizado! Gráficos totais por grupo gerados.")
