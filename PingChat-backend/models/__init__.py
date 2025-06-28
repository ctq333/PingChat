from .user import User
from .message import Message
from .group import GroupChat
from .group_member import GroupMember
from .user_login_log import UserLoginLog
from .friend import Friend
from .message_receipt import MessageReceipt
from extensions import db

# 关系映射补充（可选，便于ORM查询）

# 用户: 发送的消息
User.sent_messages = db.relationship('Message', backref='sender', foreign_keys=[Message.sender_id], lazy='dynamic')

# 用户: 拥有的群
User.groups_owned = db.relationship('GroupChat', backref='owner', foreign_keys=[GroupChat.owner_id], lazy='dynamic')

# 用户: 群成员身份
User.group_memberships = db.relationship('GroupMember', backref='user', lazy='dynamic')

# 群: 群成员
GroupChat.members = db.relationship('GroupMember', backref='group', lazy='dynamic')

# 消息: 回执
Message.receipts = db.relationship('MessageReceipt', backref='message', lazy='dynamic')

# 用户: 登录日志
User.login_logs = db.relationship('UserLoginLog', backref='user', lazy='dynamic')

# 用户: 好友
User.friends = db.relationship('Friend', foreign_keys=[Friend.user_id], backref='user', lazy='dynamic')
User.friend_of = db.relationship('Friend', foreign_keys=[Friend.friend_id], backref='friend', lazy='dynamic')

# 用户: 消息回执
User.message_receipts = db.relationship('MessageReceipt', backref='user', lazy='dynamic')