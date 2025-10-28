import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as mticker
from pathlib import Path

CSV_PATH = '../post-sums-query.csv' 
OUT_DIR = Path("./poutput")
OUT_DIR.mkdir(parents=True, exist_ok=True)

sns.set_style("whitegrid")

def k_m_formatter(x, pos):
    """Formata o eixo Y para 'K' (milhares) ou 'M' (milhões)"""
    if x >= 1_000_000:
        return f'{x/1_000_000:.1f}M'
    if x >= 1_000:
        return f'{x/1_000:.0f}K'
    return f'{x:.0f}'

def plot_projection(df_annual_agg: pd.DataFrame, metric_col: str, title: str, filename: Path):
    """
    Recebe um DataFrame agregado (com 5 pontos) e gera um gráfico de projeção.
    
    Args:
        df_annual_agg: DataFrame com colunas 'year' e a 'metric_col' (ex: 'questions').
        metric_col: O nome da coluna da métrica (ex: 'questions', 'answers').
        title: O título do gráfico.
        filename: O caminho completo para salvar o .png.
    """
    print(f"Gerando projeção para: {title}...")

    # --- 2. Modelagem (Regressão) ---
    X = df_annual_agg['year']
    Y = df_annual_agg[metric_col]
    
    # Modelo 1: Linear (Grau 1)
    model_linear = np.poly1d(np.polyfit(X, Y, 1))

    # Modelo 2: Polinomial (Grau 2)
    model_poly2 = np.poly1d(np.polyfit(X, Y, 2))

    # --- 3. Geração de Dados para Plotagem ---
    years_historico = np.arange(2018, 2023)
    years_projecao = np.arange(2023, 2026)
    years_full = np.arange(2018, 2026)

    # Criar DataFrame para plotagem das linhas de projeção
    df_plot_lines = pd.DataFrame({
        'Ano': years_full,
        'Projeção Linear': model_linear(years_full),
        'Projeção Polinomial (Grau 2)': model_poly2(years_full)
    })
    
    # Reformatar (melt) para facilitar o plot com Seaborn
    df_plot_melted = df_plot_lines.melt('Ano', var_name='Modelo de Projeção', value_name='Valor')
    
    # --- 4. Geração do Gráfico ---
    plt.figure(figsize=(12, 7))
    
    # 1. Plotar os pontos reais (Obtido)
    sns.scatterplot(
        data=df_annual_agg,
        x='year',
        y=metric_col,
        label='Obtido (Real)',
        s=150,
        color='blue',
        zorder=10
    )
    
    # 2. Plotar as linhas de projeção
    sns.lineplot(
        data=df_plot_melted,
        x='Ano',
        y='Valor',
        hue='Modelo de Projeção',
        style='Modelo de Projeção',
        dashes=True,
        linewidth=2.5
    )
    
    # 3. Adicionar linha vertical
    plt.axvline(x=2022.5, color='red', linestyle=':', linewidth=2, label='Início da Projeção')

    plt.title(title, fontsize=16)
    plt.xlabel('Ano', fontsize=12)
    plt.ylabel(f'Total de {metric_col.capitalize()}', fontsize=12)
    plt.xticks(years_full)
    
    # Formatar eixo Y
    plt.gca().yaxis.set_major_formatter(mticker.FuncFormatter(k_m_formatter))
    
    # Garantir que o eixo Y não vá abaixo de zero
    current_ylim = plt.gca().get_ylim()
    plt.ylim(bottom=max(0, current_ylim[0])) # Define o limite inferior como 0 se for negativo
    
    plt.legend()
    plt.tight_layout()

    plt.savefig(filename, dpi=150)
    plt.close()
    print(f"✅ Gráfico salvo: {filename}")


# --- SCRIPT PRINCIPAL ---
def main():
    try:
        df = pd.read_csv(CSV_PATH)
    except FileNotFoundError:
        print(f"Erro: Arquivo '{CSV_PATH}' não encontrado.")
        print("Por favor, coloque o arquivo CSV no mesmo diretório do script.")
        return

    # --- 1. Preparação dos Dados Base ---
    print(f"Carregando dados de '{CSV_PATH}'...")
    df['month_start'] = pd.to_datetime(df['month_start'])
    
    # Filtrar apenas o período histórico (2018-2022)
    df_hist = df[
        (df['month_start'] >= '2018-01-01') & (df['month_start'] < '2023-01-01')
    ].copy()
    
    # Extrair o ano (só precisamos fazer isso uma vez)
    df_hist['year'] = df_hist['month_start'].dt.year

    # --- 2. Definição dos 4 Cenários ---
    scenarios = [
        {
            'group_name': 'alto_recurso',
            'metric': 'questions',
            'title_name': 'Alto Recurso - Perguntas'
        },
        {
            'group_name': 'alto_recurso',
            'metric': 'answers',
            'title_name': 'Alto Recurso - Respostas'
        },
        {
            'group_name': 'baixo_moderado',
            'metric': 'questions',
            'title_name': 'Moderado Recurso - Perguntas'
        },
        {
            'group_name': 'baixo_moderado',
            'metric': 'answers',
            'title_name': 'Moderado Recurso - Respostas'
        }
    ]

    print(f"\nIniciando geração dos {len(scenarios)} gráficos de projeção...")

    # --- 3. Loop de Geração ---
    for scenario in scenarios:
        group = scenario['group_name']
        metric = scenario['metric']
        title_name = scenario['title_name']
        
        # 1. Filtrar o grupo
        df_group = df_hist[df_hist['group_name'] == group]
        
        # 2. Agregar os 5 pontos anuais para a métrica
        df_annual_agg = df_group.groupby('year')[metric].sum().reset_index()
        
        # 3. Definir Título e Nome do Arquivo
        title = f'Projeção (2023-2025): {title_name}'
        filename = OUT_DIR / f'projection_plot_{group}_{metric}.png'
        
        # 4. Chamar a função de plotagem
        plot_projection(df_annual_agg, metric, title, filename)
        
    print("\n--- Finalizado ---")
    print(f"Todos os {len(scenarios)} gráficos foram salvos em: {OUT_DIR.resolve()}")

if __name__ == "__main__":
    main()