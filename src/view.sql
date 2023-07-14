CREATE VIEW IF NOT EXISTS MostEvaluatedTeacher AS
SELECT prof.id AS id_professor, prof.nome AS nome_professor, COUNT(eval.id) AS total_avaliacoes
FROM Professores prof
JOIN Turmas t ON prof.id = t.id_professor
JOIN Avaliacoes eval ON t.id = eval.id_turma
GROUP BY prof.id
HAVING COUNT(eval.id) = (
    SELECT COUNT(id)
    FROM Avaliacoes
    GROUP BY id_turma
    ORDER BY COUNT(id) DESC
    LIMIT 1
);

CREATE VIEW IF NOT EXISTS GetNameUser AS
SELECT matricula, nome
FROM Usuarios;