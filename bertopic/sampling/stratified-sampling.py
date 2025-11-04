import pandas as pd

# Tag em processamento
TAG = "julia"

# Numero de documentos total para amostra final
DESIRED_SAMPLE_SIZE = 30000

input_csv_path = f"../../../{TAG}-query.csv"
output_csv_path = f"../../../{TAG}-sample.csv"

# ----------------------------------------------------

print(f"Carregando arquivo: {input_csv_path}...")
try:
    # Tenta ler com UTF-8 (padrão)
    df = pd.read_csv(input_csv_path, encoding='utf-8')
except UnicodeDecodeError:
    # Se o UTF-8 falhar, tenta o 'latin1' (comum com dados do SO)
    print("Falha no UTF-8, tentando codificação 'latin1'...")
    df = pd.read_csv(input_csv_path, encoding='latin1')
except FileNotFoundError:
    print(f"ERRO: Arquivo não encontrado em {input_csv_path}")
    print("Por favor, verifique o caminho do arquivo e a variável TAG.")
    exit()
except Exception as e:
    print(f"Ocorreu um erro inesperado ao ler o arquivo: {e}")
    exit()

print(f"Carregados {len(df)} posts com sucesso.")


YEAR_COLUMN = 'ano' 

if YEAR_COLUMN not in df.columns:
    print(f"ERRO: A coluna '{YEAR_COLUMN}' não foi encontrada no CSV.")
    print("Verifique sua query SQL (deve ter EXTRACT(YEAR ...)) e exporte o arquivo novamente.")
    exit()

# Remove qualquer linha que possa ter um ano nulo
df = df.dropna(subset=[YEAR_COLUMN])
# Garante que a coluna de ano seja um número inteiro (ex: 2018.0 vira 2018)
df[YEAR_COLUMN] = df[YEAR_COLUMN].astype(int)

print("\n--- Distribuição Original por Ano ---")
print(df[YEAR_COLUMN].value_counts().sort_index())
print("-------------------------------------")

# --- Calcular Fração de Amostragem ---
total_posts = len(df)

if total_posts == 0:
    print("Nenhum dado válido encontrado após o processamento.")
    exit()

# Se o número total de posts for MENOR que o desejado, usamos todos os dados
if total_posts <= DESIRED_SAMPLE_SIZE:
    print(f"Total de posts ({total_posts}) é menor ou igual ao tamanho desejado.")
    print("Usando todos os dados (fração de amostragem = 1.0).")
    sampling_fraction = 1.0
else:
    # Calcula a fração (ex: 30000 / 300000 = 0.1 ou 10%)
    sampling_fraction = DESIRED_SAMPLE_SIZE / total_posts
    print(f"Fração de amostragem: {sampling_fraction:.4f} (para atingir ~{DESIRED_SAMPLE_SIZE} posts)")

print("Executando amostragem estratificada por ano...")

# 1. Agrupa os dados pela coluna 'Ano'.
# 2. Tira uma amostra aleatória (frac=sampling_fraction) de DENTRO de cada grupo.
# 3. random_state=42 torna a amostragem reproduzível.
df_sample = df.groupby(YEAR_COLUMN).sample(
    frac=sampling_fraction,
    random_state=42,
    replace=False  # Garante que não escolheremos o mesmo post duas vezes
)

print("\n--- Distribuição Final da Amostra por Ano ---")
print(df_sample[YEAR_COLUMN].value_counts().sort_index())
print("-------------------------------------------")

print(f"\nTotal de posts na amostra final: {len(df_sample)}")
print(f"Salvando amostra em {output_csv_path}...")

df_sample.to_csv(output_csv_path, index=False, encoding='utf-8')

print("Processo de amostragem concluído com sucesso!")