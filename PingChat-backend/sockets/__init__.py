# sockets/__init__.py

from .user_map import user_sid_map, sid_user_map

def register_chat_events(socketio):
    from flask import request
    from .single_text import register_single_text
    # ...你可以在此注册其它事件...

    @socketio.on('connect')
    def handle_connect():
        user_id = request.args.get('user_id')
        sid = request.sid
        if user_id:
            user_sid_map[str(user_id)] = sid
            sid_user_map[sid] = str(user_id)
            print(f'[Socket] 用户{user_id} 已连接 sid={sid}')

    @socketio.on('disconnect')
    def handle_disconnect():
        sid = request.sid
        user_id = sid_user_map.pop(sid, None)
        if user_id:
            user_sid_map.pop(user_id, None)
            print(f'[Socket] 用户{user_id} 已断开 sid={sid}')

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