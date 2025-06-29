# sockets/single_image.py

from flask import request
from .user_map import user_sid_map
from extensions import db
from models import Message
from datetime import datetime

def register_single_image(socketio):
    @socketio.on('single_image')
    def handle_single_image(data):
        """
        data: {
            from: user_id,
            to: user_id,
            image: base64字符串,
            filename: "xxx.png",
            msg_type: 'image',
            send_time: 时间戳或字符串,
            extra: {width, height, ...} # 可选
        }
        """
        # 1. 这里不存图片内容，只存图片信息
        msg = Message(
            sender_id=data['from'],
            receiver_id=data['to'],
            group_id=None,
            msg_type='image',
            content='[图片]',  # 或 data['filename']
            send_time=datetime.fromtimestamp(data['send_time']/1000) if isinstance(data['send_time'], (int, float)) else datetime.utcnow(),
            status='sent',
            extra={
                'filename': data.get('filename'),
                'width': data.get('extra', {}).get('width'),
                'height': data.get('extra', {}).get('height'),
                # 你还可以预留 image_id: xxx
            }
        )
        db.session.add(msg)
        db.session.commit()
        data['id'] = msg.id

        # 3. 发送图片消息到目标用户
        to_user = str(data['to'])
        sid = user_sid_map.get(to_user)
        if sid:
            socketio.emit('single_image', data, room=sid)