-- Adiciona chaves estrangeiras e índices para otimizações

-- =============================================
-- Tabela: Posts
-- =============================================
BEGIN;
-- Relações:
-- ParentId se refere a outro Post (Pergunta -> Resposta)
ALTER TABLE posts ADD CONSTRAINT fk_posts_parent_id FOREIGN KEY (parentid) REFERENCES posts(id);
-- AcceptedAnswerId se refere a outro Post (Pergunta -> Resposta Aceita)
ALTER TABLE posts ADD CONSTRAINT fk_posts_accepted_answer_id FOREIGN KEY (acceptedanswerid) REFERENCES posts(id);
-- OwnerUserId se refere a um Usuário
ALTER TABLE posts ADD CONSTRAINT fk_posts_owner_user_id FOREIGN KEY (owneruserid) REFERENCES users(id);
-- LastEditorUserId se refere a um Usuário
ALTER TABLE posts ADD CONSTRAINT fk_posts_last_editor_user_id FOREIGN KEY (lasteditoruserid) REFERENCES users(id);

-- Índices para performance:
CREATE INDEX idx_posts_parent_id ON posts(parentid);
CREATE INDEX idx_posts_accepted_answer_id ON posts(acceptedanswerid);
CREATE INDEX idx_posts_owner_user_id ON posts(owneruserid);
CREATE INDEX idx_posts_last_editor_user_id ON posts(lasteditoruserid);
COMMIT;

-- =============================================
-- Tabela: Comments
-- =============================================
BEGIN;
-- Relações:
ALTER TABLE comments ADD CONSTRAINT fk_comments_post_id FOREIGN KEY (postid) REFERENCES posts(id);
ALTER TABLE comments ADD CONSTRAINT fk_comments_user_id FOREIGN KEY (userid) REFERENCES users(id);

-- Índices para performance:
CREATE INDEX idx_comments_post_id ON comments(postid);
CREATE INDEX idx_comments_user_id ON comments(userid);
COMMIT;

-- =============================================
-- Tabela: Votes
-- =============================================
BEGIN;
-- Relações:
ALTER TABLE votes ADD CONSTRAINT fk_votes_post_id FOREIGN KEY (postid) REFERENCES posts(id);
ALTER TABLE votes ADD CONSTRAINT fk_votes_user_id FOREIGN KEY (userid) REFERENCES users(id);

-- Índices para performance:
CREATE INDEX idx_votes_post_id ON votes(postid);
CREATE INDEX idx_votes_user_id ON votes(userid);
COMMIT;

-- =============================================
-- Tabela: Badges
-- =============================================
BEGIN;
-- Relações:
ALTER TABLE badges ADD CONSTRAINT fk_badges_user_id FOREIGN KEY (userid) REFERENCES users(id);

-- Índices para performance:
CREATE INDEX idx_badges_user_id ON badges(userid);
COMMIT;

-- =============================================
-- Tabela: PostHistory
-- =============================================
BEGIN;
-- Relações:
ALTER TABLE posthistory ADD CONSTRAINT fk_posthistory_post_id FOREIGN KEY (postid) REFERENCES posts(id);
ALTER TABLE posthistory ADD CONSTRAINT fk_posthistory_user_id FOREIGN KEY (userid) REFERENCES users(id);

-- Índices para performance:
CREATE INDEX idx_posthistory_post_id ON posthistory(postid);
CREATE INDEX idx_posthistory_user_id ON posthistory(userid);
COMMIT;

-- =============================================
-- Tabela: PostLinks
-- =============================================
BEGIN;
-- Relações:
ALTER TABLE postlinks ADD CONSTRAINT fk_postlinks_post_id FOREIGN KEY (postid) REFERENCES posts(id);
ALTER TABLE postlinks ADD CONSTRAINT fk_postlinks_related_post_id FOREIGN KEY (relatedpostid) REFERENCES posts(id);

-- Índices para performance:
CREATE INDEX idx_postlinks_post_id ON postlinks(postid);
CREATE INDEX idx_postlinks_related_post_id ON postlinks(relatedpostid);
COMMIT;

-- =============================================
-- Tabela: Tags
-- =============================================
BEGIN;
-- Relações:
ALTER TABLE tags ADD CONSTRAINT fk_tags_excerpt_post_id FOREIGN KEY (excerptpostid) REFERENCES posts(id);
ALTER TABLE tags ADD CONSTRAINT fk_tags_wiki_post_id FOREIGN KEY (wikipostid) REFERENCES posts(id);

-- Índices para performance:
CREATE INDEX idx_tags_excerpt_post_id ON tags(excerptpostid);
CREATE INDEX idx_tags_wiki_post_id ON tags(wikipostid);
COMMIT;