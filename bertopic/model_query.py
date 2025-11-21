import os 
import pandas as pd
from bertopic import BERTopic

TAG = "r" 

BASE_DIR = "../../" 
MODEL_PATH = f"{BASE_DIR}models/{TAG}_model"

OUTPUT_MODEL_DIR = f"{BASE_DIR}models/{TAG}_results"
os.makedirs(OUTPUT_MODEL_DIR, exist_ok=True)

OUTPUT_PATH = os.path.join(OUTPUT_MODEL_DIR, f"{TAG}_topics.csv")

print(f"Carregando modelo de: {MODEL_PATH}")
topic_model = BERTopic.load(MODEL_PATH) 

print(f"Tópico 0 (Exemplo): {topic_model.get_topic(0)}")

df_info = topic_model.get_topic_info()

print(f"Salvando tabela de tópicos em: {OUTPUT_PATH}")
df_info.to_csv(OUTPUT_PATH, index=False)