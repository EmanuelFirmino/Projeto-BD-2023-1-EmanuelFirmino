DELIMITER //

CREATE PROCEDURE getuser (OUT adm INT)
	BEGIN
		SELECT matricula FROM Usuarios WHERE Usuarios.isAdmin = adm;
	END;
//

DELIMITER;
