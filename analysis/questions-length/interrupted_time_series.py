import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
import glob
import os

INPUT_FOLDER = '.'
CHATGPT_START_DATE = pd.to_datetime('2022-11-30')

METRICS_TO_ANALYZE = ['log_html_len', 'log_code_len']

def prepare_data(filepath):
    filename = os.path.basename(filepath)
    try:
        tag = filename.split('_')[2]
    except:
        tag = "unknown"

    df = pd.read_csv(filepath)
    df['creationdate'] = pd.to_datetime(df['creationdate'])

    df['log_html_len'] = np.log(df['html_line_count'] + 1)
    df['log_code_len'] = np.log(df['code_line_count'] + 1)
    
    df.set_index('creationdate', inplace=True)
    
    df_weekly = df.resample('W').agg({
        'log_html_len': 'mean',
        'log_code_len': 'mean'
    }).iloc[:-1] 
    
    df_weekly.reset_index(inplace=True)
    
    df_weekly['time_trend'] = df_weekly.index
    df_weekly['intervention'] = (df_weekly['creationdate'] >= CHATGPT_START_DATE).astype(int)
    
    # Time After Intervention (Interaction)
    df_weekly['time_after'] = df_weekly['time_trend'] - df_weekly[df_weekly['intervention'] == 1]['time_trend'].min()
    df_weekly['time_after'] = df_weekly['time_after'].fillna(0)
    df_weekly.loc[df_weekly['intervention'] == 0, 'time_after'] = 0
    
    return df_weekly, tag


files = glob.glob(os.path.join(INPUT_FOLDER, 'metrics_FULL_*.csv'))
results = []

print(f"--- Rodando regressão: {METRICS_TO_ANALYZE} ---")

for f in files:
    data, tag = prepare_data(f)
    
    if data.empty: continue
    
    for metric in METRICS_TO_ANALYZE:
        formula = f"{metric} ~ time_trend + intervention + time_after"
        
        try:
            model = smf.ols(formula=formula, data=data).fit()
            
            beta3 = model.params['time_after']
            p_value = model.pvalues['time_after']
            r_squared = model.rsquared
            
            results.append({
                'Language': tag,
                'Metric': metric,  
                'Trend_Change (Beta3)': round(beta3, 5),
                'P_Value': round(p_value, 5),
                'Significant?': 'YES' if p_value < 0.05 else 'NO',
                'R_Squared': round(r_squared, 3)
            })
            
        except Exception as e:
            print(f"Erro de processamento de {tag} para {metric}: {e}")


results_df = pd.DataFrame(results)

results_df.sort_values(by=['Metric', 'Trend_Change (Beta3)'], ascending=[True, False], inplace=True)

print("\n=== Resultados (Consolidada) ===")
print(results_df.to_string(index=False))

results_df.to_csv('regression_results_full.csv', index=False)
print("\nFinalizado")