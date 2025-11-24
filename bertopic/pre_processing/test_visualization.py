import pandas as pd

TAG = "julia"

csv_path = f"../../../{TAG}-no-code.csv"
df = pd.read_csv(csv_path)

index_to_show = 0

# Verifica se o index existe
if 0 <= index_to_show < len(df):
    print(f"\n🧩 Linha {index_to_show} — Original Body:")
    print("-" * 80)
    print(df.loc[index_to_show, "body"])
    print("-" * 80)
    print(f"\n🧩 Linha {index_to_show} — Clean Body:")
    print("-" * 80)
    print(df.loc[index_to_show, "cleanbody"])
    print("-" * 80)
else:
    print(f"Indice {index_to_show} fora do intervalo (0 a {len(df)-1})")
