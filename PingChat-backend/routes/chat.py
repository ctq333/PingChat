from flask import Blueprint, request, jsonify
from models import User, Message, GroupChat, GroupMember
from extensions import db
from sqlalchemy import or_, and_

bp = Blueprint('chat', __name__)


# 单聊历史
@bp.route('/history', methods=['GET'])
def get_history():
    user_id = request.args.get('user_id', type=int)
    peer_id = request.args.get('peer_id', type=int)
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 30, type=int)

    if not user_id or not peer_id:
        return jsonify({'code': 400, 'message': '参数缺失'}), 400

    query = Message.query.filter(
        or_(
            and_(Message.sender_id == user_id, Message.receiver_id == peer_id),
            and_(Message.sender_id == peer_id, Message.receiver_id == user_id)
        )
    ).order_by(Message.send_time.asc())

    total = query.count()
    messages = query.offset((page-1)*page_size).limit(page_size).all()

    def msg_to_dict(msg):
        sender = User.query.get(msg.sender_id)
        return {
            'id': msg.id,
            'sender_id': msg.sender_id,
            'sender_name': sender.nickname or sender.username if sender else '未知',
            'msg_type': msg.msg_type,
            'content': msg.content,
            'send_time': msg.send_time.strftime("%Y-%m-%dT%H:%M:%S"),
            'avatar_url': sender.avatar_url if sender else '',
        }

    return jsonify({
        'code': 200,
        'message': 'OK',
        'data': {
            'messages': [msg_to_dict(m) for m in messages],
            'total': total
        }
    })

# 群聊历史
@bp.route('/group_history', methods=['GET'])
def get_group_history():
    group_id = request.args.get('group_id', type=int)
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 30, type=int)

    if not group_id:
        return jsonify({'code': 400, 'message': '参数缺失'}), 400

    query = Message.query.filter(
        Message.group_id == group_id
    ).order_by(Message.send_time.asc())

    total = query.count()
    messages = query.offset((page-1)*page_size).limit(page_size).all()

    def msg_to_dict(msg):
        sender = User.query.get(msg.sender_id)
        return {
            'id': msg.id,
            'sender_id': msg.sender_id,
            'sender_name': sender.nickname or sender.username if sender else '未知',
            'msg_type': msg.msg_type,
            'content': msg.content,
            'send_time': msg.send_time.strftime("%Y-%m-%dT%H:%M:%S"),
            'avatar_url': sender.avatar_url if sender else '',
        }

    return jsonify({
        'code': 200,
        'message': 'OK',
        'data': {
            'messages': [msg_to_dict(m) for m in messages],
            'total': total
        }
    })

@bp.route('/session_list', methods=['GET'])
def session_list():
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({'code': 400, 'message': '缺少user_id'}), 400

    result = []

    # ---- 单聊会话：所有其他用户 ----
    all_users = User.query.filter(User.id != user_id).all()
    for peer in all_users:
        msg = Message.query.filter(
            ((Message.sender_id == user_id) & (Message.receiver_id == peer.id)) |
            ((Message.sender_id == peer.id) & (Message.receiver_id == user_id)),
            Message.group_id == None
        ).order_by(Message.send_time.desc()).first()
        result.append({
            "id": peer.id,
            "name": peer.nickname or peer.username,
            "type": "user",
            "avatar_url": peer.avatar_url or "",
            "last_msg_time": msg.send_time.strftime("%Y-%m-%dT%H:%M:%S") if msg else "",
            "last_msg": msg.content if msg else ""
        })

    # ---- 群聊会话：所有已加入群 ----
    groups = db.session.query(GroupChat).join(GroupMember).filter(GroupMember.user_id == user_id).all()
    for group in groups:
        last_msg = Message.query.filter(Message.group_id == group.id).order_by(Message.send_time.desc()).first()
        result.append({
            "id": group.id,
            "name": group.name,
            "type": "group",
            "avatar_url": group.avatar_url or "",
            "last_msg_time": last_msg.send_time.strftime("%Y-%m-%dT%H:%M:%S") if last_msg else "",
            "last_msg": last_msg.content if last_msg else ""
        })

    # 按时间排序，无消息的排最后
    def msg_time_key(item):
        return item.get("last_msg_time") or ""
    result.sort(key=msg_time_key, reverse=True)

    return jsonify({"code": 200, "data": result})