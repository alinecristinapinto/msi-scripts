WITH tags_of_interest AS (
  -- id, tagname, group_name
  VALUES
    (16,   'python',     'alto_recurso'),
    (3,    'javascript', 'alto_recurso'),
    (17,   'java',       'alto_recurso'),
    (9,    'c#',         'alto_recurso'),
    (4452, 'r',          'baixo_moderado'),
    (77929,'julia',      'baixo_moderado'),
    (387,  'bash',       'baixo_moderado'),
    (73780,'dart',       'baixo_moderado')
), months AS (
  SELECT generate_series(
           DATE '2018-01-01',
           DATE '2025-12-01',
           INTERVAL '1 month'
         )::date AS month_start
),
-- Perguntas por tag (a própria pergunta carrega a tag)
q AS (
  SELECT
    DATE_TRUNC('month', p.creationdate)::date AS month_start,
    t.tagname,
    t.group_name,
    COUNT(*) AS questions
  FROM posts p
  JOIN posttags pt ON pt.postid  = p.id
  JOIN (
    SELECT column1 AS id, column2 AS tagname, column3 AS group_name FROM tags_of_interest
  ) t ON t.id = pt.tagid 
  WHERE p.posttypeid  = 1
    AND p.creationdate >= DATE '2018-01-01'
    AND p."creationdate" <  DATE '2026-01-01'
  GROUP BY 1,2,3
),
-- Respostas por tag (a resposta herda a tag da PERGUNTA-PAI)
a AS (
  SELECT
    DATE_TRUNC('month', a.creationdate)::date AS month_start,
    t.tagname,
    t.group_name,
    COUNT(*) AS answers
  FROM posts a
  JOIN posts q ON q.id = a.parentid              -- liga resposta -> pergunta
  JOIN posttags pt ON pt.postid  = q.id         -- pega as tags da pergunta
  JOIN (
    SELECT column1 AS id, column2 AS tagname, column3 AS group_name FROM tags_of_interest
  ) t ON t.id = pt.tagid
  WHERE a.posttypeid = 2
    AND a.creationdate >= DATE '2018-01-01'
    AND a.creationdate <  DATE '2026-01-01'
  GROUP BY 1,2,3
),
-- junta perguntas e respostas
merged AS (
  SELECT m.month_start, t.tagname, t.group_name,
         COALESCE(q.questions, 0) AS questions,
         COALESCE(a.answers,   0) AS answers,
         COALESCE(q.questions, 0) + COALESCE(a.answers, 0) AS total_q_a
  FROM months m
  CROSS JOIN (
    SELECT column2 AS tagname, column3 AS group_name FROM tags_of_interest
  ) t
  LEFT JOIN q ON q.month_start = m.month_start AND q.tagname = t.tagname
  LEFT JOIN a ON a.month_start = m.month_start AND a.tagname = t.tagname
)
SELECT *
FROM merged
ORDER BY month_start, group_name, tagname;

