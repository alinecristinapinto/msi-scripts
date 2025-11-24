import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from bertopic import BERTopic
import os

# MAPEAMENTO DE CATEGORIAS -> Dynamic Topic Modeling com redução de outliers 
MASTER_CATEGORY_MAPPING = {
    "Frontend_and_UI": {
        "description": "Construção de Interface, Widgets, DOM e Layout",
        "mapping": {
            "javascript": [0, 3, 4, 6],
            "dart": [1, 4, 6],
            "java": [9],
            "c#": [8, 9],
            "r": [5],
        }
    },
    "Data_Handling_and_Manipulation": {
        "description": "Manipulação de Arquivos, JSON, Regex e Dataframes",
        "mapping": {
            "python": [8],
            "javascript": [1],
            "c#": [1],
            "r": [1, 6, 7],
            "bash": [0, 1, 8],
            "dart": [0],
            "julia": [1],
        }
    },
    "DevOps_Build_and_Automation": {
        "description": "Configuração de Projeto, Docker, CI/CD e Compilação",
        "mapping": {
            "python": [5, 6, 7],
            "java": [0, 7],
            "bash": [1, 5, 7, 9],
            "dart": [2, 3],
            "r": [3, 7],
            "julia": [4, 7],
        }
    },
    "Scientific_Computing_and_AI": {
        "description": "Matemática, Machine Learning e Otimização",
        "mapping": {
            "python": [0, 9],
            "julia": [0, 6, 9],
            "r": [5, 9],
        }
    },
    "Data_Visualization": {
        "description": "Plotagem de Gráficos e Estilização",
        "mapping": {
            "python": [3],
            "r": [0, 2, 4, 8],
        }
    },
    "Concurrency_and_Parallelism": {
        "description": "Threads, Async/Await e Processamento Paralelo",
        "mapping": {
            "java": [4],
            "javascript": [2],
            "bash": [3],
            "julia": [2],
        }
    },
    "Networking_and_Systems": {
        "description": "Redes, Sockets, I/O e Protocolos",
        "mapping": {
            "python": [4],
            "java": [6],
            "c#": [5],
            "bash": [4, 6],
            "dart": [9],
        }
    },
    "Mobile_Development": {
        "description": "Desenvolvimento nativo e cross-platform para Celular",
        "mapping": {
            "java": [0, 7, 9],
            "dart": [0, 2, 3],
            "javascript": [8],
            "c#": [7],
        }
    }
}

BASE_DIR = "../../../" 

def get_combined_text(lang, topic_ids):
    csv_path = f"{BASE_DIR}{lang}-no-code.csv"
    model_path = f"{BASE_DIR}final_models/{lang}_model"
    
    if not os.path.exists(csv_path) or not os.path.exists(model_path):
        print(f" ERRO ARQUIVO: Não achei CSV ou Modelo para {lang}")
        return ""
    
    try:
        df = pd.read_csv(csv_path)
        TEXT_COLUMN = "cleanbody"
        df = df.dropna(subset=[TEXT_COLUMN])
        df = df[df[TEXT_COLUMN].str.strip().astype(bool)]
        docs = df[TEXT_COLUMN].tolist()
        
        topic_model = BERTopic.load(model_path)
        
        # IMPORTANTE: Calcula os tópicos para os documentos carregados
        topics, _ = topic_model.transform(docs)
        
        selected_docs = [doc for doc, topic in zip(docs, topics) if topic in topic_ids]

        count = len(selected_docs)
        total_len = sum([len(d) for d in selected_docs])
        print(f"{lang}: IDs procurados {topic_ids} -> Encontrados {count} docs (Total chars: {total_len})")
        
        if count == 0:
            return ""
            
        return " ".join(selected_docs)
        
    except Exception as e:
        print(f"ERRO EXECUÇÃO em {lang}: {e}")
        return ""

print("Carregando modelo SentenceTransformer...")
embedder = SentenceTransformer("all-MiniLM-L6-v2")

for cat_key, cat_data in MASTER_CATEGORY_MAPPING.items():
    cat_desc = cat_data["description"]
    topic_mapping = cat_data["mapping"]
    
    print(f"\n========================================================")
    print(f"PROCESSANDO: {cat_key}")
    print(f"========================================================")
    
    corpus = []
    valid_langs = []
    
    for lang, topic_ids in topic_mapping.items():
        text = get_combined_text(lang, topic_ids)
        
        if text and len(text.strip()) > 10: 
            corpus.append(text)
            valid_langs.append(lang)
        else:
            print(f"{lang}: Texto vazio ou insuficiente para gerar embedding.")
            
    if len(corpus) < 2:
        print("  [!] Menos de 2 linguagens válidas para este gráfico. Pulando.")
        continue
        
    print("  -> Calculando Similaridades...")
    
    # 1. TF-IDF
    vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
    tfidf_matrix = vectorizer.fit_transform(corpus)
    sim_lexical = cosine_similarity(tfidf_matrix)
    
    # 2. BERT
    embeddings = embedder.encode(corpus)
    sim_semantic = cosine_similarity(embeddings)
    
    print("  -> Gerando Gráfico...")
    fig, axes = plt.subplots(1, 2, figsize=(18, 7))
    sns.set_context("notebook", font_scale=1.1)
    
    # Plot Léxico
    sns.heatmap(sim_lexical, annot=True, fmt=".2f", cmap="Blues", 
                xticklabels=valid_langs, yticklabels=valid_langs, ax=axes[0], vmin=0, vmax=1)
    axes[0].set_title(f"Similaridade LÉXICA (Palavras)\n{cat_key}")
    
    # Plot Semântico
    sns.heatmap(sim_semantic, annot=True, fmt=".2f", cmap="Greens", 
                xticklabels=valid_langs, yticklabels=valid_langs, ax=axes[1], vmin=0, vmax=1)
    axes[1].set_title(f"Similaridade SEMÂNTICA (Conceito)\n{cat_key}")
    
    filename = f"{BASE_DIR}heatmap_{cat_key}.png"
    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    plt.close()
    print(f"Salvo: {filename}")

print("\n--- FIM ---")