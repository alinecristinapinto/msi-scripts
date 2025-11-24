import pandas as pd
import numpy as np
import os
from bertopic import BERTopic
from bertopic.vectorizers import ClassTfidfTransformer
from sentence_transformers import SentenceTransformer
from umap import UMAP
from hdbscan import HDBSCAN
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from sklearn.metrics.pairwise import cosine_similarity
from bertopic.representation import KeyBERTInspired, MaximalMarginalRelevance


TAG = "bash"
CHATGPT_LAUNCH = pd.to_datetime("2022-11-30")

BASE_DIR = "../../"
INPUT_CSV_PATH = f"{BASE_DIR}{TAG}-no-code.csv"
OUTPUT_DIR = f"{BASE_DIR}results_comparison/{TAG}/"

MIN_CLUSTER_SIZE = 40 
N_NEIGHBORS = 15
NR_TOPICS = 10

os.makedirs(OUTPUT_DIR, exist_ok=True)

BOILERPLATE_WORDS = {
    'question', 'questions', 'follow', 'similar', 'asked', 'previous', 'answer', 'thanks', 'help', 
    'example', 'using', 'way', 'need', 'tried', 'trying', 'following', 'want', 'like', 'solution',
    'use', 'create', 'make', 'get', 'know', 'find', 'work', 'working', 'issue', 'problem', 'error',
    'just',  'works', 'does', 've'
}

GENERIC_TECH_WORDS = {'data', 'value', 'values', 'code', 'line', 'lines', 'script', 'file', 'files'}

TAG_SPECIFIC_STOPWORDS = {
    "python": {
        "python", "py", "python3", "dict", "dictionary", "tuple", "set", "string", "str", "int", "float", "bool",
        "array", "json", "xml", "import", "from", "module", "library", "package", "function", "method", "object",
        "variable", "loop", "script", "code", "statement", "args", "kwargs", "self", "main", "init", 
        "print", "run", "running", "executed", "input", "output", "write", "read", "open", "close",
        "create", "make", "build", "get", "got", "set", "call", "calling",  "nan", "null", "none", "true", "false", 
        "id", "value", "values", "key", "keys", "data", "result", "results",  "column", "row", "rows", "columns", "index", "dataframe", "pandas", "df", 
        "file", "files", "path", "dir", "directory", "folder", "terminal", "command", "cmd",
        "pip", "install", "installed"
    },
    "java": {
        "java", "public", "private", "class", "void", "static", "new", "string", "int", 
        "system", "out", "println", "null", "object", "import", "package", "method"
    },
    "javascript": {
        "javascript", "js", "node", "nodejs", "var", "let", "const", "function", "console", "log",
        "document", "window", "element", "html", "css", "json", "object", "array"
    },
    "c#": {
        "c#", "csharp", ".net", "public", "private", "void", "string", "int", "class", "namespace", 
        "using", "static", "var", "object", "new", "method", "app", "application", "project", "server",
        "client", "service", "api", "console", "function", "implementation", "code", "run", "running", "build", "error",
        "exception", "database", "db", "table", "row", "column", "id", "key"
    },
    "r": {
        "r", "rstudio", "shiny", "plot", "ggplot", "column", "row", "dataframe", "df", "dt",
        "function", "library", "install", "packages", "vector", "list", "na", "null"
    },
    "julia": {
        "julia", "jl", "function", "end", "using", "struct", "array", "vector", "plot"
    },
    "bash": {
        "bash", "shell", "script", "sh", "command", "run", "echo", "file", "directory", "path",
        "terminal", "linux", "unix", "sudo", "permissions"
    },
    "dart": {
        "dart", "flutter", "widget", "build", "context", "child", "children", "return", "void",
        "class", "import", "package", "app", "state", "string", "int"
    }
}

def get_custom_stopwords(tag):
    stops = list(ENGLISH_STOP_WORDS)
    stops.extend(list(BOILERPLATE_WORDS))
    stops.extend(list(GENERIC_TECH_WORDS))
    
    if tag in TAG_SPECIFIC_STOPWORDS:
        stops.extend(list(TAG_SPECIFIC_STOPWORDS[tag]))
    
    return list(set(stops)) # Remove duplicatas

print(f"--- Iniciando processamento para tag: {TAG.upper()} ---")
print(f"Lendo dados de: {INPUT_CSV_PATH}")

try:
    df = pd.read_csv(INPUT_CSV_PATH)
except FileNotFoundError:
    print("ERRO: Arquivo CSV não encontrado.")
    exit()

df['lastactivitydate'] = pd.to_datetime(df['lastactivitydate'], errors='coerce')
df = df.dropna(subset=['cleanbody', 'lastactivitydate'])
df = df[df['cleanbody'].str.strip().astype(bool)]

df_pre = df[df['lastactivitydate'] < CHATGPT_LAUNCH]
df_post = df[df['lastactivitydate'] >= CHATGPT_LAUNCH]

print(f"Total Docs: {len(df)}")
print(f"Docs PRE:  {len(df_pre)}")
print(f"Docs POST: {len(df_post)}")

if len(df_pre) < 50 or len(df_post) < 50:
    print("ERRO: Dados insuficientes.")
    exit()

