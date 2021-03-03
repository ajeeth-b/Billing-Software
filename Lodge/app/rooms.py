from flask import Blueprint, render_template, redirect, request, flash
from .models import Room
from flask_login import login_required, current_user

room = Blueprint('rooms', __name__)

@room.route('/')
@login_required
def get_room():
	rooms = Room.query.order_by(Room.room_no).all()
	return render_template('room.html', rooms=rooms)

@room.route('/add_room', methods=['POST'])
@login_required
def add_room():
	if Room.query.filter_by(room_no=request.form['room_no']).first():
		flash('room number already taken', 'room-error')
		return redirect('/')
	new_room = Room(room_no=request.form['room_no'], created_by=current_user.id)
	new_room.save()
	return redirect('/')


@room.route('/room/delete/<int:id>', methods=['GET'])
@login_required
def delete_room(id):
	room = Room.query.filter_by(id=id).first()
	if not room:
		flash('No such room to delete', 'room-delete')
		return redirect('/')
	if room.booked:
		flash('Room '+str(room.room_no)+' is not empty, cannot delete', 'room-delete')
		return redirect('/')
	flash('Room '+str(room.room_no)+' successfully deleted', 'room-delete')
	room.delete()
	return redirect('/')
