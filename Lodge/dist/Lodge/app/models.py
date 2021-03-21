from flask import current_app as app, flash, render_template, redirect
from . import db, admin, login_manager
from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import MenuLink
from flask_login import UserMixin, current_user

class CustomDBModel(db.Model):
	__abstract__ = True

	def commit(self):
		db.session.commit()

	def save(self):
		db.session.add(self)
		self.commit()

	def delete(self):
		db.session.delete(self)
		self.commit()

class User(UserMixin, CustomDBModel):
	id       = db.Column(db.Integer , primary_key=True , autoincrement=True)
	email    = db.Column(db.VARCHAR(30), unique=True, nullable=False)
	password = db.Column(db.String(60), nullable=False)

	def is_admin(self):
		return current_user.email in app.config['ADMIN_USERS']

class Room(CustomDBModel):
	id         = db.Column(db.Integer , primary_key=True , autoincrement=True)
	room_no    = db.Column(db.Integer , unique=True)
	booked     = db.Column(db.Boolean, default=False)
	restroom   = db.Column(db.VARCHAR(30), nullable=False)
	rent       = db.Column(db.Integer , nullable=False)
	room_type  = db.Column(db.VARCHAR(30), nullable=False)
	created_by = db.Column(db.Integer, nullable=True)

class Customer(CustomDBModel):
	id = db.Column(db.Integer , primary_key=True , autoincrement=True)
	name = db.Column(db.Integer, nullable=False)
	count = db.Column(db.Integer, nullable=False, default = 1)
	address1 = db.Column(db.String(200), nullable=True)
	address2 = db.Column(db.String(200), nullable=True)
	city = db.Column(db.String(100), nullable=True)
	country = db.Column(db.String(60), nullable=True)
	state = db.Column(db.String(60), nullable=True)
	zip_code = db.Column(db.String(30), nullable=True)
	contact_no = db.Column(db.String(20), nullable=True)
	created_by = db.Column(db.Integer, nullable=True)

class Bill(CustomDBModel):
	id = db.Column(db.Integer , primary_key=True , autoincrement=True)
	room_id = db.Column(db.Integer, nullable=False)
	customer_id = db.Column(db.Integer, nullable=False)
	in_time = db.Column(db.DateTime, nullable=False)
	out_time =  db.Column(db.DateTime, nullable=True)
	advance = db.Column(db.Integer, nullable=True)
	miscellaneous = db.Column(db.Integer, nullable=True)
	luxary = db.Column(db.Integer, nullable=True)
	charge = db.Column(db.Integer, nullable=True)
	extra_charge = db.Column(db.Integer, nullable=True)
	gst = db.Column(db.Integer, nullable=True)
	total = db.Column(db.Integer, nullable=True)
	closed = db.Column(db.Boolean, default=False)
	created_by = db.Column(db.Integer, nullable=True)


class AdminView(ModelView):
	def is_accessible(self):
		if current_user.is_anonymous or not current_user.is_admin():
			flash('Login with admin account','login-error')
			return False
		return True

admin.add_link(MenuLink(name='Lodge', category='', url='/'))

admin.add_views(
	AdminView(User, db.session),
	AdminView(Room, db.session),
	AdminView(Customer, db.session),
	AdminView(Bill, db.session),
	)
db.create_all()