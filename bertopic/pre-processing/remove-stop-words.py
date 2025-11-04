import pandas as pd
import nltk
from nltk.corpus import stopwords
import re

from custom_stopwords import STOPWORD_SETS

TAG = "julia"

input_path = f"../../../{TAG}-no-code.csv"
output_path = f"../../../{TAG}-nostop.csv"

nltk.download("stopwords")
stop_words = set(stopwords.words("english"))

# stop_words.update([""])  # adiciona mais palavras custom
# stop_words.discard("") # remove palavras da lista

stop_words.update(STOPWORD_SETS[TAG])

def remove_stopwords(text):
    if pd.isna(text):
        return ""

    # Converte para minusculas
    text = text.lower()

    # Remove caracteres não alfabeticos
    text = re.sub(r"[^a-z]", " ", text)

    # Divide em palavras
    words = text.split()

    # Remove stopwords
    filtered = [word for word in words if word not in stop_words]

    # Junta novamente em uma string
    return " ".join(filtered)

df = pd.read_csv(input_path)
df["cleanbodynostop"] = df["cleanbody"].apply(remove_stopwords)

df.to_csv(output_path, index=False, encoding="utf-8")

print(f"Arquivo salvo como '{output_path}'")
