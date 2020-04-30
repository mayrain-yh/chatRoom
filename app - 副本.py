
from os import abort
import random

from flask import Flask, render_template
from flask_socketio import SocketIO
from flask_socketio import send, emit
from flask import abort, Response

from flask import Flask, jsonify
from flask import make_response
from flask import request

from datetime import datetime
import global_var_model as gl
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, Table, func
from sqlalchemy.orm import relationship
from flask_cors import CORS
import os

app = Flask(__name__, static_folder='dist')
CORS(app, resources=r'/*')

DIALECT = 'mysql'
DRIVER = 'pymysql'
USERNAME = 'user1'
PASSWORD ='123'

HOST = '127.0.0.1'
PORT ='3306'
DATABASE = 'api'

SQLALCHEMY_DATABASE_URI = "{}+{}://{}:{}@{}:{}/{}?charset=utf8".format(DIALECT, DRIVER, USERNAME, PASSWORD, HOST, PORT, DATABASE)
#'mysql+pymysql://user1:123@127.0.0.1:3306/api?charset=utf8'


app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


name_space = '/test'
db = SQLAlchemy(app)#创建

# # 请求的时候直接用回前端这边的域名http://localhost:9099，这就不会跨域，然后Nginx监听到凡是localhost:9099/api这个样子的，都转发到真正的服务端地址http://localhost:9871
# fetch('http://localhost:9099/api/iframePost', {
#   method: 'POST',
#   headers: {
#     'Accept': 'application/json',
#     'Content-Type': 'application/json'
#   },
#   body: JSON.stringify({
#     msg: 'helloIframePost'
#   })
# })



room_user = Table(
    "room_user",
    db.metadata,
    db.Column("room_id", db.Integer, ForeignKey("room.id"), primary_key=True),
    db.Column("user_id", db.Integer, ForeignKey("user.id"), primary_key=True)
)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, AUTO_INCREMENT=True)
    uName = db.Column(db.String(50))
    uPhone = db.Column(db.String(11))
    uEmail = db.Column(db.String(50))
    uAvatar = db.Column(db.String(1000))
    userId = db.Column(db.String(100))
    rooms = relationship("Room", backref="users", secondary=room_user)
    # def __repr__(self):
    #

class Room(db.Model):
    __tablename__ = 'room'
    id = db.Column(db.Integer, primary_key=True, AUTO_INCREMENT=True)
    gName = db.Column(db.String(50), nullable=False)
    gTopic = db.Column(db.String(100))
    gDescription = db.Column(db.String(100), nullable=False)
    gId = db.Column(db.Integer, nullable=False)
    photo = db.Column(db.String(1000))


#db.drop_all()
db.create_all()

#新建用户
@app.route('/chat/addUser',methods=['POST'])
def create_user():
    # print(request.json)
    # user1 = request.get_json()
    # uName=user1.get("uName")
    # uPhone=user1.get("uPhone")
    # uEmail=user1.get("uEmail")
    user = User()
    user.uName = 'undefined'
    user.uPhone = ''
    user.uEmail = ''
    resp = make_response("success")
    userId = random.randint(10000, 99999)
    resp.set_cookie('userId',str(userId), max_age=60*60*24*30)
    user.userId = userId
    db.session.add(user)
    db.session.commit()
    return resp

#修改用户信息  //未测试
#POST
@app.route('/chat/changeUser',methods=['POST'])
def update_user():
    user1 = request.get_json()
    print(user1)
    userId = request.cookies.get('userId')
    user_uName = user1.get('uName')
    user_uPhone = user1.get('uPhone')
    user_uEmail = user1.get('uEmail')
    a1 = User.query.filter(User.userId == userId).first()
    if not a1:
        abort(404)
    if len(user_uName) >0:
        a1.uName = user_uName
    if len(user_uPhone) >0:
        a1.uPhone = user_uPhone
    if len(user_uEmail) >0:
        a1.uEmail = user_uEmail
    db.session.commit()
    return jsonify({'status':'ok'})

