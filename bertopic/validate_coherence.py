import pandas as pd
import gensim.corpora as corpora
from gensim.models.coherencemodel import CoherenceModel
from bertopic import BERTopic
import plotly.graph_objects as go
import os

def main():
    TAG = "dart"
    
    BASE_DIR = "../../"
    INPUT_CSV_PATH = f"{BASE_DIR}{TAG}-no-code.csv"
    MODEL_PATH = f"{BASE_DIR}models/{TAG}_model"
    
    OUTPUT_RESULTS_DIR = f"{BASE_DIR}models/{TAG}_results"
    os.makedirs(OUTPUT_RESULTS_DIR, exist_ok=True)

    print(f"--- VALIDANDO COERÊNCIA PARA: {TAG} ---")
    try:
        df = pd.read_csv(INPUT_CSV_PATH)
        df = df.dropna(subset=['cleanbody'])
        docs = df['cleanbody'].tolist()
    except FileNotFoundError:
        print("Erro: Arquivo de dados não encontrado.")
        return

    print("Carregando modelo BERTopic...")
    topic_model = BERTopic.load(MODEL_PATH)

    print("Tokenizando documentos para cálculo de coerência...")
    cleaned_docs = topic_model._preprocess_text(docs)
    vectorizer = topic_model.vectorizer_model
    analyzer = vectorizer.build_analyzer()

    tokens = [analyzer(doc) for doc in cleaned_docs]
    dictionary = corpora.Dictionary(tokens)

    topics = topic_model.get_topics()
    topic_words = []

    valid_topics = [t for t in topics.keys() if t != -1]
    valid_topics.sort()

    for topic_id in valid_topics:
        words = [word for word, _ in topic_model.get_topic(topic_id)]
        topic_words.append(words)

    print(f"Calculando coerência para {len(topic_words)} tópicos...")

    coherence_model = CoherenceModel(
        topics=topic_words, 
        texts=tokens, 
        dictionary=dictionary, 
        coherence='c_v'
    )

    coherence_score = coherence_model.get_coherence()
    coherence_per_topic = coherence_model.get_coherence_per_topic()

    print(f"\nResultados para {TAG}:")
    print(f"Coerência Global (Média C_v): {coherence_score:.4f}")

    df_coherence = pd.DataFrame({
        "Topic": valid_topics,
        "Coherence_Score": coherence_per_topic,
        "Top_Words": [", ".join(words) for words in topic_words]
    })

    output_csv = os.path.join(OUTPUT_RESULTS_DIR, f"{TAG}_coherence_scores.csv")
    df_coherence.to_csv(output_csv, index=False)
    print(f"Tabela de coerência salva em: {output_csv}")

    fig = go.Figure(go.Bar(
        x=[f"Tópico {t}" for t in valid_topics],
        y=coherence_per_topic,
        text=[f"{s:.2f}" for s in coherence_per_topic],
        textposition='auto',
        marker_color='indianred'
    ))

    fig.update_layout(
        title=f"Score de Coerência por Tópico ({TAG}) - Média: {coherence_score:.3f}",
        yaxis_title="Coerência (C_v)",
        xaxis_title="Tópicos",
        template="plotly_white"
    )

    output_html = os.path.join(OUTPUT_RESULTS_DIR, f"{TAG}_coherence_plot.html")
    fig.write_html(output_html)
    print(f"Gráfico salvo em: {output_html}")

    print("\n--- COMO INTERPRETAR ---")
    print("0.3 - 0.4: Razoável (Comum para textos curtos/técnicos)")
    print("0.4 - 0.5: Bom")
    print("0.5 - 0.7: Excelente")
    print("> 0.7: Perfeito (Raro em dados reais)")

if __name__ == "__main__":
    main()