import pandas as pd
from bertopic import BERTopic
import plotly.io as pio

from sentence_transformers import SentenceTransformer
from umap import UMAP
from hdbscan import HDBSCAN
from sklearn.feature_extraction.text import CountVectorizer
from bertopic.representation import KeyBERTInspired, MaximalMarginalRelevance

from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from pre_processing.custom_stopwords import STOPWORD_SETS

TAG = "julia"
MIN_CLUSTER_SIZE = 100

INPUT_CSV_PATH = f"../../{TAG}-no-code.csv"
TEXT_COLUMN = "cleanbodynostop"
DATE_COLUMN = "lastactivitydate"
YEAR_COLUMN = "ano"

OUTPUT_TOT_CSV_PATH = f"../../{TAG}-topics_over_time.csv"
OUTPUT_TOT_HTML_PATH = f"../../{TAG}-topics_over_time.html"
OUTPUT_PROBS_PATH = f"../../{TAG}-topic_probabilities.csv"

# Para abrir no navegador
pio.renderers.default = "browser"

print(f"Carregando dados pre-processados de: {INPUT_CSV_PATH}")
try:
    df = pd.read_csv(INPUT_CSV_PATH)
except FileNotFoundError:
    print(f"ERRO: Arquivo nao encontrado em {INPUT_CSV_PATH}")
    exit()

if TEXT_COLUMN not in df.columns or DATE_COLUMN not in df.columns:
    print(f"ERRO: O CSV deve conter as colunas '{TEXT_COLUMN}' e '{DATE_COLUMN}'.")
    exit()

# Remove documentos vazios que podem ter sido criados na limpeza
df = df.dropna(subset=[TEXT_COLUMN])
df = df[df[TEXT_COLUMN].str.strip().astype(bool)]

# Converte a coluna de data para o formato datetime
# 'errors=coerce' transforma datas invalidas em Nulo
df[DATE_COLUMN] = pd.to_datetime(df[DATE_COLUMN], errors='coerce')
df = df.dropna(subset=[DATE_COLUMN])  # Remove datas nulas

# Prepara as listas para o BERTopic
docs = df[TEXT_COLUMN].tolist()
timestamps = df[DATE_COLUMN].tolist()
years = df[YEAR_COLUMN].tolist()

print(f"Total de {len(docs)} documentos prontos para o BERTopic.")

# Pre-calcular Embeddings
print("Iniciando pré-cálculo de embeddings... (Isso pode levar um tempo)")
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = embedding_model.encode(docs, show_progress_bar=True)
print("Embeddings calculados.")

# Definir Modelos de Componentes para Reprodutibilidade e Qualidade
# UMAP (Redução de Dimensionalidade)
# random_state=42 garante que os resultados sejam sempre os mesmos
umap_model = UMAP(n_neighbors=15,
                  n_components=5,
                  min_dist=0.0,
                  metric='cosine',
                  random_state=42)

# HDBSCAN (Clusterização)
# min_cluster_size pode ser usado como um delimitador de quantidade de classes
hdbscan_model = HDBSCAN(min_cluster_size=MIN_CLUSTER_SIZE,
                        metric='euclidean',
                        cluster_selection_method='eom',
                        prediction_data=True)

custom_stop_words = set(ENGLISH_STOP_WORDS).union(STOPWORD_SETS[TAG])

# CountVectorizer (Nomes dos Topicos)
# min_df=2 ignora palavras que aparecem em menos de 2 documentos
vectorizer_model = CountVectorizer(min_df=2, ngram_range=(1, 2), stop_words=custom_stop_words)

# Representation Models (Nomes de Topicos Alternativos)
keybert_model = KeyBERTInspired()
mmr_model = MaximalMarginalRelevance(diversity=0.3)

# Combina as representações
representation_model = {
    "KeyBERT": keybert_model,
    "MMR": mmr_model
}

print("Treinando o modelo BERTopic... (Isso pode levar um tempo)")

topic_model = BERTopic(
    embedding_model=embedding_model,
    umap_model=umap_model,
    hdbscan_model=hdbscan_model, 
    vectorizer_model=vectorizer_model, 
    representation_model=representation_model,

    # Hiperparâmetros
    top_n_words=10,
    calculate_probabilities=True,  
    verbose=True
)

# Treina o modelo na amostra completa (com os embeddings pre-calculados)
topics, probs = topic_model.fit_transform(docs, embeddings=embeddings)

print("Treinamento concluído. Modelo possui", len(
    topic_model.get_topic_info()), "tópicos.")

if probs is not None:
    print(f"Salvando probabilidades dos tópicos em {OUTPUT_PROBS_PATH}...")
    # Converte o array numpy 'probs' em um DataFrame do Pandas
    df_probs = pd.DataFrame(probs)

    # Pega os IDs dos tópicos para nomear as colunas
    # O .get_topics() retorna um dict, pegamos as chaves (IDs)
    topic_ids = sorted(topic_model.get_topics().keys())

    # Garante que o número de colunas bate com o número de tópicos
    if len(topic_ids) == df_probs.shape[1]:
        df_probs.columns = [f"prob_topic_{tid}" for tid in topic_ids]
    else:
        print("Aviso: Discrepância no número de colunas de probabilidade e IDs de tópico.")
        # Salva com nomes genéricos se algo der errado
        df_probs.columns = [f"prob_col_{i}" for i in range(df_probs.shape[1])]

    df_probs.to_csv(OUTPUT_PROBS_PATH, index=False)
else:
    print("Probabilidades não foram calculadas (probs is None). Pulando salvamento.")

print("Iniciando análise temporal (topics_over_time)...")
# 'timestamps=years' força o BERTopic a agrupar exatamente por ano
topics_over_time = topic_model.topics_over_time(docs=docs, timestamps=years)

print("\nAmostra da tabela de Tópicos ao Longo do Tempo:")
print(topics_over_time.head())

topics_over_time.to_csv(OUTPUT_TOT_CSV_PATH, index=False)

print("Gerando visualização... O gráfico abrirá no navegador.")

# (-1 é o tópico de "outliers", pulando)
# topics_to_visualize = list(topic_model.get_topic_info(10).Topic) # Pega os 10 maiores
topics_to_visualize = [
    topic for topic in topics_over_time.Topic.unique() if topic != -1]

# Gera um gráfico de linha interativo
fig = topic_model.visualize_topics_over_time(topics_over_time,
                                             topics=topics_to_visualize,
                                             width=1000,
                                             height=600)

fig.write_html(OUTPUT_TOT_HTML_PATH)

print(f"Análise concluída! Resultados salvos em:")
print(f"  - CSV Tópicos ao Longo do Tempo: '{OUTPUT_TOT_CSV_PATH}'")
print(f"  - HTML Tópicos ao Longo do Tempo: '{OUTPUT_TOT_HTML_PATH}'")
if probs is not None:
    print(f"  - CSV Probabilidades:              '{OUTPUT_PROBS_PATH}'")
