from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	is_teacher = db.Column(db.Boolean)
	name = db.Column(db.String, nullable=True)
	room_id = db.Column(db.Integer, db.ForeignKey('room.number'))

	def __init__(self, name, room_id, is_teacher=False):
		self.name = name
		self.room_id = room_id
		self.is_teacher = is_teacher

	@property
	def serialize(self):
		return {
			'id': self.id,
			'name' : self.name,
			'is_teacher': self.is_teacher,
		}

class Comment(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	message = db.Column(db.String)
	problem_id = db.Column(db.Integer, db.ForeignKey('problem.id'))
	@property
	def serialize(self):
	   return {
		   'id': self.id,
		   'message': self.message
	   }


class Problem(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String)
	message = db.Column(db.String)
	sender = db.relationship(User)
	sender_id = db.Column(db.ForeignKey(User.id))
	comments = db.relationship(Comment, backref='problem')
	solved = db.Column(db.Boolean)
	room_id = db.Column(db.ForeignKey('room.number'))

	@property
	def serialize(self):
		if self.sender is None: # sender is deleted
			sender = {"id":9999, "name":"[Deleted]", "is_teacher":False}
		else:
			sender = self.sender.serialize

		return {
			'id': self.id,
			'sender': sender,
			'sender_id': sender["id"],
			'solved': self.solved,
			'message': self.message,
			'title': self.title,
			'comments': [comment.serialize for comment in self.comments]
		}


class Room(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	number = db.Column(db.Integer)
	users = db.relationship(User, backref='room')
	problems = db.relationship(Problem, backref='room')
	teacher = db.relationship(User, uselist=False)
	delay = db.Column(db.Integer)
	maxOcc = db.Column(db.Integer)
	showSolved = db.Column(db.Boolean)

	def __init__(self, number, users=[], teacher=None):
		self.number = number
		self.teacher = teacher
		self.users = users

	@property
	def serialize(self):
	   return {
		   'id': self.id,
		   'number': self.number,
		   'teacher': self.teacher.name,
		   'users': [ user.name for user in self.users],
		   'problems': [problem.serialize for problem in self.problems],
		   'showSolved': self.showSolved,
	   }