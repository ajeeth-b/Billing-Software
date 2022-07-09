from flask import Blueprint, render_template, request, redirect, flash, current_app as app, send_file, send_from_directory
from .models import Bill, Room, Customer
from datetime import datetime
from math import ceil
from flask_login import login_required, current_user
import csv
import json

bill_blueprint = Blueprint('bills', __name__)

class DictToObject:
	def __init__(self, **dicts):
		self.__dict__.update(dicts)


def all_bill_data(bill):
	customer = Customer.query.filter_by(id=bill.customer_id).first()
	room = Room.query.filter_by(id=bill.room_id).first()
	data = {
		'id':bill.id,
		'room_id':room.id,
		'room_no':room.room_no,
		'customer_id':customer.id,
		'name':customer.name,
		'no_of_person':customer.count,
		'address1':customer.address1 or '',
		'address2':customer.address2 or '',
		'city':customer.city or '',
		'state':customer.state or '',
		'country':customer.country or '',
		'zip':customer.zip_code or '',
		'contact_number':customer.contact_no,
		'in_time':bill.in_time.strftime('%Y/%m/%d %I:%M %p') if bill.in_time else None,
		'out_time':bill.out_time.strftime('%Y/%m/%d %I:%M %p') if bill.out_time else None,
		'advance':bill.advance,
		'cost':bill.charge,
		'miscellaneous':bill.miscellaneous,
		'luxary':bill.luxary,
		'extra_cost':bill.extra_charge,
		'gst':bill.gst,
		'total':bill.total
	}

	return data

# def bill_table(bills):
# 	data = []
# 	for bill in bills:
# 		room = Room.query.filter_by(id=bill.room_id).first()
# 		customer = Customer.query.filter_by(id=bill.customer_id).first()
# 		if not room or not customer:
# 			continue
# 		row_data = {
# 			'id':bill.id,
# 			'name':customer.name,
# 			'room_no':room.room_no,
# 			'in_time':bill.in_time.strftime('%Y/%m/%d %I:%M %p'),
# 		}
# 		data += [row_data]
# 	return data

# def bill_table_data(page_no=1, page_per=10, closed=True):
# 	bills = Bill.query.filter_by(closed=closed).paginate(page_no, per_page=page_per, error_out=False).items
# 	data = [DictToObject(**i) for i in bill_table(bills)]
# 	return data, ceil(Bill.query.filter_by(closed=False).count()/page_per)

@bill_blueprint.route('/bill')
@login_required
def get_bills():
	bills = Bill.query.filter_by(closed=False)
	data = [DictToObject(**all_bill_data(bill)) for bill in bills]
	return render_template('bills.html', bills=data)

@bill_blueprint.route('/bill/old')
@login_required
def get_old_bills():
	bills = Bill.query.filter_by(closed=True)
	data = [DictToObject(**all_bill_data(bill)) for bill in bills]
	return render_template('old_bills.html', bills=data)


@bill_blueprint.route('/bill/get/<id>')
@login_required
def show_bill(id):
	bill = Bill.query.filter_by(id=id).first()
	return render_template('bill_detail.html')

@bill_blueprint.route('/book/room/<room_no>', methods=['GET'])
@login_required
def get_book_room(room_no):
	room = Room.query.filter_by(room_no=room_no).first()
	if not room:
		return render_template('error.html', message='No such room') 
	return render_template('book_room.html', room_id=room.id, room_no=room_no, datetime=datetime.now().strftime('%Y-%m-%dT%H:%M'))

@bill_blueprint.route('/book/room/<id>', methods=['POST'])
@login_required
def post_book_room(id):
	room = Room.query.filter_by(id=id).first()
	if not room or room.booked == True:
		return render_template('error.html', message='Room already taken')
	form = DictToObject(**request.form)

	customer = Customer(name=form.name, count=form.no_of_person, 
		address1=form.address1, address2=form.address2, state=form.state,city=form.city,
		country=form.country, zip_code=form.zip, contact_no=form.contact_number, 
		created_by=current_user.id)
	customer.save()

	in_time = datetime.strptime(form.in_time, '%Y-%m-%dT%H:%M')

	bill = Bill(room_id=room.id, customer_id=customer.id, in_time=in_time, 
		advance=form.advance, created_by=current_user.id)
	bill.save()
	room.booked = True
	room.save()
	return redirect('/bill')

@bill_blueprint.route('/room/close/<room_no>')
@login_required
def bill_the_room(room_no):
	room = Room.query.filter_by(room_no = room_no).first()
	if not room:
		return render_template('error.html', message='No such room, Create one')
	bill = Bill.query.filter_by(room_id=room.id, closed=False).first()
	if not bill:
		return render_template('error.html', message='Bill not found')
	return redirect('/bill/close/'+str(bill.id))

