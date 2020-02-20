# Room-Chat
a tool for making student/teacher chat rooms

### Dependancies
(install with pip)

`flask`
`flask-sqlalchemy`
`flask-socketio`
`gunicorn`
`gevent`

### To Run:
Deploy: `gunicorn -k gevent -w 1 main:app`
Develop: `python main.py`
