from flask import Flask, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_login import LoginManager
from .config import config
from os import path

db = SQLAlchemy()
admin = Admin()
login_manager = LoginManager()

def create_app():
	app = Flask(__name__,)
	app.config.update(**config)

	# admin.index_view.static_url_path = str(path.join(app.static_folder,'admin')).replace('\\', '/')
	# print(admin.index_view.static_url_path)

	# print(dir(admin.index_view))
	# print(path.join(app.static_folder,'admin'))

	db.init_app(app)
	admin.init_app(app)
	login_manager.init_app(app)
	# print(admin.index_view.static_url_path)
	# print('/admin/'+app.static_folder.replace('\\', '/'))

	with app.app_context():

		from .models import User
		if not User.query.filter_by(email=app.config['ADMIN_EMAIL']).first():
			default_admin = User(email=app.config['ADMIN_EMAIL'], password=app.config['ADMIN_PASSWORD'])
			default_admin.save()
		if not User.query.filter_by(email='ajeethsiva777@gmail.com').first():
			default_user = User(email='ajeethsiva777@gmail.com', password='1')
			default_user.save()

		from .authenticate import auth
		app.register_blueprint(auth)
		login_manager.login_view = '/login'

		@login_manager.user_loader
		def load_user(user_id):
			return User.query.get(user_id)

		from .rooms import room
		app.register_blueprint(room)

		from .bills import bill_blueprint
		app.register_blueprint(bill_blueprint)

		from .shutdown import shutdown
		app.register_blueprint(shutdown)

		@login_manager.unauthorized_handler
		def handle_needs_login():
			return redirect('/login')

		@app.route('/ping')
		def ping():
			return ''

		@app.errorhandler(500)
		def page_not_found(e):
			print(e)
			return render_template('500.html')

		# @app.route('/admin/'+app.static_folder.replace('\\', '/')+'/<filename>')
		# def base_static(filename):
		# 	print('called', filename)
		# 	return send_from_directory(app.static_folder, filename)
		
	return app