# TREINAMENTO (COM REDUÇÃO PÓS-TREINO)
def train_model(docs, suffix_name):
    print(f"\n>>> Treinando Modelo: {suffix_name} ({len(docs)} docs)...")
    
    final_stops = get_custom_stopwords(TAG)
    
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    umap_model = UMAP(n_neighbors=N_NEIGHBORS, n_components=5, min_dist=0.0, metric='cosine', random_state=42)
    hdbscan_model = HDBSCAN(min_cluster_size=MIN_CLUSTER_SIZE, metric='euclidean', cluster_selection_method='eom', prediction_data=True)    
    vectorizer_model = CountVectorizer(stop_words=final_stops, ngram_range=(1, 2), min_df=5) # min_df=1 para R
    
    representation_model = {
        "KeyBERT": KeyBERTInspired(),
        "MMR": MaximalMarginalRelevance(diversity=0.3)
    }

    topic_model = BERTopic(
        embedding_model=embedding_model,
        umap_model=umap_model,
        hdbscan_model=hdbscan_model,
        vectorizer_model=vectorizer_model,
        ctfidf_model=ClassTfidfTransformer(reduce_frequent_words=True),
        representation_model=representation_model,
        verbose=True
    )
    
    topic_model.fit(docs)
    
    print(f"   -> Reduzindo para {NR_TOPICS} tópicos...")
    topic_model.reduce_topics(docs, nr_topics=NR_TOPICS)
    
    save_path = f"{OUTPUT_DIR}model_{suffix_name.lower()}"
    topic_model.save(save_path, serialization="safetensors", save_ctfidf=True)
    print(f"Modelo salvo em: {save_path}")
    
    info_df = topic_model.get_topic_info()
    info_df.to_csv(f"{OUTPUT_DIR}topics_info_{suffix_name.lower()}.csv", index=False)
    
    return topic_model


model_pre = train_model(df_pre['cleanbody'].tolist(), "PRE")
model_post = train_model(df_post['cleanbody'].tolist(), "POST")

# MATCHING DE TÓPICOS 
print("\n>>> Calculando Equivalência (Matching) entre Tópicos...")

# Função auxiliar para pegar embeddings ignorando outlier (-1) de forma segura
def get_clean_embeddings_and_ids(model):
    info = model.get_topic_info()
    # Filtra apenas tópicos reais (>= 0)
    real_topics = info[info['Topic'] != -1]
    ids = real_topics['Topic'].tolist()
    
    # Precisamos pegar os embeddings correspondentes a esses IDs.
    # topic_embeddings_ geralmente inclui o -1 na posição correspondente ou no início.
    # A maneira mais segura é recriar uma lista ordenada baseada nos IDs.
    # O BERTopic armazena embeddings em model.topic_embeddings_. 
    # A ordem segue model.topic_labels_.keys() que geralmente é [-1, 0, 1...]
    
    # Verifica se os embeddings existem (se calculate_probabilities=False pode ser None em versões antigas, 
    # mas o default calcula os centróides dos tópicos)
    all_embs = model.topic_embeddings_
    all_ids = model.get_topic_info()['Topic'].tolist() # IDs na ordem que o BERTopic lista internamente
    
    # Cria mapa ID -> Embedding
    # Assume que all_ids[i] corresponde a all_embs[i] (comportamento padrão do BERTopic)
    id_to_emb = {tid: all_embs[i] for i, tid in enumerate(all_ids)}
    
    clean_embs = []
    clean_ids = []
    
    for tid in ids: 
        if tid in id_to_emb:
            clean_embs.append(id_to_emb[tid])
            clean_ids.append(tid)
            
    return np.array(clean_embs), clean_ids

emb_pre, ids_pre = get_clean_embeddings_and_ids(model_pre)
emb_post, ids_post = get_clean_embeddings_and_ids(model_post)

# Calcula similaridade
if len(emb_pre) > 0 and len(emb_post) > 0:
    sim_matrix = cosine_similarity(emb_pre, emb_post)

    matches = []

    for i, topic_id_pre in enumerate(ids_pre):
        # Acha melhor match no POST
        best_match_idx = np.argmax(sim_matrix[i])
        similarity_score = sim_matrix[i][best_match_idx]
        topic_id_post = ids_post[best_match_idx]
        
        # Pega palavras
        words_pre = ", ".join([w[0] for w in model_pre.get_topic(topic_id_pre)[:5]])
        words_post = ", ".join([w[0] for w in model_post.get_topic(topic_id_post)[:5]])
        
        # Pega %
        count_pre = model_pre.get_topic_info(topic_id_pre)['Count'].values[0]
        count_post = model_post.get_topic_info(topic_id_post)['Count'].values[0]
        
        pct_pre = (count_pre / len(df_pre)) * 100
        pct_post = (count_post / len(df_post)) * 100

        matches.append({
            "Topic_ID_Pre": topic_id_pre,
            "Words_Pre": words_pre,
            "Pct_Pre": round(pct_pre, 2),
            "Topic_ID_Post": topic_id_post,
            "Words_Post": words_post,
            "Pct_Post": round(pct_post, 2),
            "Similarity": round(similarity_score, 4)
        })

    df_matches = pd.DataFrame(matches).sort_values("Similarity", ascending=False)
    
    output_match_path = f"{OUTPUT_DIR}topic_matching_analysis.csv"
    df_matches.to_csv(output_match_path, index=False)

    print("\n=== TABELA DE EQUIVALÊNCIA (TOP MATCHES) ===")
    print(df_matches.head(10).to_string(index=False))
    print(f"\nAnálise completa salva em: {output_match_path}")
else:
    print("ERRO: Não foi possível extrair embeddings para comparação (talvez só tenha restado o tópico -1?).")
    