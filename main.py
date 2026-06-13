from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import SocketIO, send, join_room, leave_room, emit
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = "OjasOP"

rooms = {}#{room:user}
def generate_room():
    x = 0
    while True:
        x = random.randrange(1000, 9999)
        if x not in rooms:
            break
    x = str(x)
    return x
socketio = SocketIO(app, cors_allowed_origins="*")

def check_room(room):
    for i in rooms.keys():
        if room == i:
            return True
        else:
            pass
    return False



@app.route('/', methods = ['POST', 'GET'])
def home():
    session.clear()
    if request.method == "POST":
        name = request.form.get("name")
        code = request.form.get("code")
        join = request.form.get("join", False)
        create = request.form.get("create", False)


        if not name:
            return render_template('main.html', error = "Pls enter a name.", code=code, name=name) 
        if join != False and not code:
            return render_template('main.html', error = "Pls enter a code to join.", code=code, name=name) 
        
        room = code
        if create != False:
            room = generate_room()
            rooms[room] = 0
        elif join != False and room not in list(rooms.keys()):
            return render_template('main.html', error = "Invalid Room" , code=code, name=name)

        print(list(rooms.keys()), room)

        session['room'] = room
        session['name'] = name
        return redirect(url_for("chat_room"))

    return render_template('main.html') 



@app.route("/room")
def chat_room():
    room = session.get("room")
    if room is None or session.get("name") is None or room not in list(rooms.keys()):
        return redirect(url_for("home"))
    
    return render_template('room.html', code=room, rooms=rooms)

@socketio.on('message')
def message(data):
    room = session.get("room")
    if room not in list(rooms.keys()):
        return
    content = {
        "name": session.get("name"),
        "message": data["data"]
    }
    emit("message", content, room=room)

@socketio.on('connect')
def connect(auth):
    room = session.get("room")
    name = session.get("name")

    print(room, name)
    if not room and not name:
        return
    if room not in rooms:
        leave_room(room)
        return
    
    join_room(room)
    emit(
    "message",
    {
        "name": name,
        "message": "Has entered the room"
    },
    room=room
    )
    rooms[room] += 1
    socketio.emit(
        "update_count",
        {"count": rooms[room]}
    )



@socketio.on('disconnect')
def disconnect(auth):
    room = session.get("room")
    name = session.get("name")


    leave_room(room)
    if room in rooms:
         rooms[room] -= 1
         if rooms[room] == 0:
             del rooms[room]
    socketio.emit(
        "update_count",
        {"count": rooms[room]}
    )
    emit(
    "message",
    {
        "name": name,
        "message": "Has left the room"
    },
    room=room
    )
    print(f'{name} left the room, {room}')
if __name__ == '__main__':
    socketio.run(app)
