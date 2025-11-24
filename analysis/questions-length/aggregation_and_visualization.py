import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import glob
import os
import numpy as np

INPUT_FOLDER = '.' 
CHATGPT_LAUNCH = pd.to_datetime('2022-11-30')

GROUP_POPULAR = ['java', 'c#', 'python', 'javascript']
GROUP_NICHE = ['julia', 'bash', 'r', 'dart']

sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = (14, 7)


def process_file(filepath):
    filename = os.path.basename(filepath)
    try:
        tag_candidate = filename.split('_')[2]
    except:
        tag_candidate = "unknown"

    print(f"Lendo: {filename} (Tag detectada: {tag_candidate})...")
    
    df = pd.read_csv(filepath)
    df['creationdate'] = pd.to_datetime(df['creationdate'])
    
    # --- Normalização em log ---
    # np.log(x + 1) para evitar erro de log(0)
    df['log_html_len'] = np.log(df['html_line_count'] + 1)
    df['log_code_len'] = np.log(df['code_line_count'] + 1)
    
    df.set_index('creationdate', inplace=True)
    
    # Agrega por SEMANA ('W')
    df_weekly = df.resample('W').agg({
        'id': 'count',                
        'html_line_count': 'mean',    
        'log_html_len': 'mean',       
        'code_line_count': 'mean',    
        'log_code_len': 'mean'           
    })
    
    df_weekly['tag'] = tag_candidate
    df_weekly = df_weekly.iloc[:-1]
    
    return df_weekly

files = glob.glob(os.path.join(INPUT_FOLDER, 'metrics_FULL_*.csv'))
all_data = []

for f in files:
    df_processed = process_file(f)
    all_data.append(df_processed)

if not all_data:
    print("ERRO: Nenhum arquivo encontrado! Gere os CSVs primeiro.")
    exit()

df_final = pd.concat(all_data)
df_final = df_final.reset_index()

df_final = df_final[df_final['tag'].isin(GROUP_POPULAR + GROUP_NICHE)]

def plot_comparison(data, tags, metric, title, ylabel, filename_suffix):
    subset = data[data['tag'].isin(tags)]
    
    if subset.empty:
        print(f"Aviso: Nenhuma dado encontrado para o grupo {tags}")
        return

    plt.figure()
    
    sns.lineplot(data=subset, x='creationdate', y=metric, hue='tag', linewidth=2, alpha=0.8)
    plt.axvline(CHATGPT_LAUNCH, color='red', linestyle='--', label='ChatGPT Launch', linewidth=1.5)
    
    plt.title(title, fontsize=16)
    plt.ylabel(ylabel, fontsize=12)
    plt.xlabel('Período', fontsize=12)
    plt.legend(title='Linguagem')
    
    savename = f"plot_{filename_suffix}.png"

    plt.savefig(savename)
    print(f"Gráfico salvo: {savename}")
    
    plt.close() 

# --- PARTE 1: TAMANHO DA PERGUNTA (HTML) ---
plot_comparison(
    df_final, GROUP_POPULAR, 
    metric='html_line_count',
    title='[Alto Recurso] Tamanho da Pergunta (DADOS BRUTOS)',
    ylabel='Média de Linhas (HTML)',
    filename_suffix='popular_html_raw'
)

plot_comparison(
    df_final, GROUP_POPULAR, 
    metric='log_html_len',
    title='[Alto Recurso] Tamanho da Pergunta',
    ylabel='Média do Log (número de linhas)',
    filename_suffix='popular_html_log'
)

plot_comparison(
    df_final, GROUP_NICHE, 
    metric='html_line_count',
    title='[Moderado Recurso] Tamanho da Pergunta (DADOS BRUTOS)',
    ylabel='Média de Linhas (HTML)',
    filename_suffix='niche_html_raw'
)

plot_comparison(
    df_final, GROUP_NICHE, 
    metric='log_html_len',
    title='[Moderado Recurso] Tamanho da Pergunta',
    ylabel='Média do Log (número de linhas)',
    filename_suffix='niche_html_log'
)

# --- PARTE 2: TAMANHO DO CÓDIGO (CODE) ---
plot_comparison(
    df_final, GROUP_POPULAR, 
    metric='code_line_count',
    title='[Alto Recurso] Tamanho do Código (DADOS BRUTOS)',
    ylabel='Média de Linhas de Código',
    filename_suffix='popular_code_raw'
)

plot_comparison(
    df_final, GROUP_POPULAR, 
    metric='log_code_len',
    title='[Alto Recurso] Tamanho do Código',
    ylabel='Média do Log(Code Lines)',
    filename_suffix='popular_code_log'
)

plot_comparison(
    df_final, GROUP_NICHE, 
    metric='code_line_count',
    title='[Moderado Recurso] Tamanho do Código (DADOS BRUTOS)',
    ylabel='Média de Linhas de Código',
    filename_suffix='niche_code_raw'
)

plot_comparison(
    df_final, GROUP_NICHE, 
    metric='log_code_len',
    title='[Moderado Recurso] Tamanho do Código',
    ylabel='Média do Log(Code Lines)',
    filename_suffix='niche_code_log'
)
