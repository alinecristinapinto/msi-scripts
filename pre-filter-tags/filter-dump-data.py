import xml.etree.ElementTree as ET
import os
from pathlib import Path

# --- CONFIGURAÇÃO ---
TARGET_TAGS = {'r', 'julia', 'bash', 'dart', 'python', 'javascript', 'java', 'c#'}

START_DATE = '2018-01-01T00:00:00.000'
END_DATE = '2026-01-01T00:00:00.000' 

INPUT_DIR = Path('../stackoverflow-data/stackoverflow.com')
OUTPUT_DIR = Path('../stackoverflow-data/filtered-data-stackoverflow.com')
# --- FIM DA CONFIGURAÇÃO ---

def create_output_dir():
    """Cria a pasta de saída se ela não existir."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Arquivos filtrados serão salvos em: '{OUTPUT_DIR}'")

def write_xml_header(writer, root_tag):
    """Escreve o cabeçalho XML e a tag raiz de abertura."""
    writer.write('<?xml version="1.0" encoding="utf-8"?>\n')
    writer.write(f'<{root_tag}>\n')

def write_xml_footer(writer, root_tag):
    """Escreve a tag raiz de fechamento."""
    writer.write(f'</{root_tag}>\n')

def is_date_in_range(date_str):
    """Verifica se uma string de data está no intervalo definido."""
    if not date_str:
        return False
    # A comparação de strings funciona porque o formato é ISO 8601 (AAAA-MM-DD)
    return START_DATE <= date_str < END_DATE

def filter_tags():
    """
    Filtra o arquivo Tags.xml, salvando as linhas das tags alvo.
    """
    print("Processando Tags.xml...")
    source_file = INPUT_DIR / 'Tags.xml'
    output_file = OUTPUT_DIR / 'filtered_Tags.xml'
    
    found_tags = set()
    count = 0

    with open(output_file, 'w', encoding='utf-8') as writer:
        write_xml_header(writer, 'tags')
        
        context = ET.iterparse(source_file, events=('end',))
        for _, elem in context:
            if elem.tag == 'row':
                tag_name = elem.get('TagName')
                if tag_name and tag_name.lower() in TARGET_TAGS:
                    writer.write('  ' + ET.tostring(elem, encoding='unicode'))
                    found_tags.add(tag_name)
                    count += 1
                elem.clear()
        
        write_xml_footer(writer, 'tags')
    
    print(f"Tags.xml processado. {count} tags relevantes encontradas e salvas em '{output_file}'.\n")
    return found_tags

def filter_posts(relevant_tags):
    """
    Filtra Posts.xml com base nas tags e no intervalo de datas, incluindo perguntas e suas respostas.
    Utiliza uma abordagem de duas passagens para garantir que as respostas sejam incluídas.
    """
    print(f"Processando Posts.xml para o período {START_DATE[:4]}-{END_DATE[:4]} (isso pode demorar bastante)...")
    source_file = INPUT_DIR / 'Posts.xml'
    output_file = OUTPUT_DIR / 'filtered_Posts.xml'

    tag_search_patterns = [f"<{tag}>" for tag in relevant_tags]
    
    # --- ETAPA 1: Encontrar IDs de todas as perguntas relevantes ---
    print("Etapa 1/2: Identificando IDs de perguntas relevantes...")
    relevant_question_ids = set()
    context = ET.iterparse(source_file, events=('end',))
    for _, elem in context:
        if elem.tag == 'row':
            # Filtra apenas por perguntas (PostTypeId=1) que tenham as tags desejadas
            if elem.get('PostTypeId') == '1':
                tags_str = elem.get('Tags', '')
                if any(pattern in tags_str for pattern in tag_search_patterns):
                    creation_date = elem.get('CreationDate')
                    if is_date_in_range(creation_date):
                        relevant_question_ids.add(elem.get('Id'))
            elem.clear()
    print(f"Encontradas {len(relevant_question_ids)} perguntas relevantes.")

    # --- ETAPA 2: Filtrar e escrever perguntas e suas respostas ---
    print("Etapa 2/2: Escrevendo perguntas e respostas correspondentes...")
    relevant_post_ids = set()
    relevant_user_ids = set()
    count = 0
    
    with open(output_file, 'w', encoding='utf-8') as writer:
        write_xml_header(writer, 'posts')
        
        context = ET.iterparse(source_file, events=('end',))
        for _, elem in context:
            if elem.tag == 'row':
                post_id = elem.get('Id')
                parent_id = elem.get('ParentId')
                
                # Condição: O post é uma pergunta relevante OU é uma resposta de uma pergunta relevante
                is_relevant_question = post_id in relevant_question_ids
                is_relevant_answer = parent_id in relevant_question_ids

                if is_relevant_question or is_relevant_answer:
                    # A data da resposta também deve estar no intervalo, caso queira filtrar
                    # Aqui, incluímos todas as respostas de perguntas relevantes, independentemente da data da resposta
                    writer.write('  ' + ET.tostring(elem, encoding='unicode'))
                    
                    if post_id:
                        relevant_post_ids.add(post_id)
                    
                    owner_id = elem.get('OwnerUserId')
                    if owner_id:
                        relevant_user_ids.add(owner_id)
                        
                    last_editor_id = elem.get('LastEditorUserId')
                    if last_editor_id:
                        relevant_user_ids.add(last_editor_id)

                    count += 1
            elem.clear()

        write_xml_footer(writer, 'posts')

    print(f"Posts.xml processado. {count} posts relevantes (perguntas e respostas) salvos em '{output_file}'.")
    print(f"Encontrados {len(relevant_post_ids)} IDs de posts e {len(relevant_user_ids)} IDs de usuários.\n")
    return relevant_post_ids, relevant_user_ids

def create_post_tags_from_files():
    """
    Cria o arquivo filtered_PostTags.xml a partir dos posts e tags já filtrados.
    """
    print("Gerando PostTags a partir de Posts.xml e Tags.xml...")
    tags_filepath = OUTPUT_DIR / 'filtered_Tags.xml'
    posts_filepath = OUTPUT_DIR / 'filtered_Posts.xml'
    output_filepath = OUTPUT_DIR / 'filtered_PostTags.xml'

    if not tags_filepath.exists() or not posts_filepath.exists():
        print(f"Aviso: Arquivos necessários '{tags_filepath.name}' ou '{posts_filepath.name}' não encontrados. Pulando.")
        return

    # Etapa 1: Mapear nome da tag para seu ID
    tag_to_id_map = {}
    context = ET.iterparse(tags_filepath, events=('end',))
    for _, elem in context:
        if elem.tag == 'row':
            tag_name = elem.get('TagName')
            tag_id = elem.get('Id')
            if tag_name and tag_id:
                tag_to_id_map[tag_name] = tag_id
        elem.clear()
    
    print(f"Mapeamento de {len(tag_to_id_map)} tags para IDs criado.")

    # Etapa 2: Ler os posts, extrair tags e escrever as relações
    count = 0
    with open(output_filepath, 'w', encoding='utf-8') as writer:
        write_xml_header(writer, 'posttags')
        
        context = ET.iterparse(posts_filepath, events=('end',))
        for _, elem in context:
            if elem.tag == 'row':
                post_id = elem.get('Id')
                tags_str = elem.get('Tags')

                if post_id and tags_str:
                    # Extrai os nomes das tags da string, ex: "<python><pandas>" -> ["python", "pandas"]
                    tag_names = tags_str.replace('><', ' ').replace('<', '').replace('>', '').split()
                    
                    for name in tag_names:
                        if name in tag_to_id_map:
                            tag_id = tag_to_id_map[name]
                            # Escreve a linha no formato XML para a tabela de junção
                            writer.write(f'  <row PostId="{post_id}" TagId="{tag_id}" />\n')
                            count += 1
            elem.clear()

        write_xml_footer(writer, 'posttags')

    print(f"filtered_PostTags.xml gerado com {count} relações Post-Tag.\n")
def filter_file_by_post_id(filename, relevant_post_ids):
    """
    Filtra arquivos (Comments, Votes, PostHistory) por PostId e data.
    """
    print(f"Processando {filename}...")
    source_file = INPUT_DIR / filename
    output_file = OUTPUT_DIR / f'filtered_{filename}'
    root_tag = filename.lower().replace('.xml', '')

    found_user_ids = set()
    count = 0

    if not source_file.exists():
        print(f"Arquivo {source_file} não encontrado. Pulando.")
        return found_user_ids

    with open(output_file, 'w', encoding='utf-8') as writer:
        write_xml_header(writer, root_tag)
        
        context = ET.iterparse(source_file, events=('end',))
        for _, elem in context:
            if elem.tag == 'row':
                if elem.get('PostId') in relevant_post_ids:
                    creation_date = elem.get('CreationDate')
                    if is_date_in_range(creation_date):
                        writer.write('  ' + ET.tostring(elem, encoding='unicode'))
                        
                        user_id = elem.get('UserId') or elem.get('OwnerUserId')
                        if user_id:
                            found_user_ids.add(user_id)
                        count += 1
                elem.clear()

        write_xml_footer(writer, root_tag)
    
    print(f"{filename} processado. {count} linhas relevantes salvas em '{output_file}'.\n")
    return found_user_ids

def filter_post_links(relevant_post_ids):
    """Filtra PostLinks.xml por PostId e data."""
    print("Processando PostLinks.xml...")
    source_file = INPUT_DIR / 'PostLinks.xml'
    output_file = OUTPUT_DIR / 'filtered_PostLinks.xml'
    
    count = 0
    
    if not source_file.exists():
        print(f"Arquivo {source_file} não encontrado. Pulando.")
        return

    with open(output_file, 'w', encoding='utf-8') as writer:
        write_xml_header(writer, 'postlinks')
        
        context = ET.iterparse(source_file, events=('end',))
        for _, elem in context:
            if elem.tag == 'row':
                post_id = elem.get('PostId')
                related_post_id = elem.get('RelatedPostId')
                if post_id in relevant_post_ids or related_post_id in relevant_post_ids:
                    creation_date = elem.get('CreationDate')
                    if is_date_in_range(creation_date):
                        writer.write('  ' + ET.tostring(elem, encoding='unicode'))
                        count += 1
                elem.clear()
        
        write_xml_footer(writer, 'postlinks')

    print(f"PostLinks.xml processado. {count} links relevantes salvos em '{output_file}'.\n")

def filter_file_by_user_id(filename, relevant_user_ids):
    """
    Filtra Users.xml (sem filtro de data) e Badges.xml (com filtro de data).
    """
    print(f"Processando {filename}...")
    source_file = INPUT_DIR / filename
    output_file = OUTPUT_DIR / f'filtered_{filename}'
    root_tag = filename.lower().replace('.xml', '')
    
    count = 0
    is_badges_file = 'Badges' in filename
    id_attribute = 'UserId' if is_badges_file else 'Id'

    if not source_file.exists():
        print(f"Arquivo {source_file} não encontrado. Pulando.")
        return

    with open(output_file, 'w', encoding='utf-8') as writer:
        write_xml_header(writer, root_tag)
        
        context = ET.iterparse(source_file, events=('end',))
        for _, elem in context:
            if elem.tag == 'row':
                if elem.get(id_attribute) in relevant_user_ids:
                    # Aplica filtro de data apenas para o arquivo de Badges
                    if is_badges_file:
                        badge_date = elem.get('Date')
                        if is_date_in_range(badge_date):
                            writer.write('  ' + ET.tostring(elem, encoding='unicode'))
                            count += 1
                    else: # Para Users.xml, não há filtro de data
                        writer.write('  ' + ET.tostring(elem, encoding='unicode'))
                        count += 1
                elem.clear()
        
        write_xml_footer(writer, root_tag)

    print(f"{filename} processado. {count} linhas relevantes salvas em '{output_file}'.\n")

if __name__ == '__main__':
    create_output_dir()
    
    relevant_tags = filter_tags()
    relevant_post_ids, relevant_user_ids = filter_posts(relevant_tags)
    
    files_to_filter_by_post = ['Comments.xml', 'Votes.xml', 'PostHistory.xml']
    for filename in files_to_filter_by_post:
        found_users = filter_file_by_post_id(filename, relevant_post_ids)
        relevant_user_ids.update(found_users)
        
    filter_post_links(relevant_post_ids)
    
    create_post_tags_from_files()
    
    print(f"Total de {len(relevant_user_ids)} usuários únicos para filtrar.")
    filter_file_by_user_id('Users.xml', relevant_user_ids)
    filter_file_by_user_id('Badges.xml', relevant_user_ids)
    
    print("--- Processo de filtragem concluído! ---")
