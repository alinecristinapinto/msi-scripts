-- Para acelerar a busca de respostas para uma pergunta (JOIN em si mesmo)
CREATE INDEX idx_posts_parentid ON Posts (ParentId);

-- Para acelerar buscas por tipo de post (ex: WHERE PostTypeId = 1 para perguntas)
CREATE INDEX idx_posts_posttypeid ON Posts (PostTypeId);

-- Para acelerar JOINs com a tabela Users
CREATE INDEX idx_posts_owneruserid ON Posts (OwnerUserId);

-- Para buscas e ordenação por data
CREATE INDEX idx_posts_creationdate ON Posts (CreationDate);
CREATE INDEX idx_posts_lastactivitydate ON Posts (LastActivityDate);

-- Essencial para buscar comentários de um post específico
CREATE INDEX idx_comments_postid ON Comments (PostId);

-- Para buscar todos os comentários de um usuário
CREATE INDEX idx_comments_userid ON Comments (UserId);

-- Essencial para buscar as medalhas de um usuário
CREATE INDEX idx_badges_userid ON Badges (UserId);

-- Para buscar todo o histórico de um post
CREATE INDEX idx_posthistory_postid ON PostHistory (PostId);

-- Para buscar todas as edições feitas por um usuário
CREATE INDEX idx_posthistory_userid ON PostHistory (UserId);

-- Para encontrar posts relacionados a partir de um PostId
CREATE INDEX idx_postlinks_postid ON PostLinks (PostId);

-- Para encontrar posts que se relacionam com um RelatedPostId
CREATE INDEX idx_postlinks_relatedpostid ON PostLinks (RelatedPostId);

-- Essencial para a consulta "quais posts têm a tag X?"
CREATE INDEX idx_posttags_tagid_postid ON PostTags (TagId, PostId);

-- Para acelerar a busca de uma tag pelo nome (ex: WHERE TagName = 'python')
CREATE INDEX idx_tags_tagname ON Tags (TagName);

-- Essencial para contar os votos de um post
CREATE INDEX idx_votes_postid ON Votes (PostId);

-- Para encontrar os votos de um usuário específico
CREATE INDEX idx_votes_userid ON Votes (UserId);

-- Para encontrar edições sugeridas para um post
CREATE INDEX idx_suggestededits_postid ON SuggestedEdits (PostId);

-- Para encontrar edições sugeridas por um usuário
CREATE INDEX idx_suggestededits_owneruserid ON SuggestedEdits (OwnerUserId);