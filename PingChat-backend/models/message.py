from extensions import db
from sqlalchemy.dialects.mysql import JSON as MySQLJSON
from sqlalchemy.sql import func

class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    sender_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False, index=True)
    receiver_id = db.Column(db.BigInteger, index=True)
    group_id = db.Column(db.BigInteger, index=True)
    msg_type = db.Column(db.String(20), nullable=False)
    content = db.Column(db.Text)
    send_time = db.Column(db.DateTime, nullable=False)
    delivered_time = db.Column(db.DateTime)
    read_time = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='sent')
    extra = db.Column(MySQLJSON)