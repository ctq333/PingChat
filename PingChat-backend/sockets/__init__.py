# sockets/__init__.py

from .user_map import user_sid_map, sid_user_map
from extensions import socketio
from flask import request
from datetime import datetime

@socketio.on('connect')
def handle_connect():
    user_id = str(request.args.get('user_id'))
    if user_id is not None:
        user_id = int(user_id)
        sid = request.sid
        user_sid_map[user_id] = sid
        sid_user_map[sid] = user_id
    print(f"user_sid_map add: {user_id} ({type(user_id)}) => {sid}")
    print(f"[SOCKETIO] 用户 {user_id} 连接成功，socket id: {sid}")

@socketio.on('disconnect')
def handle_disconnect():
    sid = request.sid
    user_id = sid_user_map.pop(sid, None)
    if user_id:
        user_sid_map.pop(user_id, None)

def register_chat_events(socketio):
    from flask import request
    from .single_text import register_single_text
    # ...你可以在此注册其它事件...

    # 注册每个功能事件
    from .single_text import register_single_text
    from .single_image import register_single_image
    from .group_text import register_group_text
    from .group_image import register_group_image
    from .admin import register_admin

    register_single_text(socketio)
    register_single_image(socketio)
    register_group_text(socketio)
    register_group_image(socketio)
    register_admin(socketio)