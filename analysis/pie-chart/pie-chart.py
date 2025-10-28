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
    "julia":      "#8c564b",
    "bash":       "#e377c2",
    "dart":       "#7f7f7f",
}

df = pd.read_csv(CSV_PATH)
df["month_start"] = pd.to_datetime(df["month_start"])
df["tagname"] = df["tagname"].str.lower() 

def plot_pie_group(df_group: pd.DataFrame, group_name: str, out_png: Path):
    """
    Pie chart mostrando a proporção de perguntas + respostas por tag
    e o breakdown interno (P vs R) em cada fatia.
    """
    summary = (
        df_group.groupby("tagname")[["questions", "answers", "total_q_a"]]
        .sum()
        .reset_index()
        .sort_values("total_q_a", ascending=False)
    )

    labels = summary["tagname"]
    values = summary["total_q_a"]
    colors = [tag_colors.get(tag, "#999999") for tag in labels]

    # função de label detalhada
    def make_autopct(q_vals, a_vals):
        total_all = (q_vals + a_vals).sum()
        def _autopct(pct):
            idx = next(i for i, v in enumerate(values.cumsum()) if pct/100 * total_all <= v)
            q = q_vals.iloc[idx]
            a = a_vals.iloc[idx]
            tag_total = q + a
            q_share = q / tag_total * 100
            a_share = a / tag_total * 100
            return f"{pct:.1f}%\n(P:{q_share:.0f}%/R:{a_share:.0f}%)"
        return _autopct

    plt.figure(figsize=(7,7))
    plt.pie(
        values,
        labels=labels,
        colors=colors,
        autopct=make_autopct(summary["questions"], summary["answers"]),
        startangle=140,
        textprops={"fontsize": 9},
    )
    titleName = "Alto Recurso" if group_name == "alto_recurso" else "Moderado Recurso"
    plt.title(f"Stack Overflow (2018–2025): Distribuição por Tag — {titleName}")
    plt.tight_layout()
    plt.savefig(out_png, dpi=160)
    plt.close()
    print(f"✅ Gráfico salvo: {out_png}")

for group_name in ["alto_recurso", "baixo_moderado"]:
    df_group = df[df["group_name"] == group_name]
    out_path = OUT_DIR / f"pie_{group_name}_detalhado.png"
    plot_pie_group(df_group, group_name, out_path)

print("✅ Finalizado! Gráficos de pizza detalhados gerados.")