@bill_blueprint.route('/bill/close/<int:id>', methods=['GET'])
@login_required
def close_bill_form(id):
	bill = Bill.query.filter_by(id=id).first()
	if not bill:
		return render_template('error.html', message='no such bill')
	if bill.closed:
		flash('Bill already closed')
		return redirect('/bill/print/'+str(bill.id))
	room = Room.query.filter_by(id=bill.room_id).first()
	customer = Customer.query.filter_by(id=bill.customer_id).first()

	form_data = {
		'id':bill.id,
		'room_id':room.id,
		'room_no':room.room_no,
		'customer_id':customer.id,
		'name':customer.name,
		'no_of_person':customer.count,
		'address1':customer.address1,
		'address2':customer.address2,
		'city':customer.city,
		'state':customer.state,
		'country':customer.country,
		'zip':customer.zip_code,
		'contact_number':customer.contact_no,
		'in_time':bill.in_time.strftime('%Y-%m-%dT%H:%M'),
		'out_time':datetime.now().strftime('%Y-%m-%dT%H:%M'),
		'advance':bill.advance,
		'rent':room.rent,
	}
	return render_template('close_bill.html', **form_data)

@bill_blueprint.route('/bill/close', methods=['POST'])
@login_required
def close_bill():
	if 'gst' not in request.form:
		request.form = request.form.to_dict()
		request.form.update({'gst':0})
	form = DictToObject(**request.form)

	bill = Bill.query.filter_by(id=form.id).first()
	if bill.closed:
		flash('Bill already closed')
		return redirect('/bill/print/'+str(bill.id))
	room = Room.query.filter_by(id=form.room_id).first()
	customer = Customer.query.filter_by(id=form.customer_id).first()

	bill.out_time = datetime.strptime(form.out_time, '%Y-%m-%dT%H:%M')
	bill.miscellaneous = form.miscellaneous
	bill.luxary = form.luxary
	bill.charge = form.cost
	bill.extra_charge = form.extra_cost
	bill.gst = form.gst
	bill.total = form.total
	bill.closed = True
	room.booked = False
	bill.save()
	room.save()
	return redirect('/bill/print/'+str(bill.id))

@bill_blueprint.route('/bill/custom', methods=['GET'])
@login_required
def get_custom_bill():
	rooms = Room.query.all()
	room_detail = {room.room_no: room.rent for room in rooms}
	return render_template('custom_bill.html', room_detail=json.dumps(room_detail))

@bill_blueprint.route('/bill/custom', methods=['POST'])
@login_required
def custom_bill():
	if 'gst' not in request.form:
		request.form = request.form.to_dict()
		request.form.update({'gst':0})
	form = DictToObject(**request.form)

	if not form.room_no or not form.name:
		flash('Room number required.', 'custom_bill')
		return render_template('custom_bill.html', **request.form)

	room = Room.query.filter_by(room_no=form.room_no).first()
	if not room:
		room = Room(room_no=form.room_no, created_by=current_user.id)
		room.save()

	customer = Customer(name=form.name, count=form.no_of_person, 
		address1=form.address1, address2=form.address2, state=form.state,
		country=form.country, zip_code=form.zip, contact_no=form.contact_number, 
		created_by=current_user.id)
	customer.save()

	in_time = datetime.strptime(form.in_time, '%Y-%m-%dT%H:%M')
	out_time = datetime.strptime(form.out_time, '%Y-%m-%dT%H:%M')

	bill = Bill(room_id=room.id, customer_id=customer.id, in_time=in_time, 
		out_time=out_time, charge=form.cost, extra_charge=form.extra_cost, 
		gst=form.gst, total=form.total, closed=True, created_by=current_user.id,
		advance=form.advance, miscellaneous=form.miscellaneous, luxary=form.luxary,)
	bill.save()
	return redirect('/bill/print/'+str(bill.id))


@bill_blueprint.route('/bill/print/<int:id>')
@login_required
def print_bill(id):
	bill = Bill.query.filter_by(id=id).first()
	data = DictToObject(**all_bill_data(bill))
	return render_template('print_bill.html', data=data)

@bill_blueprint.route('/bill/printn/<int:id>')
@login_required
def new_print_bill(id):
	bill = Bill.query.filter_by(id=id).first()
	data = DictToObject(**all_bill_data(bill))
	return render_template('new_print.html', data=data, curent_time=datetime.now().strftime("%d %B, %Y %H:%M%p"))

@bill_blueprint.route('/lodge_data.csv')
def download_data():
	csv_columns = ['id','room_id','room_no','customer_id','name','no_of_person','address1',
	'address2','city','state','country','zip','contact_number','in_time','out_time','advance','cost',
	'miscellaneous','luxary','extra_cost','gst','total']
	with open(app.config['DATA_FILE'], 'w') as f:
		writer = csv.DictWriter(f, fieldnames=csv_columns)
		writer.writeheader()
		for bill in Bill.query:
			writer.writerow(all_bill_data(bill))
	return send_file(app.config['DATA_FILE'], attachment_filename='data.csv', cache_timeout=0)
