import pandas as pd
from bertopic import BERTopic
from bertopic.vectorizers import ClassTfidfTransformer # Importante para limpar stopwords
import plotly.io as pio
import os 

from sentence_transformers import SentenceTransformer
from umap import UMAP
from hdbscan import HDBSCAN
from sklearn.feature_extraction.text import CountVectorizer
from bertopic.representation import KeyBERTInspired, MaximalMarginalRelevance

from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from pre_processing.custom_stopwords import BOILERPLATE_WORDS, GENERIC_TECH_WORDS, TAG_SPECIFIC_STOPWORDS 

TAG = "python" 

MIN_CLUSTER_SIZE = 40 

N_NEIGHBORS = 15
NR_TOPICS = 10

BASE_DIR = "../../" 
INPUT_CSV_PATH = f"{BASE_DIR}{TAG}-no-code.csv"  
OUTPUT_MODEL_DIR = f"{BASE_DIR}models/{TAG}_model" 

os.makedirs(os.path.dirname(OUTPUT_MODEL_DIR), exist_ok=True)

OUTPUT_TOT_CSV_PATH = f"{BASE_DIR}{TAG}-topics_over_time.csv"
OUTPUT_TOT_HTML_PATH = f"{BASE_DIR}{TAG}-topics_over_time.html"
OUTPUT_PROBS_PATH = f"{BASE_DIR}{TAG}-topic_probabilities.csv"

pio.renderers.default = "browser"

print(f"Tag: {TAG}")
print(f"Carregando dados de: {INPUT_CSV_PATH}")

try:
    df = pd.read_csv(INPUT_CSV_PATH)
except FileNotFoundError:
    print(f"ERRO: Arquivo nao encontrado em {INPUT_CSV_PATH}")
    exit()

TEXT_COLUMN = "cleanbody"
DATE_COLUMN = "lastactivitydate"
YEAR_COLUMN = "ano"

df = df.dropna(subset=[TEXT_COLUMN])
df = df[df[TEXT_COLUMN].str.strip().astype(bool)]

df[DATE_COLUMN] = pd.to_datetime(df[DATE_COLUMN], errors='coerce')
df = df.dropna(subset=[DATE_COLUMN])

docs = df[TEXT_COLUMN].tolist()
timestamps = df[DATE_COLUMN].tolist() 
years = df[YEAR_COLUMN].tolist()

print(f"Total de {len(docs)} documentos prontos.")

print("Calculando embeddings...")
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = embedding_model.encode(docs, show_progress_bar=True)

umap_model = UMAP(n_neighbors=N_NEIGHBORS, n_components=5, min_dist=0.0, metric='cosine', random_state=42)

hdbscan_model = HDBSCAN(
    min_cluster_size=MIN_CLUSTER_SIZE, 
    min_samples=5, 
    metric='euclidean', 
    cluster_selection_method='eom', 
    prediction_data=True
)

current_tag_specific = TAG_SPECIFIC_STOPWORDS.get(TAG, set())
custom_stop_words = list(set(ENGLISH_STOP_WORDS)
                         .union(BOILERPLATE_WORDS)
                         .union(GENERIC_TECH_WORDS) 
                         .union(current_tag_specific))

vectorizer_model = CountVectorizer(
    min_df=5, 
    max_df=0.95, 
    ngram_range=(1, 2), 
    stop_words=custom_stop_words
)

ctfidf_model = ClassTfidfTransformer(reduce_frequent_words=True)

keybert_model = KeyBERTInspired()
mmr_model = MaximalMarginalRelevance(diversity=0.3)

representation_model = {
    "Main": keybert_model, 
    "KeyBERT": keybert_model,
    "MMR": mmr_model
}

print("Treinando BERTopic...")
topic_model = BERTopic(
    embedding_model=embedding_model,
    umap_model=umap_model,
    hdbscan_model=hdbscan_model, 
    vectorizer_model=vectorizer_model, 
    ctfidf_model=ctfidf_model,
    representation_model=representation_model,
    top_n_words=10,
    calculate_probabilities=True, 
    verbose=True
)

topics, probs = topic_model.fit_transform(docs, embeddings=embeddings)

if -1 in topics:
    print(f"Outliers antes da redução: {topics.count(-1)}")
    new_topics = topic_model.reduce_outliers(docs, topics, probabilities=probs, strategy="probabilities")
    topic_model.update_topics(docs, topics=new_topics)
    topics = new_topics
    print(f"Outliers depois da redução: {topics.count(-1)}")

# --- SALVANDO PROBABILIDADES (ANTES DE REDUZIR TÓPICOS) ---
if probs is not None:
    print("Salvando probabilidades...")
    df_probs = pd.DataFrame(probs)
    
    try:
        current_topic_ids = sorted(list(set(topics)))
        if -1 in current_topic_ids: current_topic_ids.remove(-1)
        
        if df_probs.shape[1] == len(current_topic_ids):
            df_probs.columns = [f"prob_topic_{tid}" for tid in current_topic_ids]
        else:
            df_probs.columns = [f"prob_col_{i}" for i in range(df_probs.shape[1])]
            
        df_probs.to_csv(OUTPUT_PROBS_PATH, index=False)
    except Exception as e:
        print(f"Aviso: Não foi possível salvar nomes exatos das colunas de probabilidade ({e}). Salvando cru.")
        pd.DataFrame(probs).to_csv(OUTPUT_PROBS_PATH, index=False)

print(f"Reduzindo de {len(set(topics))} para {NR_TOPICS} tópicos principais...")
topic_model.reduce_topics(docs, nr_topics=NR_TOPICS)

# O reduce_topics reseta a representação para o padrão. 
# Precisamos reaplicar o KeyBERT e o Vectorizer limpo nos tópicos finais.
print("Reaplicando configurações de limpeza e KeyBERT nos tópicos reduzidos...")
topic_model.update_topics(
    docs, 
    vectorizer_model=vectorizer_model, 
    ctfidf_model=ctfidf_model, 
    representation_model=representation_model
)

topics = topic_model.topics_

print(f"Salvando o modelo completo em: {OUTPUT_MODEL_DIR}")
topic_model.save(OUTPUT_MODEL_DIR, serialization="safetensors", save_ctfidf=True, save_embedding_model="all-MiniLM-L6-v2")

print("Gerando Topics Over Time...")
topics_over_time = topic_model.topics_over_time(docs=docs, timestamps=years, global_tuning=True, evolution_tuning=True)
topics_over_time.to_csv(OUTPUT_TOT_CSV_PATH, index=False)

topics_to_visualize = [t for t in topics_over_time.Topic.unique() if t != -1]
fig = topic_model.visualize_topics_over_time(topics_over_time, topics=topics_to_visualize)
fig.write_html(OUTPUT_TOT_HTML_PATH)

print("\n--- TÓPICOS FINAIS ---")
print(topic_model.get_topic_info().head(11))

print("Concluído.")