#修改用户头像  //未测试
#POST
@app.route('/chat/changeAvatar',methods=['POST'])
def update_avatar():
    userId = request.cookies.get('userId')
    image_file = request.files.get("avatar")
    print(image_file)
    a1 = User.query.filter(User.userId == userId).first()
    if not a1:
        abort(404)
    if image_file != '':
        base_url = os.path.dirname(os.path.dirname(__file__))
        image_name = image_file.filename
        total_url = os.path.join(base_url, 'thefifith\dist\image', image_name)
        # url = os.path.join('img', image_name)
        url = image_name
        a1.uAvatar = url
        print(url)
        image_file.save(total_url)
    db.session.commit()
    return jsonify({'avatarName': url})


#删除用户
@app.route('/chat/deleteUser',methods=['DELETE'])
def delete_user():
    if not request.args:
        print('##1')
        abort(400)
    if 'id' in request.args:
        user_id = request.args['id']
        a1 = User.query.filter(User.id == user_id).all()
    else:
        print('参数错误')
    if not a1:
        print('没有该任务')
        abort(404)
    for i in a1:
        db.session.delete(i)

    db.session.commit()
    return jsonify({'status':'ok'})

#获取用户信息
@app.route('/chat/getUser',methods=['GET'])
def getUser():
    # resp = make_response("success")
    userId = request.cookies.get('userId')
    # print(userId)
    a1 = User.query.filter(User.userId == userId).first()
    print(a1.uName)
    if not a1:
        print('nonono')
    return jsonify({
        'uName': a1.uName,
        'uEmail': a1.uEmail,
        'uPhone': a1.uPhone,
        'avatarName': a1.uAvatar
    })


#获取群信息
@app.route('/chat/getRoom/<id>', methods=['GET'])
def get_room(id):
    # print(request.json)
    # if not request.json:
    #     print('##1')
    #     abort(400)
    # room1 = request.get_json()
    room_id = id
    a1 = Room.query.filter(Room.id == room_id).first()
    b1 =User.query.filter(User.id == a1.gId).first()
    # print(b1.userId)
    # print(a1.gId)
    if not a1:
        abort(404)
    return jsonify({
        'gName': a1.gName,
        'gTopic': a1.gTopic,
        'gDescription': a1.gDescription,
        'userId': b1.userId
    })

#新建群
@app.route('/chat/createGroup',methods=['GET','POST'])
def create_group():
    user_info = request.form.to_dict()
    userId = request.cookies.get('userId')
    a1 = User.query.filter(User.userId == userId).first()
    gId = a1.id
    gName = user_info.get('gName')
    gTopic = user_info.get('gTopic')
    gDescription = user_info.get('gDescription')
    # image_file = request.files.get("photo")
    #
    # print(request.json)
    # room1 = request.get_json()
    # gName = room1.get("gName")
    # gTopic = room1.get("gTopic")
    # gDescription = room1.get("gDescription")
    # image_file = request.files.get("photo")
    # name = Room.query.filter_by(gName=gName).first()
    # if name is not None:
    #     return jsonify({'status':'error'})
    room = Room()
    room.gId = gId
    room.gName = gName
    room.gTopic = gTopic
    room.gDescription = gDescription
    # base_url = os.path.dirname(os.path.dirname(__file__))
    # image_name = image_file.filename
    # total_url = os.path.join(base_url, 'thefifith\dist\img', image_name)
    # url = image_name
    # room.photo = url
    # image_file.save(total_url)
    db.session.add(room)
    db.session.commit()
    b1 = Room.query.filter(Room.gName == gName).first()
    if not b1:
        return jsonify({'status': 'notfound'})
    a = b1.id
    return jsonify({'roomId': a}),201


