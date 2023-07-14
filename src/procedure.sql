CREATE PROCEDURE IF NOT EXISTS get_adm()
BEGIN
    SELECT 1
    FROM Usuarios
    WHERE isAdmin = 1;
END;

CREATE PROCEDURE IF NOT EXISTS get_reports()
BEGIN
    SELECT *
    FROM Denuncias;
END;
