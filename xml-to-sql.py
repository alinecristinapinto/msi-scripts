import xml.etree.ElementTree as ET
from pathlib import Path
import os

# --- CONFIGURAÇÃO ---
INPUT_DIR = Path('../stackoverflow-data/filtered-data-stackoverflow.com')

OUTPUT_SQL_DIR = Path('../stackoverflow-data/sql-stackoverflow.com')
BATCH_SIZE = 500
# --- FIM DA CONFIGURAÇÃO ---

SCHEMA = {
    'filtered_Users.xml': {
        'table_name': 'users',
        'columns': [
            ('Id', 'int'), ('Reputation', 'int'), ('CreationDate', 'timestamp'),
            ('DisplayName', 'varchar'), ('LastAccessDate', 'timestamp'), ('WebsiteUrl', 'varchar'),
            ('Location', 'varchar'), ('AboutMe', 'text'), ('Views', 'int'),
            ('UpVotes', 'int'), ('DownVotes', 'int'), ('ProfileImageUrl', 'varchar'),
            ('EmailHash', 'varchar'), ('AccountId', 'int')
        ]
    },
    'filtered_Tags.xml': {
        'table_name': 'tags',
        'columns': [
            ('Id', 'int'), ('TagName', 'varchar'), ('Count', 'int'),
            ('ExcerptPostId', 'int'), ('WikiPostId', 'int')
        ]
    },
    'filtered_Posts.xml': {
        'table_name': 'posts',
        'columns': [
            ('Id', 'int'), ('PostTypeId', 'int'), ('AcceptedAnswerId', 'int'),
            ('ParentId', 'int'), ('CreationDate', 'timestamp'), ('Score', 'int'),
            ('ViewCount', 'int'), ('Body', 'text'), ('OwnerUserId', 'int'),
            ('LastEditorUserId', 'int'), ('LastEditDate', 'timestamp'),
            ('LastActivityDate', 'timestamp'), ('Title', 'text'), ('Tags', 'text'),
            ('AnswerCount', 'int'), ('CommentCount', 'int'), ('FavoriteCount', 'int'),
            ('ClosedDate', 'timestamp'), ('ContentLicense', 'text')
        ]
    },
    'filtered_Comments.xml': {
        'table_name': 'comments',
        'columns': [
            ('Id', 'int'), ('PostId', 'int'), ('Score', 'int'),
            ('Text', 'text'), ('CreationDate', 'timestamp'), ('UserId', 'int'),
            ('ContentLicense', 'text')
        ]
    },
    'filtered_Votes.xml': {
        'table_name': 'votes',
        'columns': [
            ('Id', 'int'), ('PostId', 'int'), ('VoteTypeId', 'int'),
            ('UserId', 'int'), ('CreationDate', 'date'), ('BountyAmount', 'int')
        ]
    },
    'filtered_PostHistory.xml': {
        'table_name': 'posthistory',
        'columns': [
            ('Id', 'int'), ('PostHistoryTypeId', 'int'), ('PostId', 'int'),
            ('RevisionGUID', 'uuid'), ('CreationDate', 'timestamp'), ('UserId', 'int'),
            ('Comment', 'text'), ('Text', 'text'), ('ContentLicense', 'text')
        ]
    },
    'filtered_PostLinks.xml': {
        'table_name': 'postlinks',
        'columns': [
            ('Id', 'int'), ('CreationDate', 'timestamp'), ('PostId', 'int'),
            ('RelatedPostId', 'int'), ('LinkTypeId', 'int')
        ]
    },
    'filtered_Badges.xml': {
        'table_name': 'badges',
        'columns': [
            ('Id', 'int'), ('UserId', 'int'), ('Name', 'varchar'),
            ('Date', 'timestamp'), ('Class', 'smallint'), ('TagBased', 'boolean')
        ]
    }
}


def format_value(value, dtype):
    """Formata um valor Python para uma string SQL válida."""
    if value is None:
        return 'NULL'
    if dtype in ['text', 'varchar', 'timestamp', 'date', 'uuid']:
        escaped_value = value.replace("'", "''")
        return f"'{escaped_value}'"
    if dtype in ['int', 'smallint']:
        return str(value)
    if dtype == 'boolean':
        return 'TRUE' if value.lower() == 'true' else 'FALSE'
    escaped_value = value.replace("'", "''")
    return f"'{escaped_value}'"

def generate_inserts_for_file(filepath, writer):
    """Lê um arquivo XML e gera instruções INSERT em lote."""
    filename = filepath.name
    if filename not in SCHEMA:
        print(f"Aviso: Nenhum schema definido para '{filename}'. Pulando.")
        return

    schema = SCHEMA[filename]
    table_name = schema['table_name']
    columns = schema['columns']

    col_names_str = ', '.join([col[0].lower() for col in columns])
    
    print(f"Processando '{filename}' para a tabela '{table_name}'...")

    values_batch = []
    total_rows = 0

    context = ET.iterparse(filepath, events=('end',))
    for _, elem in context:
        if elem.tag == 'row':
            row_values = []
            for col_name, col_type in columns:
                value = elem.get(col_name)
                formatted_val = format_value(value, col_type)
                row_values.append(formatted_val)
            
            values_batch.append(f"({', '.join(row_values)})")
            total_rows += 1

            if len(values_batch) >= BATCH_SIZE:
                writer.write(f"INSERT INTO {table_name} ({col_names_str}) VALUES\n")
                writer.write(',\n'.join(values_batch))
                writer.write(';\n\n')
                values_batch.clear()

            elem.clear()

    if values_batch:
        writer.write(f"INSERT INTO {table_name} ({col_names_str}) VALUES\n")
        writer.write(',\n'.join(values_batch))
        writer.write(';\n\n')

    print(f"Processamento de '{filename}' concluído. {total_rows} linhas convertidas.")

if __name__ == '__main__':
    os.makedirs(OUTPUT_SQL_DIR, exist_ok=True)

    # Ordem de processamento para tentar respeitar dependências lógicas
    process_order = [
        'filtered_Users.xml',
        'filtered_Tags.xml',
        'filtered_Posts.xml',
        'filtered_Comments.xml',
        'filtered_Votes.xml',
        'filtered_PostHistory.xml',
        'filtered_PostLinks.xml',
        'filtered_Badges.xml',
    ]

    # Itera sobre cada arquivo para criar um .sql separado
    for filename in process_order:
        filepath = INPUT_DIR / filename
        if filepath.exists():
            # Define o nome do arquivo de saída
            table_name = SCHEMA[filename]['table_name']
            output_sql_path = OUTPUT_SQL_DIR / f"{table_name}_inserts.sql"

            print(f"--- Gerando script para a tabela '{table_name}' ---")
            with open(output_sql_path, 'w', encoding='utf-8') as writer:
                writer.write(f"-- Script de inserção para a tabela {table_name}\n")
                writer.write("BEGIN;\n\n")

                generate_inserts_for_file(filepath, writer)
                
                writer.write("COMMIT;\n")
            
            print(f"Script SQL salvo em '{output_sql_path}'\n")
        else:
            print(f"Aviso: Arquivo '{filepath}' não encontrado. Pulando.\n")
    
    print("--- Processo concluído! Todos os scripts SQL foram gerados. ---")