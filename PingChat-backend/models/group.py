from extensions import db
from sqlalchemy.sql import func

class GroupChat(db.Model):
    __tablename__ = 'groupchat'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128), nullable=False)
    owner_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    avatar_url = db.Column(db.String(256))
    notice = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )