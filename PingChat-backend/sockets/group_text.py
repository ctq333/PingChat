# sockets/group_text.py
from .user_map import user_sid_map
from extensions import db
from models import Message, GroupMember
from datetime import datetime

def get_group_user_ids(group_id):
    # 查询群成员 user_id，返回 list
    return [m.user_id for m in GroupMember.query.filter_by(group_id=group_id).all()]

def register_group_text(socketio):
    @socketio.on('group_message')
    def handle_group_message(data):
        """
        data: {
            from: user_id,
            group_id: int,
            content: str,
            msg_type: 'text',
            send_time: 时间戳,
            sender_name: str  # 新增
        }
        """
        # 入库
        msg = Message(
            sender_id=data['from'],
            receiver_id=None,
            group_id=data['group_id'],
            msg_type='text',
            content=data['content'],
            send_time=datetime.fromtimestamp(data['send_time']/1000) if isinstance(data['send_time'], (int, float)) else datetime.utcnow(),
            status='sent',
            # 可以冗余存一份 sender_name 到 extra 字段
            extra={'sender_name': data.get('sender_name', '')}
        )
        db.session.add(msg)
        db.session.commit()
        data['id'] = msg.id

        # 群发
        group_id = data['group_id']
        from_user = int(data['from'])
        user_ids = get_group_user_ids(group_id)
        for uid in user_ids:
            uid = int(uid)
            if uid != from_user:
                sid = user_sid_map.get(uid)
                if sid:
                    socketio.emit('group_message', data, room=sid)

    