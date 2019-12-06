from flask import Flask, render_template, request, redirect, session
import time
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit, join_room, leave_room, send, close_room


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
app.config["SECRET_KEY"] = "yeet"
socketio = SocketIO(app)
db = SQLAlchemy(app)


class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, nullable=False)
    users = db.relationship('User', backref='room')
    teacher = db.relationship('User', uselist=False)

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
           'users': [ user.name for user in self.users]
       }


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    is_teacher = db.Column(db.Boolean, nullable=False)
    name = db.Column(db.String, nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.number'), nullable=False)

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

db.create_all()

@app.route('/')
def index():
    return render_template("index.html")

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
        socketio.emit('room_deleted', None, room=str(roomno))
        session['user'] = None
        socketio.close_room(str(roomno))

    return redirect("/")

@app.route('/join', methods=['GET', 'POST'])
def join():
    if request.method == 'GET':
        return render_template("join.html")

    elif request.method == 'POST':
        if request.form.get('code') and not request.form.get('name'):
            try:
                int(request.form['code'])
            except ValueError:
                return render_template("join.html", badcode=True)

            room = Room.query.filter_by(number=int(request.form['code'])).first()
            if room is None:
                return render_template("join.html", badcode=True)
            return render_template('name.html', code=request.form['code'])

        elif request.form.get('code') and request.form.get('name'):
            room = Room.query.filter_by(number=int(request.form['code'])).first()
            user = User(name=request.form['name'], room_id=room.number, is_teacher=False)
            room.users.append(user)
            db.session.add(room)
            db.session.add(user)
            db.session.commit()

            session['user'] = user.id

            return redirect(f'/room/{request.form["code"]}')

    return render_template("join.html")

@app.route('/create', methods=['GET','POST'])
def create():
    if request.method == 'GET':
        return render_template('name.html')

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
        db.session.add(room)
        db.session.add(teacher)
        db.session.commit()

        session["user"] = teacher.id

        return redirect(f'/room/{roomno}')

@socketio.on('leave')
def leave(json):
    User.query.filter_by(id=session['user']).delete()
    db.session.commit()
    session['user'] = None
    leave_room(json["room"])
    emit('disconnection', {"name":json["name"]}, room=json["room"])

@socketio.on('join')
def join(json):
    join_room(json["room"])
    emit('connection', {"name":json["name"]}, room=json["room"])

@socketio.on('message')
def new_message(json):
    emit('new_message', {"name":json["name"], "message":json["message"]}, room=json["room"])

if __name__ == '__main__':
    socketio.run(app)