import MySQLdb
from config import *
from hashlib import sha256
from base64 import b64encode
import csv

class queryHandler:

	def __init__(self, handler):
		self.handler = handler
		self.control = Controllers(handler)

	def login(self, credentials):

		try:
			with self.handler.cursor() as cursor:
				usr 	= cursor.connection.escape_string(credentials['user']).decode('utf-8')
				passwd 	= self.get_hash(cursor.connection.escape_string(credentials['passwd']))
				cursor.execute('SELECT nome, matricula, curso, isAdmin FROM Usuarios WHERE matricula = %s AND senha = %s',
								(usr, passwd))
				result = cursor.fetchone()

		except MySQLdb.ProgrammingError:
			print(' **&& erro aqui')
			return 0xb851

		return result

	def insert_avatar(self, avatar, matricula):
		with self.handler.cursor() as cursor:
			cursor.execute('UPDATE Usuarios SET avatar = %s WHERE matricula = %s', (avatar, matricula))
		self.handler.commit()

	def insert_eval(self, values):
		with self.handler.cursor() as cursor:
			cursor.execute('INSERT INTO Avaliacoes (comentario, matricula_autor, id_turma) VALUES (%s, %s, %s)', (values[0], values[1], values[2]))
		self.handler.commit()

	def get_name(self, matr):
		with self.handler.cursor() as cursor:
			cursor.execute('SELECT nome From Usuarios WHERE matricula = %s', (matr,))
			result = cursor.fetchone()
		return result

	def get_num_users(self)	:

		with self.handler.cursor() as cursor:
			cursor.execute('SELECT COUNT(*) FROM Usuarios')
			result = cursor.fetchone()[0]
		return result

	def get_num_disc(self):

		with self.handler.cursor() as cursor:
			cursor.execute('SELECT COUNT(*) FROM Disciplinas')
			result = cursor.fetchone()[0]
		return result

	def get_num_prof(self):

		with self.handler.cursor() as cursor:
			cursor.execute('SELECT COUNT(*) FROM Professores')
			result = cursor.fetchone()[0]
		return result
		
	def get_hash(self, hash_it):
		hashid	= sha256()
		hashid.update(hash_it)
		return hashid.hexdigest()

	def get_info(self, id):
		info = dict()
		attributes = ['nome', 'matricula', 'avatar', 'curso', 'isAdmin']

		with self.handler.cursor() as cursor:
			cursor.execute('SELECT nome, matricula, avatar, curso, isAdmin FROM Usuarios WHERE matricula = %s', (id,))
			result = cursor.fetchone()

		if result:

			for attr in range(len(attributes)):
				if attributes[attr] == 'avatar':
					avatar_bytes = result[attr]
					if avatar_bytes:
						info[attributes[attr]] = b64encode(avatar_bytes).decode('utf-8')
					else:
						info[attributes[attr]] = None
				else:
					info[attributes[attr]] = result[attr]

			return info
		return None

	def get_courses(self, page):

		with self.handler.cursor() as cursor:
			cursor.execute(f'SELECT * FROM Disciplinas LIMIT 30 OFFSET {30*page}')
			result = cursor.fetchall()
		return result

	def get_course_info(self, course):

		with self.handler.cursor() as cursor:
			cursor.execute('SELECT * FROM Disciplinas WHERE codigo = %s', (course,))
			result = cursor.fetchone()
		return result

	def get_id_class(self, cod_dis):
		with self.handler.cursor() as cursor:
			cursor.execute('SELECT id FROM Turmas WHERE codigo_disciplina = %s', (cod_dis,))
			result = cursor.fetchone()
		return result

	def get_dec_eval(self, id):
		with self.handler.cursor() as cursor:
			cursor.execute('SELECT * FROM Avaliacoes WHERE id = %s', (id,))
			result = cursor.fetchone()
		return result

	def get_eval(self, course):
		with self.handler.cursor() as cursor:
			cursor.execute('SELECT * from Avaliacoes WHERE id_turma = (SELECT id FROM Turmas WHERE codigo_disciplina = %s LIMIT 1)', (course,))
			result = cursor.fetchall()
		return result

	def del_eval(self, id):
		with self.handler.cursor() as cursor:
			cursor.execute('DELETE FROM Avaliacoes WHERE id = %s', (id,))
		self.handler.commit()

	def del_user(self, matr):
		with self.handler.cursor() as cursor:
			cursor.execute('DELETE FROM Usuarios WHERE matricula = %s', (matr,))
		self.handler.commit()

	def del_dec(self, id):
		with self.handler.cursor() as cursor:
			cursor.execute('DELETE FROM Denuncias WHERE id = %s', (id,))
		self.handler.commit()

	def get_teachers(self, cod):
		with self.handler.cursor() as cursor:
			cursor.execute('SELECT DISTINCT Professores.id, Professores.nome from Professores, Turmas WHERE Turmas.id_professor = Professores.id AND Turmas.codigo_disciplina = %s', (cod,))
			result = cursor.fetchall()
		return result

	def insert_den(self, values):
		with self.handler.cursor() as cursor:
			cursor.execute('INSERT INTO Denuncias (comentario, id_avaliacao) VALUES (%s, %s)', (values['denuncia'], values['id']))
		self.handler.commit()

	def get_decs(self):
		with self.handler.cursor() as cursor:
			cursor.execute('SELECT * FROM Denuncias;')
			result = cursor.fetchall()
		return result

	def insert_eval_prof(self, values):
		with self.handler.cursor() as cursor:
			cursor.execute('INSERT INTO Avaliacoes (comentario, matricula_autor, id_professor) VALUES (%s, %s, %s)', (values[0], values[1], values[2]))
		self.handler.commit()

	def get_eval_prof(self, id):
		with self.handler.cursor() as cursor:
			cursor.execute('SELECT * FROM Avaliacoes WHERE id_professor = %s', (id,))
			result = cursor.fetchall()
		return result

	def is_Admin(self, matr):
		with self.handler.cursor() as cursor:
			cursor.execute('SELECT isAdmin FROM Usuarios WHERE matricula = %s', (matr,))
			result = cursor.fetchone()[0]
		return result

	def seed(self):

		with self.handler.cursor() as cursor:
			cursor.execute('DELETE FROM Avaliacoes')
			cursor.execute('DELETE FROM Turmas')
		self.handler.commit()


		# Cria as tabelas, se não existirem

		try:
			with open('seed_tables.sql') as fp:
				commands = fp.read()

			with self.handler.cursor() as cursor:
				cursor.execute(commands)

			self.handler.commit()

		except:
			print('Erro ao alimentar o banco de dados!')

		# Alimenta a tabela Departamentos com o arquivo csv

		with open('departamentos_2023-1.csv') as file:
			csvr = csv.reader(file)

			for line in csvr:
				if line[0] == 'cod':
					continue
				with self.handler.cursor() as cursor: 
					cursor.execute('''IF NOT EXISTS (SELECT 1 FROM Departamentos WHERE codigo = %s)
					THEN INSERT INTO Disciplinas (codigo, nome) VALUES (%s, %s); END IF;''', (line[0], line[0], line[1]))
			self.handler.commit()

		# Alimenta a tabela Disciplinas com o arquivo csv
	
		with open('disciplinas_2023-1.csv') as file:
			csvr = csv.reader(file)

			for line in csvr:
				if line[0] == 'cod':
					continue
				with self.handler.cursor() as cursor:
					cursor.execute('''IF NOT EXISTS (SELECT 1 FROM Disciplinas WHERE codigo = %s)
					THEN INSERT INTO Disciplinas (codigo, nome, codigo_departamento) VALUES (%s, %s, %s); END IF;''', (line[0], line[0], line[1], line[2]))
			self.handler.commit()

		# Alimenta as tabelas Professores e Turmas com o arquivo csv
		
		with open('turmas_2023-1.csv') as file:
			csvr = csv.reader(file)

			for line in csvr:

				if line[0] == 'turma':
					continue

				with self.handler.cursor() as cursor:
					cursor.execute('''IF NOT EXISTS (SELECT 1 FROM Professores WHERE nome = %s)
					THEN INSERT INTO Professores (nome, codigo_departamento) VALUES (%s, %s); END IF;''', (line[2], line[2], line[8]))

					cursor.execute('''INSERT INTO Turmas (turma, horario, id_professor, codigo_disciplina) VALUES (%s, %s, (SELECT id FROM Professores WHERE nome = %s), %s)''', (line[0], line[3], line[2], line[7]))
					
			self.handler.commit()

		users = [['19192020',
		 		 'Admin Example',
				 'batata',
				 'Engenharia de Computação',
				 1
				 ],

				 ['282828281',
				  'Maligen Bridges',
				  'mama123',
				  'Filosofia',
				  0
				 ],

			     ['280642129',
				  'Frank',
				  'cafebabe',
				  'Física',
				  0
				 ]
				]
		 
		for user in users:

			with self.handler.cursor() as cursor:
				hash_id = sha256()
				hash_id.update(user[2].encode('utf-8'))
				passwd = hash_id.hexdigest()
				cursor.execute('INSERT IGNORE INTO Usuarios (matricula, nome, senha, curso, isAdmin) VALUES (%s, %s, %s, %s, %s)', (user[0], user[1], passwd, user[3], user[4]))
			self.handler.commit()

		print('\n * Banco de dados alimentado com sucesso! *\n')

