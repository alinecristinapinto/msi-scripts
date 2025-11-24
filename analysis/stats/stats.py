import pandas as pd
from sqlalchemy import create_engine

TAGS = ['python', 'java', 'c#', 'javascript',  # Alto Recurso
        'r', 'julia', 'bash', 'dart']          # Moderado Recurso

START_DATE = '2018-01-01'
END_DATE = '2025-12-31'

DB_STRING = 'postgresql+psycopg2://USUARIO:SENHA@HOST:PORTA/NOME_DO_BANCO'

# Query para Perguntas (Volume e Score)
sql_questions = """
SELECT 
    DATE_TRUNC('week', p.creationdate) as week_date,
    COUNT(p.id) as q_count,
    SUM(p.score) as q_score
FROM Posts p
JOIN PostTags pt ON p.id = pt.postid
JOIN Tags t ON pt.tagid = t.id
WHERE 
    p.posttypeid = 1 
    AND t.tagname = %(tag)s
    AND p.creationdate BETWEEN %(start)s AND %(end)s
GROUP BY 1
ORDER BY 1;
"""

# Query para Respostas (Volume e Score)
sql_answers = """
SELECT 
    DATE_TRUNC('week', a.creationdate) as week_date,
    COUNT(a.id) as a_count,
    SUM(a.score) as a_score
FROM Posts a
JOIN Posts q ON a.parentid = q.id
JOIN PostTags pt ON q.id = pt.postid
JOIN Tags t ON pt.tagid = t.id
WHERE 
    a.PostTypeId = 2 -- Respostas
    AND t.tagname = %(tag)s
    AND a.creationdate BETWEEN %(start)s AND %(end)s
GROUP BY 1
ORDER BY 1;
"""

def main():
    engine = create_engine(DB_STRING)
    
    print(f"--- Iniciando Extração de Estatísticas ---")
    
    for tag in TAGS:
        print(f"Processando tag: {tag.upper()}...")
        
        params = {'tag': tag, 'start': START_DATE, 'end': END_DATE}
        
        df_q = pd.read_sql(sql_questions, engine, params=params)
        df_q.set_index('week_date', inplace=True)
        
        df_a = pd.read_sql(sql_answers, engine, params=params)
        df_a.set_index('week_date', inplace=True)
        
        df_final = df_q.join(df_a, how='outer').fillna(0)
        
        output_file = f'stats_{tag}.csv'
        df_final.to_csv(output_file)
        print(f" -> Salvo: {output_file}")

    print("\nConcluído!")

if __name__ == "__main__":
    main()