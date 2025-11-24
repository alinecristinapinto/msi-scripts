import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

CSV_PATH = "../post-sums-query.csv" 
OUT_PATH = Path("compare_groups.png")

df = pd.read_csv(CSV_PATH)
df["month_start"] = pd.to_datetime(df["month_start"])

# soma todas as perguntas e respostas do periodo inteiro
agg = (
    df.groupby("group_name")[["questions", "answers", "total_q_a"]]
    .sum()
    .reset_index()
)

agg["group_name"] = agg["group_name"].replace({
    "alto_recurso": "Alto Recurso",
    "baixo_moderado": "Moderado Recurso"
})

print(agg)

plt.figure(figsize=(8,6))

x = range(len(agg))
bar_width = 0.3

plt.bar([i - bar_width/2 for i in x], agg["questions"], width=bar_width, label="Perguntas", color="#1f77b4")
plt.bar([i + bar_width/2 for i in x], agg["answers"], width=bar_width, label="Respostas", color="#ff7f0e")

plt.title("Stack Overflow (2018–2025): Comparativo de Grupos")
plt.xticks(x, agg["group_name"])
plt.ylabel("Quantidade Total (2018–2025)")
plt.ticklabel_format(style="plain", axis="y") 
plt.legend()
plt.tight_layout()
plt.savefig(OUT_PATH, dpi=160)
plt.show()

print(f"Gráfico salvo em {OUT_PATH}")


