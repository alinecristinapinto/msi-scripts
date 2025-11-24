import pandas as pd
from bs4 import BeautifulSoup
import re

TAG = "python"

csv_path = f"../../../{TAG}-sample.csv"
output_path = f"../../../{TAG}-no-code.csv"

df = pd.read_csv(csv_path)

def clean_body(text):
    if pd.isna(text):
        return ""

    # Remove blocos de código entre <code>...</code>
    text = re.sub(r"<code>.*?</code>", "", text, flags=re.DOTALL)

    # Remove blocos de código em Markdown (``` ... ```)
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)

    # Remove links
    text = re.sub(r'https?://\S+|www\.\S+', '', text)

    # Remove tags HTML restantes
    soup = BeautifulSoup(text, "html.parser")
    cleaned = soup.get_text(separator=" ", strip=True)

    # Remove múltiplos espaços e linhas em branco
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    return cleaned

df["cleanbody"] = df["body"].apply(clean_body)

df.to_csv(output_path, index=False, encoding="utf-8")

print(f"Arquivo salvo como '{output_path}'")
