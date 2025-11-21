import pandas as pd
from bertopic import BERTopic
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

MIN_CLUSTER_SIZE = 75 
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

# --- MODELAGEM ---

print("Calculando embeddings...")
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = embedding_model.encode(docs, show_progress_bar=True)

umap_model = UMAP(n_neighbors=N_NEIGHBORS, n_components=10, min_dist=0.0, metric='cosine', random_state=42)

# min_samples baixo ajuda a recuperar pontos que seriam descartados como ruído (-1)
hdbscan_model = HDBSCAN(
    min_cluster_size=MIN_CLUSTER_SIZE, 
    min_samples=5, 
    metric='euclidean', 
    cluster_selection_method='eom', 
    prediction_data=True
)

current_tag_specific = TAG_SPECIFIC_STOPWORDS.get(TAG, set())
# custom_stop_words = list(set(ENGLISH_STOP_WORDS).union(BOILERPLATE_WORDS).union(current_tag_specific))
custom_stop_words = list(set(ENGLISH_STOP_WORDS)
                         .union(BOILERPLATE_WORDS)
                         .union(GENERIC_TECH_WORDS) 
                         .union(current_tag_specific))

vectorizer_model = CountVectorizer(min_df=2, ngram_range=(1, 2), stop_words=custom_stop_words)
representation_model = {"KeyBERT": KeyBERTInspired(), "MMR": MaximalMarginalRelevance(diversity=0.3)}

print("Treinando BERTopic...")
topic_model = BERTopic(
    embedding_model=embedding_model,
    umap_model=umap_model,
    hdbscan_model=hdbscan_model, 
    vectorizer_model=vectorizer_model, 
    representation_model=representation_model,
    nr_topics=NR_TOPICS,
    top_n_words=10,
    calculate_probabilities=True, 
    verbose=True
)

topics, probs = topic_model.fit_transform(docs, embeddings=embeddings)

print(f"Salvando o modelo completo em: {OUTPUT_MODEL_DIR}")
topic_model.save(OUTPUT_MODEL_DIR, serialization="safetensors", save_ctfidf=True, save_embedding_model="all-MiniLM-L6-v2")
print("Modelo salvo! Para carregar depois use: topic_model = BERTopic.load(path)")

# --- POS-PROCESSAMENTO ---

if probs is not None:
    print("Salvando probabilidades...")
    df_probs = pd.DataFrame(probs)
    topic_ids = sorted(topic_model.get_topics().keys())
    if df_probs.shape[1] == len(topic_ids):
        df_probs.columns = [f"prob_topic_{tid}" for tid in topic_ids]
    df_probs.to_csv(OUTPUT_PROBS_PATH, index=False)

print("Gerando Topics Over Time...")
topics_over_time = topic_model.topics_over_time(docs=docs, timestamps=years, global_tuning=True, evolution_tuning=True)
topics_over_time.to_csv(OUTPUT_TOT_CSV_PATH, index=False)

topics_to_visualize = [t for t in topics_over_time.Topic.unique() if t != -1]
fig = topic_model.visualize_topics_over_time(topics_over_time, topics=topics_to_visualize)
fig.write_html(OUTPUT_TOT_HTML_PATH)

print("Concluído.")