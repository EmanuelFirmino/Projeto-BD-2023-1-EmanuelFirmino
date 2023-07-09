#!/usr/bin/python3

from flask  import Flask, render_template, request, redirect
from flask  import url_for, flash, get_flashed_messages, session, abort
from functools import wraps
from mariaDB import *
from sys import argv

class UNBSystem:

	def __init__(self):

		self.app   = Flask(__name__,
						   template_folder ='../pages',
						   static_folder   ='../static'
						  )
		self.app.secret_key = 'batata'
		get_MariaDB_config(self.app)
		self.queryHandler = get_MariaDB_QueryHandler(self.app)
		self.routes() 

	def routes(self):

		def auth_required(auth):
			@wraps(auth)
			def decorator(*args, **kwargs):
				if 'user_auth' not in session:
					return redirect(url_for('index'))
				return auth(*args, **kwargs)
			return decorator

		@self.app.errorhandler(404)
		def not_found(err):
			return render_template('404.html', title='Avalia UnB - Página não encontrada!'), 404

		@self.app.route('/')
		def index():
			if 'user_auth' in session:
				return redirect(url_for('home'))
			return render_template('index.html', title='Avalia UnB')

		@self.app.route('/login', methods=['post'])
		def login():
			result = self.queryHandler.login(request.form)

			if result == 0xb851:
				flash('Ocorreu um erro. Tente novamente.')

			elif result:
				session['user_auth'] = result[0:3]
				return redirect(url_for('home'))

			else:
				flash('Usuário e/ou senha incorreto(s)!')
			
			return redirect(url_for('index'))

		@self.app.route('/logout')
		@auth_required
		def logout():
			session.pop('user_auth')	
			return redirect(url_for('index'))

		@self.app.route('/home')
		@auth_required
		def home():
			info = session['user_auth']
			return render_template('home.html', title='Avalia UnB - Home',
			name=info[0].split()[0], n_users=self.queryHandler.get_num_users(),
			profile=session['user_auth'][1], n_disc=self.queryHandler.get_num_disc(),
			n_prof=self.queryHandler.get_num_prof())

		@self.app.route('/perfil/<id>', methods=['get', 'post'])
		@auth_required
		def perfil(id):

			if request.method == 'POST':
				if 'image' in request.files and session['user_auth'][1] == id:
					img = request.files['image']
					self.queryHandler.insert_avatar(img.read(), session['user_auth'][1])

			info = self.queryHandler.get_info(id)
			if info:
				if info["avatar"]:
					img  = f'data:image/jpeg;base64,{info["avatar"]}'
				else:
					img  = None
				return render_template('perfil.html', title='Avalia UnB - Perfil', profile_pic=img,
				name=info["nome"], matr=info["matricula"], course=info["curso"], isAdmin=info["isAdmin"])
			abort(404)

		@self.app.route('/courses', methods=['get'])
		@auth_required
		def courses():
			page = request.args.get('page')

			if page and page.isdigit():
				page = int(page) - 1
				courses = self.queryHandler.get_courses(page)
				if not page+1 or not courses:
					abort(404)
				return render_template('courses.html', profile=session['user_auth'][1],
				page=page+1, courses=courses, title='Avalia UnB - Cursos')
			abort(404)

		@self.app.route('/template/<course>', methods=['get', 'post'])
		@auth_required
		def template(course):

			info = self.queryHandler.get_course_info(course)

			if request.method == 'POST':

				if 'id_prof' in request.form:
					eval = [request.form['comment'], session['user_auth'][1], request.form['id_prof']]
					print(eval)
					self.queryHandler.insert_eval_prof(eval)

			
				elif 'comment' in request.form:								
					eval = [request.form['comment'], session['user_auth'][1], self.queryHandler.get_id_class(info[0])[0]]
					self.queryHandler.insert_eval(eval)

				
				elif 'denuncia' in request.form:
					self.queryHandler.insert_den(request.form)

				

			evals = self.queryHandler.get_eval(course)
			evals = list(evals)
			teachers = self.queryHandler.get_teachers(info[0])
			evals_teachers = {}

			for teacher in teachers:
				print(teacher[0])
				evals_teachers[teacher[0]] = self.queryHandler.get_eval_prof(teacher[0])

			for i in range(len(evals)):
				evals[i] = list(evals[i])
				evals[i][2] = self.queryHandler.get_name(evals[i][2])[0]

			return render_template('template.html', course=course, title=f'Avalia UnB - {course}', info=info,
			profile=session['user_auth'][1], evals=evals, teachers=teachers, evals_teachers=evals_teachers)


	def start(self):
		self.app.run(debug=True)

	def feed_db(self):
		self.queryHandler.seed()

if __name__ == '__main__':

	aplication = UNBSystem()
	help = '''

 Ajuda
 
 --run:  Inicia a aplicação.
 --feed: Cria as tabelas (se não existirem) e alimenta o banco de dados.

		   '''	
	if len(argv) == 2:
		if argv[1]   == '--feed':
			aplication.feed_db()
		elif argv[1] == '--run':
			aplication.start()
		elif argv[1] == '--insert-user':
			aplication.queryHandler.control.create_user()
		else:
			print('\n Comando inválido!')
			print(help)
	else:
		print(help)