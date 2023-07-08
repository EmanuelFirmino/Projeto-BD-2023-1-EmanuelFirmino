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

	def get_eval(self, course):
		pass

	def seed(self):

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

		print('\n * Banco de dados alimentado com sucesso! *\n')

class Usuarios:

	def __init__(self, matricula, nome, avatar, senha, curso, isAdmin):
		self.nome 	   = nome
		self.matricula = matricula
		self.avatar	   = avatar
		self.senha	   = senha
		self.curso     = curso
		self.isAdmin   = isAdmin

	def create(self):
		pass
		

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