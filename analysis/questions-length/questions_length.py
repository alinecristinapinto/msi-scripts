import pandas as pd
from sqlalchemy import create_engine
from bs4 import BeautifulSoup
import os

TAG = 'dart'
START_DATE = '2018-01-01'
END_DATE = '2025-12-31'

TEST_MODE = False       
TEST_LIMIT = 1000       

DB_CONNECTION_STR = 'postgresql+psycopg2://USUARIO:SENHA@HOST:PORTA/NOME_DO_BANCO'

execution_mode = "VALIDATION" if TEST_MODE else "FULL"
OUTPUT_FILE = f'metrics_{execution_mode}_{TAG}_{START_DATE[:4]}_{END_DATE[:4]}.csv'

CHUNK_SIZE = 10000  # Batch size 

sql_query = """
SELECT 
    p.id,
    p.creationdate,
    -- Calculate total HTML lines directly in DB for performance
    -- (Calcula linhas totais de HTML direto no banco para performance)
    (LENGTH(p.body) - LENGTH(REPLACE(p.body, CHR(10), ''))) + 1 AS html_line_count,
    p.body
FROM posts p
JOIN posttags pt ON p.id = pt.postid
JOIN tags t ON pt.tagid = t.id
WHERE 
    p.posttypeid = 1 -- Questions only (Apenas perguntas)
    AND t.tagname = %(tag_name)s
    AND p.creationdate BETWEEN %(start_date)s AND %(end_date)s
ORDER BY p.creationdate ASC
"""

if TEST_MODE:
    sql_query += f" LIMIT {TEST_LIMIT}"

def get_code_line_count(html_body):
    if not html_body: 
        return 0
    
    soup = BeautifulSoup(html_body, "html.parser")
    code_lines = 0
    
    for code_block in soup.find_all('code'):
        text = code_block.get_text()
        if text:
            code_lines += text.count('\n') + 1
            
    return code_lines

def main():
    print(f"--- Starting extraction ({execution_mode}) for tag: {TAG.upper()} ---")
    
    engine = create_engine(DB_CONNECTION_STR)
    query_params = {'tag_name': TAG, 'start_date': START_DATE, 'end_date': END_DATE}
    
    chunks = pd.read_sql(sql_query, engine, params=query_params, chunksize=CHUNK_SIZE)
    
    file_mode = 'w' 
    header = True  
    total_processed = 0
    
    for i, df_chunk in enumerate(chunks):
        print(f"Processing batch {i+1}...")
        
        df_chunk['code_line_count'] = df_chunk['body'].apply(get_code_line_count)
        
        cols = ['id', 'creationdate', 'html_line_count', 'code_line_count', 'body']
        final_df = df_chunk[cols]
        
        if not TEST_MODE:
            final_df = final_df.drop(columns=['body'])
        
        # quoting=1 garante que as quebras de linhas HTML são citadas corretamente
        final_df.to_csv(OUTPUT_FILE, index=False, mode=file_mode, header=header, quoting=1)
        
        file_mode = 'a'
        header = False
        total_processed += len(df_chunk)

    print(f"\n--- Feito! ---")
    print(f"Arquivo: {OUTPUT_FILE}")
    print(f"Total de linhas processadas: {total_processed}")
    
    if TEST_MODE:
        print("(Abra o CSV e verifique manualmente se 'code_line_count' bate com o conteúdo dentro das tags <code> no 'body'.)")

if __name__ == "__main__":
    main()