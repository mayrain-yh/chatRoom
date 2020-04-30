from flask import Flask, render_template
from flask_socketio import SocketIO
from flask_socketio import send, emit
from flask import abort

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@socketio.on('message')
def handleMessage(msg):
    print('Message:'+msg)
    send(msg,broadcast=True)

if __name__ == '__main__':
    socketio.run(app)