from flask import Flask, render_template, request, redirect, session
import time
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit, join_room, leave_room, send, close_room
from python.sockets import socketio
from python.models import User, Room, Problem, Comment, db
# from uuid import uuid4
# import gevent


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
app.config["SECRET_KEY"] = "yeet"
socketio.init_app(app)
db.init_app(app)

with app.app_context():
	db.create_all()

with app.app_context():
	room = Room.query.filter_by(number=1).first()
	if room is None:
		room = Room(number=1, users=[])
		teacher = User(name="GRT", room_id=room.number, is_teacher=True)
		room.users.append(teacher)
		room.teacher = teacher
		room.delay = 0
		room.maxOcc = 100
		room.showSolved = True
		db.session.add(room)
		db.session.add(teacher)
		db.session.commit()

@app.route('/')
def index():
	return render_template("index.html")
	# room = Room.query.filter_by(number=1).first()
	# if room is None:
	# 	room = Room(number=1, users=[])
	# 	user = User(name='teach', room_id=room.number, is_teacher=True)
	# 	room.users.append(user)
	# 	room.teacher = user
	# 	room.delay = 0 # .get() returns None if the item doesnt exsist, so no error. it was being weid idk why
	# 	room.maxOcc = 9999
	# 	room.showSolved = True # don't ask me why its off and not on, I don't know why
	# 	db.session.add(room)
	#
	# else:
	# 	user = User(name=str(uuid4()), room_id=room.number, is_teacher=False)
	# 	room.users.append(user)
	# 	db.session.add(room)
	# 	db.session.add(user)
	#
	# db.session.commit()
	#
	# session['user'] = user.id
	#
	# return redirect('/room/1')

@app.route('/room/<roomno>')
def room(roomno):
	user = User.query.filter_by(id=session.get("user")).first()
	if user is None:
		return redirect("/")
	elif str(user.room_id) == str(roomno):
		room = user.room.serialize
		room['users'].pop(-1)
		return render_template("room.html", roomno=roomno, user=user.serialize, room=room)
	return redirect("/")



@app.route('/delete/<roomno>')
def delete(roomno):
	user = User.query.filter_by(id=session.get("user")).first()
	if user is None:
		return redirect("/room/<roomno>")
	else:
		Room.query.filter_by(number=int(roomno)).delete()
		User.query.filter_by(room_id=int(roomno)).delete()
		db.session.commit()
		socketio.emit('update', {'type':'room_deleted'}, room=str(roomno))
		session['user'] = None
		socketio.close_room(str(roomno))

	return redirect("/")

@app.route('/join', methods=['GET', 'POST'])
def join():
	if request.method == 'GET':
		return render_template("join.html")

	elif request.method == 'POST':
		try:
			int(request.form['code'])
		except ValueError:
			return render_template("join.html", error="Invalid room number")

		room = Room.query.filter_by(number=int(request.form['code'])).first()
		if room is None:
			return render_template("join.html", error="Room Not Found")
		elif room.maxOcc <= len(room.users):
			return render_template("join.html", error="Room Full")

		room = Room.query.filter_by(number=int(request.form['code'])).first()
		user = User(name=request.form['name'], room_id=room.number, is_teacher=False)
		room.users.append(user)
		db.session.add(room)
		db.session.add(user)
		db.session.commit()

		session['user'] = user.id

		return redirect('/room/%s' % request.form["code"])

	return render_template("join.html")


@app.route('/create', methods=['GET','POST'])
def create():
	if request.method == 'GET':
		return render_template('settings.html')

	if request.method == 'POST':
		roomno = str(time.time()).replace(".", "")[-6:]
		room = Room.query.filter_by(number=roomno).first()
		while room is not None:
			roomno = str(time.time()).replace(".", "")[-6:]
			room = Room.query.filter_by(number=roomno).first()

		room = Room(number=roomno, users=[])
		teacher = User(name=request.form['name'], room_id=room.number, is_teacher=True)
		room.users.append(teacher)
		room.teacher = teacher
		room.delay = int(request.form.get('delay')) # .get() returns None if the item doesnt exsist, so no error. it was being weid idk why
		room.maxOcc = int(request.form.get('max'))
		room.showSolved = True if request.form.get('solved') == "off" else False # don't ask me why its off and not on, I don't know why
		db.session.add(room)
		db.session.add(teacher)
		db.session.commit()

		session["user"] = teacher.id

		return redirect('/room/%s' %roomno)


@app.route('/suggest', methods=['GET', 'POST'])
def joinSuggestionRoom():
	if request.method == 'GET':
		return render_template("suggest.html")

	elif request.method == 'POST':
		room = Room.query.filter_by(number=1).first()
		print(room.serialize)
		if room.maxOcc <= len(room.users):
			return render_template("suggest.html", error="We're receiving a lot of requests right now. Please try again later.")
		user = User(name=request.form['name'], room_id=room.number, is_teacher=False)
		room.users.append(user)
		db.session.add(room)
		db.session.add(user)
		db.session.commit()
		session['user'] = user.id

		return redirect('/room/1')

	return render_template("suggest.html")

if __name__ == '__main__':
	socketio.run(app)
