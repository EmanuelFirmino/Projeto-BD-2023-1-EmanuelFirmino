CREATE TABLE IF NOT EXISTS Usuarios (
  matricula VARCHAR(20) PRIMARY KEY,
  nome VARCHAR(30) NOT NULL,
  avatar BLOB,
  senha VARCHAR(100) NOT NULL,
  curso VARCHAR(30) NOT NULL,
  isAdmin TINYINT(1) NOT NULL
);

CREATE TABLE IF NOT EXISTS Departamentos (
  codigo INTEGER PRIMARY KEY,
  nome VARCHAR(500) NOT NULL
);

CREATE TABLE IF NOT EXISTS Professores (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  nome VARCHAR(30) NOT NULL,
  codigo_departamento INTEGER,
  FOREIGN KEY (codigo_departamento) REFERENCES Departamentos(codigo)
);

CREATE TABLE IF NOT EXISTS Disciplinas (
  codigo VARCHAR(20) PRIMARY KEY,
  nome VARCHAR(30) NOT NULL,
  codigo_departamento INTEGER,
  FOREIGN KEY (codigo_departamento) REFERENCES Departamentos(codigo)
);

CREATE TABLE IF NOT EXISTS Turmas (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  turma VARCHAR(20),
  horario VARCHAR(150),
  id_professor INTEGER,
  codigo_disciplina VARCHAR(20),
  FOREIGN KEY (id_professor) REFERENCES Professores(id),
  FOREIGN KEY (codigo_disciplina) REFERENCES Disciplinas(codigo)
);

CREATE TABLE IF NOT EXISTS Avaliacoes (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  comentario TEXT,
  matricula_autor VARCHAR(20),
  id_professor INTEGER,
  id_turma INTEGER,
  FOREIGN KEY (matricula_autor) REFERENCES Usuarios(matricula) ON DELETE CASCADE,
  FOREIGN KEY (id_professor) REFERENCES Professores(id),
  FOREIGN KEY (id_turma) REFERENCES Turmas(id)
);

CREATE TABLE IF NOT EXISTS Denuncias (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  comentario TEXT,
  id_avaliacao INTEGER,
  FOREIGN KEY (id_avaliacao) REFERENCES Avaliacoes(id) ON DELETE CASCADE
);