#修改群信息
@app.route('/chat/updateRoom/<id>',methods=['POST'])
def update_room(id):
    if not request.json:
        print('##1')
        abort(400)
    room1 = request.get_json()
    gName = room1.get("gName")
    gTopic = room1.get("gTopic")
    gDescription = room1.get("gDescription")
    image_file = request.files.get("photo")
    print(image_file)
    a1 = Room.query.filter(Room.id == id).first()
    if not a1:
        abort(404)
    if len(gName) >0:
        a1.gName = gName
    if len(gTopic) >0:
        a1.gTopic = gTopic
    if len(gDescription) >0:
        a1.gDescription = gDescription
    if image_file != '':
        base_url = os.path.dirname(os.path.dirname(__file__))
        image_name = image_file.filename
        total_url = os.path.join(base_url, 'thefifith\dist\image', image_name)
        url = image_name
        a1.photo = url
        image_file.save(total_url)

    db.session.commit()
    return jsonify({'status': 'ok'})

#修改群头像
@app.route('/chat/updateRoom_photo/<id>',methods=['POST'])
def update_room_photo(id):
    image_file = request.files.get("photo")
    print(image_file)
    a1 = Room.query.filter(Room.id == id).first()
    if not a1:
        abort(404)
    if image_file != '':
        base_url = os.path.dirname(os.path.dirname(__file__))
        image_name = image_file.filename
        total_url = os.path.join(base_url, 'thefifith\dist\image', image_name)
        url = image_name
        a1.photo = url
        image_file.save(total_url)
    db.session.commit()
    return jsonify({'avatarName': url})

#删除房间
@app.route('/chat/deleteRoom/<id>',methods=['DELETE'])
def delete_room(id):
    # if not request.args:
    #     print('##1')
    #     abort(400)
    # userId = request.cookies.get('userId')
    # a1 = User.query.filter(User.userId == userId).first()
    userid = 1
    a1 = User.query.filter(User.id == userid).first()
    if not a1:
        abort(404)
    roomid = id
    b1 = Room.query.filter(Room.id == roomid).first()
    if not b1:
        abort(404)
    if b1.gId == a1.id:
        db.session.delete(b1)
    # b1.users.clear()
    # db.session.add(b1)
    db.session.commit()
    return jsonify({'status':'ok'})


#加入群
@app.route('/chat/addRoom/<id>',methods=['POST'])
def addRoom(id):
    userId = request.cookies.get('userId')
    a1 = User.query.filter(User.userId == userId).first()
    if not a1:
        abort(404)
    roomid = id
    print(id)
    print(userId)
    b1 = Room.query.filter(Room.id == roomid).first()
    if not b1:
        abort(404)
    b1.users.append(a1)
    db.session.add(b1)
    db.session.commit()
    return jsonify({'status': 'ok'}), 201

#计算群人数  //不清楚是否要用
@app.route('/chat/countMates',methods=['GET'])
def countMates():
    print(request.json)
    if not request.json:
        abort(400)
    get_infor = request.get_json()
    roomid = get_infor.get("roomid")
    b1 = Room.query.filter(Room.id == roomid).first()
    if not b1:
        abort(404)
    result = room_user.query(func.count(room_user.room_id == roomid)).first()
    print(result)
    return jsonify({'status':'ok'})
#result = session.query(func.count(Article.id)).first()


#退出群
@app.route('/chat/outRoom/<id>',methods=['POST'])
def outRoom():
    userId = request.cookies.get('userId')
    a1 = User.query.filter(User.userId == userId).first()
    if not a1:
        abort(404)
    roomid = id
    b1 = Room.query.filter(Room.id == roomid).first()
    if not b1:
        abort(404)
    obj = room_user.query().filter(room_user.room_id == roomid and room_user.user_id == a1.id).first()
    print(obj)
    db.session.delete(obj)
    db.session.commit()
    return jsonify({'status':'ok'})



# socketio.on('connect')
# def login(socket):
#     gl.online_num += 1
#     print('Num:' + gl.online_num)
# socketio.on('disconnect')
# def logout(socket):
#     gl.online_num -= 1
#
# socketio.on('user')
# def user():
#     print('Num:' + gl.online_num)
#     send(gl.online_num, broadcast=True)

socketio.on('message')
def handleMessage(msg):
    print('Message:'+msg)
    send(msg, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='127.0.0.1', port=9000, debug=True)
    #app.run(debug=True)





