# 1. Tabelas sem dependências
psql -h localhost -U postgres -d stackoverflow_db -f users_inserts.sql > log_importacao.txt 2>&1
psql -h localhost -U postgres -d stackoverflow_db -f tags_inserts.sql > log_importacao.txt 2>&1

# 2. Tabelas que dependem das anteriores (ex: Posts dependem de Users)
psql -h localhost -U postgres -d stackoverflow_db -f posts_inserts.sql > log_importacao.txt 2>&1
psql -h localhost -U postgres -d stackoverflow_db -f posttags_inserts.sql > log_importacao.txt 2>&1

# 3. Tabelas que dependem de Posts
psql -h localhost -U postgres -d stackoverflow_db -f comments_inserts.sql > log_importacao.txt 2>&1
psql -h localhost -U postgres -d stackoverflow_db -f votes_inserts.sql > log_importacao.txt 2>&1
psql -h localhost -U postgres -d stackoverflow_db -f posthistory_inserts.sql > log_importacao.txt 2>&1
psql -h localhost -U postgres -d stackoverflow_db -f postlinks_inserts.sql > log_importacao.txt 2>&1

# 4. Tabela que depende de Users
psql -h localhost -U postgres -d stackoverflow_db -f badges_inserts.sql > log_importacao.txt 2>&1

# Atualiza constraints depois de adicionar todos os dados
# psql -h localhost -U postgres -d stackoverflow_db -f alter-table-schemas.sql