class Usuarios:

	def __init__(self, matricula, nome, avatar, senha, curso, isAdmin):

		self.nome 	   = nome
		self.matricula = matricula
		self.avatar	   = avatar
		self.senha	   = senha
		self.curso     = curso
		self.isAdmin   = isAdmin
	
class Controllers:

	def __init__(self, handler):
		self.handler = handler
	
	def create_user(self):
		nome 		= input('Insira o nome: ')
		matricula 	= input('Insira a matricula: ')
		avatar      = input('Insira o caminho para a imagem: ')
		try:
			with open(avatar, 'rb') as img:
				avatar = img.read()
		except:
			print('Ocorreu um erro ao abrir o arquivo.')
			avatar = None
		curso 		= input('Insira o curso: ')
		senha		= input('Insira a senha: ')
		hashid		= sha256()
		hashid.update(senha.encode('utf-8'))
		senha 		= hashid.hexdigest()
		isAdmin 	= int(input('O usuário é Admin? [0, 1]: '))

		try:
			with self.handler.cursor() as cursor:
				sql = '''INSERT INTO Usuarios (matricula, nome, avatar, senha, curso, isAdmin)
						VALUES (%s, %s, %s, %s, %s, %s)'''
				cursor.execute(sql, (matricula, nome, avatar, senha, curso, isAdmin))
				self.handler.commit()

		except MySQLdb.OperationalError:
			print('Erro ao inserir no banco de dados!')


def get_MariaDB_config(app):

	app.config['MYSQL_HOST'] 		= HOST
	app.config['MYSQL_USER'] 		= USER
	app.config['MYSQL_PASSWORD']	= PASSWORD
	app.config['MYSQL_DB']			= DATABASE

def get_MariaDB_QueryHandler(app):

	try:

		conn = MySQLdb.connect	(
			host 		= app.config['MYSQL_HOST'],
			user 		= app.config['MYSQL_USER'],
			password 	= app.config['MYSQL_PASSWORD'],
			database    = app.config['MYSQL_DB']
		)

		return queryHandler(conn)

	except MySQLdb.OperationalError:

		print("\n***Não foi possível conectar ao banco de dados!***\n")
		return None