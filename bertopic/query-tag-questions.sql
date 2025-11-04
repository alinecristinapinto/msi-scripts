SELECT 
    p.id,
    p.posttypeid,
    p.body,
    p.lastactivitydate,
    EXTRACT(YEAR FROM p.lastactivitydate) AS Ano 
FROM posts p
JOIN posttags pt ON p.id = pt.postid
JOIN tags t ON pt.tagid = t.id
WHERE 
    p.posttypeid = 1
    AND t.tagname = 'python'
    AND p.lastactivitydate BETWEEN '2018-01-01' AND '2025-12-31'
ORDER BY p.lastactivitydate ASC;

-- SELECT 
--     COUNT(p.id)
-- FROM posts p
-- JOIN posttags pt ON p.id = pt.postid
-- JOIN tags t ON pt.tagid = t.id
-- WHERE 
--     p.posttypeid = 1
--     AND t.tagname = 'python'
--     AND p.lastactivitydate BETWEEN '2018-01-01' AND '2025-12-31';

-- SELECT 
--     EXTRACT(YEAR FROM p.lastactivitydate) AS Ano,
--     COUNT(p.id) AS TotalPosts
-- FROM posts p
-- JOIN posttags pt ON p.id = pt.postid
-- JOIN tags t ON pt.tagid = t.id
-- WHERE 
--     p.posttypeid = 1
--     AND t.tagname = 'python'
--     AND p.lastactivitydate BETWEEN '2018-01-01' AND '2025-12-31'
-- GROUP BY 
--     Ano 
-- ORDER BY 
--     Ano ASC;