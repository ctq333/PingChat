from flask import request
from extensions import socketio

user_sid_map = {}

def register_chat_events(socketio):

    @socketio.on('connect')
    def handle_connect():
        user_id = request.args.get('user_id')
        if user_id:
            user_sid_map[user_id] = request.sid
        print(f'User {user_id} connected, sid={request.sid}')

    @socketio.on('disconnect')
    def handle_disconnect():
        for uid, sid in list(user_sid_map.items()):
            if sid == request.sid:
                del user_sid_map[uid]
                print(f'User {uid} disconnected')
                break

    @socketio.on('send_message')
    def handle_send_message(data):
        # ...同前面一样，实现消息转发...
        pass

    @socketio.on('send_image')
    def handle_send_image(data):
        # ...同前面一样，实现图片消息端到端转发...
        pass