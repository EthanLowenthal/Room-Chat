from flask_socketio import SocketIO, emit, join_room, leave_room, send, close_room
from flask import session

from models import db, User, Room, Comment, Problem

socketio = SocketIO()

@socketio.on('leave')
def leave(json):
	user = User.query.filter_by(id=int(session['user'])).first()
	# room = 	Room.query.filter_by(number=user.room_id).first()
	if user.is_teacher:
		Room.query.filter_by(number=user.room_id).delete()
		# db.session.delete(room)
	else:
		room = Room.query.filter_by(number=user.room_id).first()
		room.users.remove(user)
		db.session.add(room)

	User.query.filter_by(id=session['user']).delete()

	emit('update', {'type':'disconnection', "name": json["name"]}, room=json["room"])

	db.session.commit()
	session['user'] = None
	leave_room(json["room"])


@socketio.on('join')
def join(json):
	join_room(json["room"])
	emit('update', {'type':'connection', "name":json["name"]}, room=json["room"])

@socketio.on('problem_solved')
def problem_solved(json):
	problem = Problem.query.filter_by(id=json["id"]).first()
	problem.solved = True
	db.session.add(problem)
	db.session.commit()
	emit('update', {'type':'new_problem_solved', "id":json["id"]}, room=json["room"])

@socketio.on('problem_deleted')
def problem_solved(json):
	problem = Problem.query.filter_by(id=json["id"]).first()
	db.session.delete(problem)
	db.session.commit()
	emit('update', {'type':'new_problem_deleted', "id":json["id"]}, room=json["room"])

@socketio.on('problem')
def new_problem(json):
	user = User.query.filter_by(id=session['user']).first()
	room = Room.query.filter_by(number=user.room_id).first()

	problem = Problem(title=json["title"], sender=user, room=room, solved=False, message=json["message"])
	room.problems.append(problem)
	db.session.add(problem)
	db.session.add(room)
	db.session.commit()

	emit('update', {'type':'new_problem', "id":problem.id, "problem":problem.serialize}, room=json["room"])


@socketio.on('message')
def new_message(json):
	emit('update', {'type':'new_message', "name":json["name"], "message":json["message"]}, room=json["room"])

@socketio.on('comment')
def new_comment(json):
	problem = Problem.query.filter_by(id=json["problem"]).first()
	comment = Comment(message=json["message"])
	problem.comments.append(comment)
	db.session.add(comment)
	db.session.add(problem)
	db.session.commit()

	emit('update', {'type':'new_comment', "comment":comment.serialize, "problem":json["problem"]}, room=json["room"])
