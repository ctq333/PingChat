from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Message, GroupMember, GroupChat, User
from sqlalchemy import or_, and_, desc, func

bp = Blueprint('message', __name__, url_prefix='/api/message')

@bp.route('/session_list', methods=['GET'])
@jwt_required()
def get_session_list():
    user_id = get_jwt_identity()

    # ---- 1. 私聊会话 ----
    # 查询与当前用户有关的所有私聊消息（group_id is NULL）
    private_msgs = (
        db.session.query(
            func.if_(
                Message.sender_id == user_id,
                Message.receiver_id,
                Message.sender_id
            ).label('other_id'),
            func.max(Message.send_time).label('last_time')
        )
        .filter(
            or_(
                Message.sender_id == user_id,
                Message.receiver_id == user_id
            ),
            Message.group_id == None
        )
        .group_by('other_id')
        .subquery()
    )

    private_last_msgs = (
        db.session.query(Message)
        .join(
            private_msgs,
            and_(
                func.if_(
                    Message.sender_id == user_id,
                    Message.receiver_id,
                    Message.sender_id
                ) == private_msgs.c.other_id,
                Message.send_time == private_msgs.c.last_time
            )
        )
        .all()
    )

    # ---- 2. 群聊会话 ----
    # 当前用户加入的群
    user_groups = db.session.query(GroupMember.group_id).filter_by(user_id=user_id)
    group_msgs = (
        db.session.query(
            Message.group_id,
            func.max(Message.send_time).label('last_time')
        )
        .filter(Message.group_id.in_(user_groups))
        .group_by(Message.group_id)
        .subquery()
    )
    group_last_msgs = (
        db.session.query(Message)
        .join(
            group_msgs,
            and_(
                Message.group_id == group_msgs.c.group_id,
                Message.send_time == group_msgs.c.last_time
            )
        )
        .all()
    )

    # ---- 3. 合并会话 ----
    sessions = []
    # 私聊
    for msg in private_last_msgs:
        other_id = msg.receiver_id if msg.sender_id == user_id else msg.sender_id
        user = User.query.get(other_id)
        sessions.append({
            "type": "private",
            "id": other_id,
            "nickname": user.username,
            "avatar": getattr(user, 'avatar_url', ''),
            "last_message": msg.content,
            "msg_type": msg.msg_type,
            "send_time": msg.send_time.isoformat()
        })

    # 群聊
    for msg in group_last_msgs:
        group = GroupChat.query.get(msg.group_id)
        sessions.append({
            "type": "group",
            "id": group.id,
            "nickname": group.name,
            "avatar": group.avatar_url,
            "last_message": msg.content,
            "msg_type": msg.msg_type,
            "send_time": msg.send_time.isoformat()
        })

    # 按最后通讯时间倒序排列
    sessions.sort(key=lambda x: x['send_time'], reverse=True)

    return jsonify({"code": 200, "data": sessions})

@bp.route('/list', methods=['GET'])
def get_message_list():
    user_id = request.args.get('user_id', type=int)
    group_id = request.args.get('group_id', type=int)
    keyword = request.args.get('keyword', type=str)
    time_range = request.args.get('timeRange', type=str)
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)

    query = Message.query
    
    # 筛选条件
    if user_id:
        query = query.filter(or_(Message.sender_id == user_id, Message.receiver_id == user_id))
    if group_id:
        query = query.filter(Message.group_id == group_id)
    if keyword:
        query = query.filter(Message.content.like(f"%{keyword}%"))
    
    # 时间范围筛选
    if time_range:
        from datetime import datetime, timedelta
        now = datetime.now()
        if time_range == '1h':
            start_time = now - timedelta(hours=1)
        elif time_range == '24h':
            start_time = now - timedelta(days=1)
        elif time_range == '7d':
            start_time = now - timedelta(days=7)
        elif time_range == '30d':
            start_time = now - timedelta(days=30)
        else:
            start_time = None
        
        if start_time:
            query = query.filter(Message.send_time >= start_time)

    total = query.count()
    messages = query.order_by(Message.send_time.desc()).offset((page-1)*page_size).limit(page_size).all()

    result = []
    for m in messages:
        sender = User.query.get(m.sender_id)
        receiver = User.query.get(m.receiver_id) if m.receiver_id else None
        group = GroupChat.query.get(m.group_id) if m.group_id else None
        
        result.append({
            'id': m.id,
            'sender_id': m.sender_id,
            'sender_username': sender.username if sender else '',
            'sender_nickname': sender.nickname if sender else '',
            'sender_avatar': sender.avatar_url if sender else '',
            'receiver_id': m.receiver_id,
            'receiver_username': receiver.username if receiver else '',
            'receiver_nickname': receiver.nickname if receiver else '',
            'group_id': m.group_id,
            'group_name': group.name if group else '',
            'msg_type': m.msg_type,
            'content': m.content,
            'created_at': m.send_time.isoformat() if m.send_time else '',
        })
    
    return jsonify({
        'code': 200, 
        'data': {
            'messages': result,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        }
    })