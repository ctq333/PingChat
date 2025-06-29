# sockets/single_text.py

from .user_map import user_sid_map
from extensions import db
from models import Message
from datetime import datetime

def register_single_text(socketio):
    @socketio.on('single_message')
    def handle_single_message(data):
        """
        data: {
            from: user_id,
            to: user_id,
            content: str,
            msg_type: 'text',
            send_time: 时间戳或字符串
        }
        """
        # 1. 入库（单聊文本消息）
        try:
            msg = Message(
                sender_id=data['from'],
                receiver_id=data['to'],
                group_id=None,
                msg_type='text',
                content=data['content'],
                send_time=datetime.fromtimestamp(data['send_time']/1000) if isinstance(data['send_time'], (int, float)) else datetime.utcnow(),
                status='sent'
            )
            print(f"[DB] 正在写入消息: {msg}")
            db.session.add(msg)
            db.session.commit()
            print(f"[DB] 消息写入成功 id={msg.id}")
            data['id'] = msg.id
        except Exception as e:
            db.session.rollback()
            print(f"[DB ERROR] 消息写入失败: {e}")
            return  # 此时不往下发消息


        # 2. 回传消息id给前端
        data['id'] = msg.id

        # 3. 发送给目标用户
        to_user = str(data['to'])
        sid = user_sid_map.get(to_user)
        if sid:
            socketio.emit('single_message', data, room=sid)


    