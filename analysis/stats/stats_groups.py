import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ==========================================
# 1. CONFIGURAÇÕES
# ==========================================
CHATGPT_LAUNCH = pd.to_datetime('2022-11-30')

# Definição dos Grupos
GROUPS = {
    'Alto Recurso': ['python', 'java', 'c#', 'javascript'],
    'Moderado Recurso': ['r', 'julia', 'bash', 'dart']
}

sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)

# ==========================================
# 2. PROCESSAMENTO
# ==========================================
def load_and_sum_group(group_tags):
    df_group_total = None
    
    for tag in group_tags:
        filepath = f'stats_{tag}.csv'
        if not os.path.exists(filepath):
            print(f"AVISO: Arquivo {filepath} não encontrado. Certifique-se de rodar o extract_stats.py antes.")
            continue
            
        df = pd.read_csv(filepath)
        df['week_date'] = pd.to_datetime(df['week_date'])
        df.set_index('week_date', inplace=True)
        
        # Soma acumulativa do grupo (agora somamos q_score e a_score individualmente)
        if df_group_total is None:
            df_group_total = df
        else:
            df_group_total = df_group_total.add(df, fill_value=0)
            
    return df_group_total

# ==========================================
# 3. PLOTAGEM (ATUALIZADO PARA 4 LINHAS)
# ==========================================
def plot_group_metrics(df, group_name):
    if df is None or df.empty:
        return

    # Opcional: Re-amostrar para MENSAL ('ME') se quiser limpar o visual das bolinhas
    # df = df.resample('ME').sum()

    # Preparar dados para o Seaborn (Formato Longo)
    
    # 1. Volume de Perguntas
    q_vol = df[['q_count']].rename(columns={'q_count': 'Valor'})
    q_vol['Métrica'] = 'Volume: Perguntas'
    
    # 2. Volume de Respostas
    a_vol = df[['a_count']].rename(columns={'a_count': 'Valor'})
    a_vol['Métrica'] = 'Volume: Respostas'
    
    # 3. Score de Perguntas (NOVO)
    q_score = df[['q_score']].rename(columns={'q_score': 'Valor'})
    q_score['Métrica'] = 'Score: Perguntas'

    # 4. Score de Respostas (NOVO)
    a_score = df[['a_score']].rename(columns={'a_score': 'Valor'})
    a_score['Métrica'] = 'Score: Respostas'
    
    # Junta as 4 métricas
    plot_data = pd.concat([q_vol, a_vol, q_score, a_score]).reset_index()
    
    # Plot
    plt.figure()
    
    # Adicionei marker='o' e markevery=12 (aprox 3 meses) para as bolinhas não ficarem poluídas
    sns.lineplot(
        data=plot_data, 
        x='week_date', 
        y='Valor', 
        hue='Métrica', 
        linewidth=2.0,
        marker='o',
        markevery=12 
    )
    
    plt.axvline(CHATGPT_LAUNCH, color='red', linestyle='--', label='ChatGPT Launch')
    
    plt.title(f'Grupo: {group_name} (Volume vs. Score)', fontsize=16)
    plt.ylabel('Quantidade / Score', fontsize=12)
    plt.xlabel('Período', fontsize=12)
    plt.legend(title='Indicador')
    
    # Salva
    filename = f"plot_metrics_split_{group_name.replace(' ', '_').lower()}.png"
    plt.savefig(filename)
    print(f"Gráfico salvo: {filename}")
    plt.close()

# ==========================================
# 4. EXECUÇÃO
# ==========================================
for group_name, tags in GROUPS.items():
    print(f"Gerando gráfico (split scores) para: {group_name}...")
    df_group = load_and_sum_group(tags)
    plot_group_metrics(df_group, group_name)

print("Processo concluído!")