from flask import Blueprint, render_template, redirect, request, flash, current_app as app
from flask_login import login_user, logout_user, login_manager
from .models import User

auth = Blueprint('auth', __name__)

@auth.route('/login')
def get_login():
	return render_template('login.html')

@auth.route('/login', methods=['POST'])
def post_login():
	logout_user()
	_next = request.args.get('next', '/')

	if 'email' not in request.form or 'password' not in request.form:
		flash('Please fill all the fields.','login-error')
		return render_template('login.html')
	user = User.query.filter_by(email=request.form['email']).first()

	if not user or user.password != request.form['password']:
		flash('Invalid credentials.','login-error')
		return render_template('login.html')
	login_user(user)
	return redirect(_next)

@auth.route('/logout')
def logout():
	logout_user()
	return redirect('/login')

# @app.before_request
# def logout_without_refere():
# 	# if request.path == '/admin/' or request.path == '/admin' or 'Referer' not in request.headers:
# 	if request.path == '/admin/' or request.path == '/admin':
# 		logout()